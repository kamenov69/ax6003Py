#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 13:09:35 2025

Python driver for the power supply 
Manufacturer: AXIO MET
Model: ax6003P
1 output, USB interface

Absolute maximum ratings:
    V_max = 60 V
    I_max = 3 A

@author: kamen
"""

from tools import print_my_ip, search_by_manufacturer, serial_ports_list
import scpy

# USB device name in Linux environment
mnfact_linux = 'Prolific Technology Inc'


class Ax6003Py(scpy.Scpy):
    """Python driver for a single-channel power supply unit:
       Manufacturer: AXIO MET
       Model: ax6003P
       Interface: 1 output, USB connection

       Absolute maximum ratings:
           V_max = 60 V
           I_max = 3 A

       Inherits from: Scpy
       Communication: Serial protocol using SCPI.
       Implements the *FNCK command common to all SCPI devices.
       Inherits methods such as reset(), in_number(), status(), etc.
    """

    def __init__(self, **kargs):
        """Initializes the serial connection with given arguments.

        Parameters
        ----------
        port : str
            Serial device name (e.g., '/dev/ttyUSB0' or 'COM3')
        baudrate : int
            Serial baud rate (e.g., 9600)

        Returns
        -------
        None
        """
        super().__init__(**kargs)
        self.string_rep = f"Connected on {kargs} \n\n"
        self.timeout = 1
        _ = self.read_all()  # Clear the initial buffer
        
        # Optionally reset the device and set the response time to minimum (1 s)
        # self.reset()
        # self.delay_time(1)

    def apply_voltage(self, volts=None):
        """Set or get the output voltage.

        Parameters
        ----------
        volts : float, optional
            Voltage to apply [V], min 0.01, max 60 V

        Returns
        -------
        float
            Currently applied voltage [V]
        """
        if volts is not None:
            self.write_line(':VOLT', volts)
        return self.command('APPL?')[0]

    def apply_current(self, ampers=None):
        """Set or get the output current.

        Parameters
        ----------
        ampers : float, optional
            Current to apply [A], 0.0001, max 3 A

        Returns
        -------
        float
            Currently applied current [A]
        """
        if ampers is not None:
            self.write_line(':CURR', ampers)
        return self.command('APPL?')[1]

    def apply(self, volts=None, ampers=None):
        """Set or get the output voltage and current.

        Parameters
        ----------
        volts : float, optional
            Voltage to apply [V], min 0.001, max 60 V
        ampers : float, optional
            Current to apply [A], min 0.0001, max 3 A

        Returns
        -------
        tuple (float, float)
            Currently applied voltage [V] and current [A]
        """
        if volts and ampers:
            self.write_line(':APPL', volts, ampers)
        return self.command('APPL?')

    def measure_voltage(self):
        """Measure and return the real-time output voltage.

        Returns
        -------
        float
            Measured voltage [V]
        """
        return self.command(':MEAS:VOLT?')

    def measure_current(self):
        """Measure and return the real-time output current.

        Returns
        -------
        float
            Measured current [A]
        """
        return self.command(':MEAS:CURR?')

    def measure_power(self):
        """Measure and return the real-time output power.

        Returns
        -------
        float
            Measured power [W]
        """
        return self.command(':MEAS:POWer?')

    def output(self, on=None):
        """Turn the output ON or OFF.

        Parameters
        ----------
        on : str or int, optional
            'ON', 1 to enable; 'OFF', 0 to disable

        Returns
        -------
        int
            Output status: 1 for ON, 0 for OFF
        """
        if on is not None:
            on = 'ON' if on == 'ON' or on == 1 else 'OFF'
            self.write_line(':OUTP', on)
        return 1 if self.command(':OUTP?') == 'ON' else 0

    def delay_time(self, delay_sec=None):
        """Set or get the delay time after an apply command.

        Parameters
        ----------
        delay_sec : int, optional
            Delay in seconds min 1s max ...??

        Returns
        -------
        int
            Current delay time [s]
        """
        if delay_sec is not None:
            self.write_line(':SYST:AUTO:DEL', delay_sec)
        return self.command(':SYST:AUTO:DEL?')

    def current_protection_level(self, ampers=None):
        """Set or get the current protection level (fuse).

        Parameters
        ----------
        ampers : float, optional
            Maximum current [A] before protection triggers

        Returns
        -------
        float
            Applied current protection level [A]
        """
        if ampers is not None:
            self.write_line(':CURR:PROT:LEV', ampers)
        return self.command(':CURR:PROT:LEV?')

    def current_protection_state(self, on=None):
        """Enable or disable current protection.

        Parameters
        ----------
        on : str or int, optional
            'ON', 1 to enable; 'OFF', 0 to disable

        Returns
        -------
        int
            Current protection status: 1 for ON, 0 for OFF
        """
        if on is not None:
            on = 'ON' if on and on != 'OFF' else 'OFF'
            self.write_line(':CURR:PROT:STAT', on)
        return 1 if self.command(':CURR:PROT:STAT?') == 'ON' else 0

    def current_protection_triped(self):
        """Check if current protection has been triggered.

        Returns
        -------
        int
            1 if tripped, 0 otherwise
        """
        return 1 if self.command(':CURR:PROT:TRIP?') == 'ON' else 0

    def current_protection_clear(self):
        """Clear the tripped current protection fuse.

        Returns
        -------
        int
            1 if still tripped, 0 if cleared
        """
        self.command(':CURR:PROT:CLE')
        return 1 if self.command(':CURR:PROT:TRIP?') == 'ON' else 0

    def voltage_protection_state(self, on=None):
        """Enable or disable voltage protection.

        Parameters
        ----------
        on : str or int, optional
            'ON', 1 to enable; 'OFF', 0 to disable

        Returns
        -------
        int
            Voltage protection status: 1 for ON, 0 for OFF
        """
        if on is not None:
            on = 'ON' if on and on != 'OFF' else 'OFF'
            self.write_line(':VOLT:PROT:STAT', on)
        return 1 if self.command(':VOLT:PROT:STAT?') == 'ON' else 0

    def voltage_protection_level(self, volts=None):
        """Set or get the voltage protection level (fuse).

        Parameters
        ----------
        volts : float, optional
            Maximum voltage [V] before protection triggers

        Returns
        -------
        float
            Applied voltage protection level [V]
        """
        if volts is not None:
            self.write_line(':VOLT:PROT:LEV', volts)
        return self.command(':VOLT:PROT:LEV?')

    def voltage_protection_triped(self):
        """Check if voltage protection has been triggered.

        Returns
        -------
        int
            1 if tripped, 0 otherwise
        """
        return 1 if self.command(':VOLT:PROT:TRIP?') == 'ON' else 0

    def voltage_protection_clear(self):
        """Clear the tripped voltage protection fuse.

        Returns
        -------
        int
            1 if still tripped, 0 if cleared
        """
        self.command(':VOLT:PROT:CLE')
        return 1 if self.command(':VOLT:PROT:TRIP?') == 'ON' else 0


if __name__ == '__main__':
    #from calibration import oc
    ports = serial_ports_list()
    mnfact = 'Prolific Technology'
    baudrate = 9600
    serial_port_dev = search_by_manufacturer(ports, mnfact_linux)

    print(serial_port_dev)

    ps = Ax6003Py(port=serial_port_dev, baudrate=baudrate)
    #oc(ps.measure_voltage(),'equ')
