# thermostat.py — СИСТЕМА (те, що поїде в прод). Один код на всі три рівні.
from dataclasses import dataclass
from typing import Protocol


class Sensor(Protocol):
    def read(self) -> float: ...          # контракт: завжди віддає °C

class Heater(Protocol):
    def on(self) -> None: ...
    def off(self) -> None: ...


# політика + проводка: читає крізь шов, керує грілкою
def decide(sensor: Sensor, heater: Heater, threshold: float) -> None:
    if sensor.read() < threshold:
        heater.on()
    else:
        heater.off()


class Device(Protocol):
    def temp_f(self) -> float: ...        # вендорів пристрій говорить у °F


class VendorSensorAdapter:                # адаптер: вендорові °F → наші °C (правильна версія)
    def __init__(self, device: Device) -> None:
        self._device = device
    def read(self) -> float:
        return (self._device.temp_f() - 32) * 5 / 9


@dataclass
class Config:
    threshold: float


class Hub:                                # те, що прод збирає й крутить
    def __init__(self, sensor: Sensor, heater: Heater, threshold: float) -> None:
        self._sensor, self._heater, self._threshold = sensor, heater, threshold
    def tick(self) -> None:
        decide(self._sensor, self._heater, self._threshold)


def build_hub(sensor: Sensor, heater: Heater, cfg: Config) -> Hub:
    return Hub(sensor, heater, cfg.threshold)
