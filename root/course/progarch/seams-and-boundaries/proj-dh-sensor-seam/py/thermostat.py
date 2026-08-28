# thermostat.py — політика керування теплом із відкритим об'єктним швом.
# Тіло decide НЕ знає, звідки береться число й куди йде команда.
from typing import Protocol


class Sensor(Protocol):
    def read(self) -> float: ...      # контракт: віддати °C; не кидати виняток крізь межу


class Heater(Protocol):
    def on(self) -> None: ...
    def off(self) -> None: ...


def decide(sensor: Sensor, heater: Heater, threshold: float) -> None:
    t = sensor.read()                 # ← шов: чим є sensor, вирішують ЗЗОВНІ
    if t < threshold:
        heater.on()
    else:
        heater.off()
