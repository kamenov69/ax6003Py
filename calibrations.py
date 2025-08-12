
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import jsonpickle
from functools import wraps
from typing import Callable, Dict, List, Any

class Calibrations:
    def __init__(self):
        self.poly_dict: Dict[str, List[float]] = {
            "equ": [1.0, 0.0],
            "hlv": [0.5, 0.0]
        }

    def __call__(self, poly_name: str) -> Callable[[Callable[..., float]], Callable[..., float]]:
        def decorator(func: Callable[..., float]) -> Callable[..., float]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> float:
                raw_value = func(*args, **kwargs)
                return self.polynom(raw_value, poly_name)
            return wrapper
        return decorator

    def polynom(self, x: float, name_of_coef: str) -> float:
        coef = self.poly_dict.get(name_of_coef)
        if coef is None:
            raise KeyError(f"Polynomial '{name_of_coef}' not found.")
        if not coef:
            raise ValueError(f"Polynomial '{name_of_coef}' has no coefficients.")
        # Метод на Хорнер
        result = 0.0
        for c in coef:
            result = result * x + c
        return result

    def add_polynom(self, coef: List[float], polynom_name: str) -> None:
        if not coef:
            raise ValueError("coef must contain at least one coefficient.")
        self.poly_dict[polynom_name] = coef

    def polynoms_list(self) -> str:
        items = (f"{k}: {v}" for k, v in sorted(self.poly_dict.items()))
        return ", ".join(items)

    def __repr__(self) -> str:
        return self.polynoms_list()

    def __str__(self) -> str:
        return self.polynoms_list()

    def polynoms_to_file(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            f.write(jsonpickle.encode(self.poly_dict, indent=4))

    def polynoms_from_file(self, file_name: str) -> None:
        with open(file_name, 'r') as f:
            self.poly_dict = jsonpickle.decode(f.read())

    @classmethod
    def from_file_or_default(cls, file_name: str) -> "Calibrations":
        """Създава екземпляр от файл или с базови стойности, ако файлът липсва."""
        inst = cls()
        if os.path.exists(file_name):
            inst.polynoms_from_file(file_name)
        else:
            inst.polynoms_to_file(file_name)
        return inst


if __name__ == '__main__':
    # Създаване или зареждане на калибрации
    calibrations = Calibrations.from_file_or_default("cal_data.json")

    @calibrations('doble')
    def tst_func(arg: float) -> float:
        return arg

    print("Текущи полиноми:", calibrations)
    print("Резултат:", tst_func(42.0))
    
    #calibrations.add_polynom([2,0],'doble')
    #calibrations.polynoms_to_file("cal_data.json")
