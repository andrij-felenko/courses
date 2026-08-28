# drivers.py — справжні драйвери. Тіла мокують фізику; у продакшені — залізо.
import random


class Room:                            # прихована «фізика»: у реальності це саме повітря кімнати
    def __init__(self, temp: float = 18.0) -> None:
        self.temp = temp
        self.heating = False


class RealSensor:                      # дотримує контракт Sensor структурно
    def __init__(self, room: Room) -> None:
        self._room = room
    def read(self) -> float:
        self._room.temp += (0.4 if self._room.heating else -0.2) + random.uniform(-0.05, 0.05)
        return round(self._room.temp, 1)          # °C дробом — таким є контракт


class RealHeater:
    def __init__(self, room: Room) -> None:
        self._room = room
    def on(self) -> None:
        if not self._room.heating:                # ідемпотентно: не смикати реле дарма
            self._room.heating = True
            print("[розетка] обігрівач УВІМКНЕНО")
    def off(self) -> None:
        if self._room.heating:
            self._room.heating = False
            print("[розетка] обігрівач вимкнено")


# main.py — точка ввімкнення. САМЕ ТУТ вирішено, що під'єднати до шва.
from time import sleep

def run() -> None:
    room = Room(temp=18.0)
    sensor, heater = RealSensor(room), RealHeater(room)   # ← вимикач стоїть ТУТ
    while True:
        decide(sensor, heater, threshold=20.0)            # політику не чіпаємо
        sleep(30)

if __name__ == "__main__":
    run()
