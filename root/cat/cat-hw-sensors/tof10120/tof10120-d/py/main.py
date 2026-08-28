from machine import I2C, Pin
from time import sleep_ms

TOF_ADDR = 0x52          # 7-бітна адреса (байт 0xA4 → 0x52)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))    # ніжки — під свою плату

def read_distance_mm():
    try:
        # readfrom_mem: пише регістр 0x00 (відстань) і зразу читає два байти
        b = i2c.readfrom_mem(TOF_ADDR, 0x00, 2)
    except OSError:
        return -1                         # модуль не відповів
    return (b[0] << 8) | b[1]             # старший, молодший → мм

while True:
    mm = read_distance_mm()
    if mm >= 0:
        print(mm, "mm")
    sleep_ms(100)
