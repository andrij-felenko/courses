# hub.py — увесь «розумний дім» Digital Homes v0, один файл
from time import sleep
import random

THRESHOLD = 20.0                 # °C — поріг зашитий просто в код

# ── Драйвери. Тут вони МОКОВІ: замість заліза дім живе в пам'яті.
#    Кімната сама холоне, а коли ввімкнено розетку — гріється.
#    Ці три тіла — єдине, що знає мову конкретного пристрою. ──
_room = 18.0                     # прихований «фізичний» стан кімнати, °C
_heater = False                  # чи подано живлення на обігрівач

def read_sensor():               # драйвер давача → °C
    global _room
    _room += (0.4 if _heater else -0.2) + random.uniform(-0.05, 0.05)
    return round(_room, 1)

def heater_on():                 # драйвер розетки: подати живлення
    global _heater
    if not _heater:              # ідемпотентно: не смикати реле дарма
        _heater = True
        print("[розетка] обігрівач УВІМКНЕНО")

def heater_off():                # драйвер розетки: зняти живлення
    global _heater
    if _heater:
        _heater = False
        print("[розетка] обігрівач вимкнено")

# ── Серце дому: read → decide → act, і так вічно. ──
while True:
    t = read_sensor()            # read
    if t < THRESHOLD:            # decide
        heater_on()              # act
    else:
        heater_off()
    sleep(30)                    # знову спитати давач за 30 с
