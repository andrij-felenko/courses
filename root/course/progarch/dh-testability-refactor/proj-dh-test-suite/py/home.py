# home.py — код під тестом (форми v1, без змін)
from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol

@dataclass(frozen=True)
class Reading:
    celsius: float
    ok: bool = True          # False ⇒ числу вірити не можна

@dataclass(frozen=True)
class Config:
    threshold: float = 20.0

class Command(Enum):
    HEAT = auto()
    IDLE = auto()

class Sensor(Protocol):
    def read(self) -> Reading: ...

class Heater(Protocol):
    def on(self)  -> None: ...
    def off(self) -> None: ...

def decide(r: Reading, cfg: Config) -> Command:      # чиста: вхід-значення → вихід-значення
    if not r.ok:
        return Command.IDLE
    return Command.HEAT if r.celsius < cfg.threshold else Command.IDLE

def tick(sensor: Sensor, heater: Heater, cfg: Config) -> None:   # рівно один оберт
    match decide(sensor.read(), cfg):
        case Command.HEAT: heater.on()
        case Command.IDLE: heater.off()
