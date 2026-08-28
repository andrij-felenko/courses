from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)            # незмінний: отримав Reading — його вже не підмінять
class Reading:
    celsius: float                 # ЗАВЖДИ °C: одиниця живе в контракті, не в чиїйсь голові
    ok: bool = True                # чи вдалося дістати справжнє свіже число

class Sensor(Protocol):            # ПОРТ: рішення залежатиме від цього, а не від марки заліза
    def read(self) -> Reading: ...

class OneWireThermometer:          # драйвер: мову СВОГО давача знає тільки він
    def read(self) -> Reading:
        raw = self._device.millicelsius()    # 20125 — діалект саме цього давача
        return Reading(celsius=raw / 1000)   # переклад на °C ТУТ, на самому краю
