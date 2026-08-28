# sw6106_probe.py — та сама перевірка, коротко.
#   pip install smbus2   (або: apt install python3-smbus)
from smbus2 import SMBus

BUS      = 1       # /dev/i2c-1 — гребінка Pi
SW6106   = 0x3C    # 7-бітна адреса; бібліотека сама зсуне її
REG      = 0xB0    # керувальний регістр із datasheet

try:
    with SMBus(BUS) as bus:
        val = bus.read_byte_data(SW6106, REG)
        print(f"SW6106 reg 0xB0 = 0x{val:02X}")
        print("Це керувальне значення, НЕ відсоток заряду.")
except OSError as e:
    # errno 121 == Remote I/O error: пристрій не відповів
    print(f"Немає відповіді (errno {e.errno}).")
    print("Спершу перевір i2cdetect -y 1: чи є 3c у сітці?")
    print("Порожньо → LED4/I2C не притягнуто до землі на цій платі.")
