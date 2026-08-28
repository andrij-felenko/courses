from typing import Protocol

class Device(Protocol):              # ПОРТ — давач і розетка одним отвором, мовою ядра
    def temperature(self) -> float: ...   # °C, не мілі-градуси й не вольти
    def heat(self, on: bool) -> None: ...

# ── Адаптер 1: СПРАВЖНІЙ. Єдиний в усьому хабі, хто говорить мовою заліза. ──
import urllib.request

class RealDevice:                    # 1-Wire давач + Wi-Fi розетка (напр. Shelly)
    def __init__(self, w1_id: str, plug_url: str):
        self._w1 = f"/sys/bus/w1/devices/{w1_id}/w1_slave"
        self._plug = plug_url

    def temperature(self) -> float:
        text = open(self._w1).read()          # "...crc=.. YES\n.. t=20125"
        milli = int(text.split("t=")[-1])     # DS18B20 віддає мілі-градуси
        return milli / 1000.0                 # → °C ТУТ, на межі; далі ядро °C і не бачить іншого

    def heat(self, on: bool) -> None:
        turn = "on" if on else "off"
        urllib.request.urlopen(f"{self._plug}/relay/0?turn={turn}", timeout=3)

# ── Адаптер 2: ПІДРОБКА. Кімната живе в пам'яті + пише журнал команд. ──
import random

class FakeDevice:
    def __init__(self, start: float = 18.0):
        self._room = start           # прихований «фізичний» стан, як у моку v0
        self._on = False
        self.log: list[bool] = []    # журнал переходів — щоб тест мав що перевірити

    def temperature(self) -> float:
        self._room += (0.4 if self._on else -0.2) + random.uniform(-0.05, 0.05)
        return round(self._room, 1)

    def heat(self, on: bool) -> None:
        if on != self._on:           # записуємо лише реальні перемикання
            self.log.append(on)
        self._on = on
