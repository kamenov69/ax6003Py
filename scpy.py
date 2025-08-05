#!/usr/bin/env python
# coding: utf-8
# pykiba V3.0 – initially named pykibaNew
#     - Added timeout before sending a command
#     - Replaced .split(',') with re.split
#     - Appended '\n' when sending commands
# Note: No use of the Walrus operator!
# Compatible with old functions, but redesigned
# V3.1 – Added def install_arduino_commands(self)

import serial
import re
import time
from tools import print_my_ip, search_by_manufacturer, serial_ports_list

def prepare_line_to_send(*args):
    """Converts all input arguments into a formatted byte string for serial transmission.

    Handles int, float, and str input types. Adds newline at the end.
    Floats are scaled (x1000) and appended with a marker "-3" [legacy, not implemented here].

    Returns
    -------
    bytes
        A single byte string ready for serial transmission.
    """
    output_buffer = []
    for index, word in enumerate(args):
        if isinstance(word, int) or isinstance(word, float) or isinstance(word, str):
            word = str(word).encode()

        if word[-1] == 13:  # Remove trailing carriage return if present
            word = word[:-1]

        output_buffer.append(word)
        output_buffer.append(b',' if index else b' ')

    output_buffer.pop(-1)  # Remove trailing separator
    output_buffer.append(b'\n')

    return b''.join(output_buffer)

def parse_line(line):
    """Parses a byte line received from serial into appropriate Python types.

    Splits the line into tokens, then converts each to int or float when possible.
    Leaves token as string if conversion fails.

    Parameters
    ----------
    line : bytes
        Raw line of serial data.

    Returns
    -------
    int, float, str, or list of these
        Parsed response.
    """
    line = line.decode().strip()
    tokens = re.split(r"[, ;#!?:]+", line)
    output_val = []
    for token in tokens:
        cleaned = re.sub('[^0-9,.]', '', token)
        try:
            output_val.append(int(cleaned))
            continue
        except ValueError:
            pass
        try:
            output_val.append(float(cleaned))
            continue
        except ValueError:
            pass
        output_val.append(token)

    if len(output_val) == 1:
        return output_val[0]
    if not output_val:
        return None
    return output_val


class Scpy(serial.Serial):
    """Main class for SCPI communication over serial interface.

    Inherits from serial.Serial and provides methods for SCPI command interaction.
    """

    def __init__(self, **kargs):
        """Initializes the serial connection.

        Parameters
        ----------
        port : str
            Serial port name (e.g., '/dev/ttyUSB0')
        baudrate : int
            Serial baud rate (e.g., 9600)
        """
        super().__init__(**kargs)
        self.string_rep = f"Connected on {kargs}\n\n"
        self.timeout = 1
        _ = self.read_all()  # Clear buffer

    def write_line(self, *args):
        """Formats and sends a command line to the device.

        Waits for the output buffer to clear before sending.
        """
        line = prepare_line_to_send(*args)
        while self.out_waiting:
            pass
        self.echo_of_the_command = line
        self.write(line)
        self.flush()

    def raw_lines(self, *args, timeout=5):
        """Send command and receive raw response lines.

        Parameters
        ----------
        *args : arguments for write_line
        timeout : float
            Response wait time in seconds.

        Returns
        -------
        list of bytes
            Raw serial lines from device.
        """
        tmp_timeout = self.timeout
        self.timeout = timeout
        _ = self.read_all()
        self.write_line(*args)
        lines = self.readlines()
        self.timeout = tmp_timeout
        return lines

    def command(self, *args, timeout=2.5):
        """Send command and return parsed response.

        Main method to communicate with SCPI device.

        Parameters
        ----------
        *args : str/int/float
            Command and arguments.
        timeout : float
            Read timeout.

        Returns
        -------
        Parsed response (int, float, str, or list)
        """
        tmp_timeout = self.timeout
        self.timeout = timeout
        self.flush()
        while self.out_waiting:
            pass
        time.sleep(0.25)
        _ = self.read_all()
        self.write_line(*args)
        response = []
        while True:
            if response:
                break
            line = self.readline()
            if self.echo_of_the_command in line:
                continue
            parsed = parse_line(line)
            response.append(parsed)
            if '' in response:
                response.remove('')
                break

        self.echo_of_the_command = None
        self.timeout = tmp_timeout
        if len(response) == 1:
            return response[0]
        if not response:
            return None
        return response

    def id_number(self):
        """Query device ID number.

        Returns
        -------
        int
            Device ID number
        """
        return self.command('*IDN?')

    def status(self):
        """Query status byte.

        Returns
        -------
        int
            Status byte (refer to device manual for meaning)
        """
        return self.command('*ESR?')

    def ready(self):
        """Query operation complete flag.

        Returns
        -------
        int
            1 if operation complete
        """
        return self.command('*OPC?')

    def clear_errors(self):
        """Clear all errors in status byte.

        Returns
        -------
        int
            Cleared status byte
        """
        self.write_line('*CLS')
        return self.command('*ESR?')

    def power_on_clean_status(self, state=None):
        """Configure status clearing on power-up.

        Parameters
        ----------
        state : int, optional
            0 = retain status, 1 = clear status after restart

        Returns
        -------
        int
            Currently set state
        """
        if state is not None:
            state = 1 if state != 0 else 0
            self.write_line('*PSC', state)
        return self.command('*PSC?')

    def reset(self):
        """Perform full device reset.

        Returns
        -------
        int
            Operation complete flag after reset
        """
        self.write_line('*RST')
        time.sleep(7)
        return self.command('*OPC?')

    def __repr__(self):
        return self.string_rep

    def __str__(self):
        return self.string_rep

    def __del__(self):
        self.close()


if __name__ == '__main__':
    import tools

    ports = tools.serial_ports_list()
    mnfact = 'Prolific Technology'
    baudrate = 9600
    serial_port_dev = tools.search_by_manufacturer(ports, mnfact)

    print(serial_port_dev)

    ps = Scpy(port=serial_port_dev, baudrate=baudrate)
