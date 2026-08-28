# smbus2 — стандартний шлях на Raspberry Pi.
# Пристрій 0x3C, єдиний задокументований регістр 0xB0.
from smbus2 import SMBus

I2C_BUS  = 1       # шина i2c-1 на 40-піновій гребінці
SW6106   = 0x3C    # адреса пристрою з datasheet
REG_CTRL = 0xB0    # єдиний задокументований регістр

with SMBus(I2C_BUS) as bus:
    try:
        raw = bus.read_byte_data(SW6106, REG_CTRL)
        print(f"0xB0 = 0x{raw:02X}  (0b{raw:08b})")
    except OSError as e:
        # errno 121 = Remote I/O error: пристрій не відповів (ACK не прийшов).
        # Майже завжди означає: LED4/I2C не на землі АБО не той пристрій.
        print(f"пристрій 0x{SW6106:02X} мовчить: {e}")
