# i2c_id.py — читаємо регістр 0xD0 (id) давача BMP280 за адресою 0x76 на шині i2c-1
# постановка:  pip install smbus2   (або sudo apt install python3-smbus2)
from smbus2 import SMBus

I2C_BUS = 1        # шина i2c-1: фізичні штирки 3 (SDA) і 5 (SCL)
ADDR    = 0x76     # адреса BMP280 на шині
REG_ID  = 0xD0     # регістр «id»; має віддати 0x58

# with сам відкриє /dev/i2c-1 і закриє його на виході.
with SMBus(I2C_BUS) as bus:
    # read_byte_data робить обидва такти за раз: пише номер регістра,
    # потім читає один байт відповіді — та сама розмова, що в C.
    id = bus.read_byte_data(ADDR, REG_ID)

hint = "(BMP280 — зв'язок є!)" if id == 0x58 else "(не той підпис?)"
print(f"id давача = 0x{id:02X} {hint}")
