# i2c_id.py — читаємо регістр 0xD0 (id) BMP280 за адресою 0x76 на шині i2c-1
# постав:  pip install smbus2
from smbus2 import SMBus

I2C_BUS = 1        # /dev/i2c-1 — лінії SDA (GPIO2) і SCL (GPIO3), виведені платою
ADDR    = 0x76     # адреса BMP280 на шині
REG_ID  = 0xD0     # регістр «id»; має віддати 0x58

# with сам відкриє й закриє шину; адресу пристрою передаємо в кожен виклик.
# read_byte_data робить обидва такти за раз: пише номер регістра, потім читає байт.
with SMBus(I2C_BUS) as bus:
    dev_id = bus.read_byte_data(ADDR, REG_ID)

note = "(BMP280 — зв'язок є!)" if dev_id == 0x58 else "(не той підпис?)"
print(f"id давача = 0x{dev_id:02X} {note}")
