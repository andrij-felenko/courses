# hub.py — Digital Homes v1: той самий дім, але за швами. Драйвери — мокові.
from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol
from time import sleep
import random

# ── Значення на межах: одиниця й статус живуть у типі, не в чиїйсь голові ──
@dataclass(frozen=True)
class Reading:                       # DTO давача
    celsius: float                   # ЗАВЖДИ °C
    ok: bool = True                  # чи це справжнє свіже число

@dataclass(frozen=True)
class Config:
    threshold: float = 20.0          # поріг — вхід рішення, а не його нутрощі

class Command(Enum):                 # рішення — це ЗНАЧЕННЯ, а не вчинок
    HEAT = auto()
    IDLE = auto()

# ── Порти: логіка залежить від них, а не від марки заліза ──
class Sensor(Protocol):
    def read(self) -> Reading: ...

class Heater(Protocol):
    def on(self) -> None: ...        # ідемпотентно
    def off(self) -> None: ...

# ── Мокова фізика: те єдине, що справді спільне — повітря кімнати ──
class MockRoom:
    def __init__(self, temp=18.0):
        self.temp = temp             # «справжня» температура повітря, °C
        self.heating = False         # чи подано струм на грілку
    def drift(self):                 # холоне сама, гріється під струмом, + шум виміру
        self.temp += (0.4 if self.heating else -0.2) + random.uniform(-0.05, 0.05)

# ── Драйвер давача: мову СВОГО заліза знає тільки він ──
class MockThermometer:               # реалізує порт Sensor
    def __init__(self, room, fault_plan=()):
        self._room = room
        self._faults = iter(fault_plan)          # напр. (0,0,1,0): 1 імітує збій заліза
    def read(self) -> Reading:
        self._room.drift()                       # фізика марширує далі, дарма що давач німий
        if next(self._faults, 0):                # таймаут / CRC=NO — числа немає
            return Reading(celsius=float("nan"), ok=False)   # переклад збою на «не вірю»
        milli = round(self._room.temp * 1000)    # сирий діалект: цілі мілі-°C, як 1-Wire
        return Reading(celsius=milli / 1000, ok=True)        # переклад одиниць ТУТ, на краю

# ── Драйвер розетки: ідемпотентний ──
class MockPlug:                      # реалізує порт Heater
    def __init__(self, room, name="вітальня"):
        self._room = room
        self._name = name
    def on(self):
        if not self._room.heating:   # повторний «увімкни» реле дарма не смикає
            self._room.heating = True
            print(f"[{self._name}] обігрівач УВІМКНЕНО")
    def off(self):
        if self._room.heating:
            self._room.heating = False
            print(f"[{self._name}] обігрівач вимкнено")

# ── Чисте рішення: ті самі входи → той самий вихід, жодних ефектів ──
def decide(r: Reading, cfg: Config) -> Command:
    if not r.ok:
        return Command.IDLE          # давач мовчить → безпечний спокій, не «грій наосліп»
    return Command.HEAT if r.celsius < cfg.threshold else Command.IDLE

# ── Збірка: тонкий цикл, що лише диригує ──
def run(sensor: Sensor, heater: Heater, cfg: Config, ticks=None):
    n = 0
    while ticks is None or n < ticks:
        reading = sensor.read()              # драйвер ховає діалект і збої заліза
        if not reading.ok:
            print("[давач] мовчить — тримаю безпечний спокій")   # видимість збою нагорі
        if decide(reading, cfg) is Command.HEAT:
            heater.on()
        else:
            heater.off()
        sleep(30)
        n += 1

# ── Корінь склеювання: конкретне зустрічає конкретне рівно тут ──
if __name__ == "__main__":
    room = MockRoom(temp=18.0)               # спільне «повітря» для давача й розетки
    run(sensor=MockThermometer(room),
        heater=MockPlug(room),
        cfg=Config(threshold=20.0))
