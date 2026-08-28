from machine import I2C, Pin
import time

TOF_ADDR = 0x52          # 7-бітна адреса модуля (байт 0xA4 → 0x52)

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

def read_distance_mm():
    try:
        i2c.writeto(TOF_ADDR, b"\x00")   # хочу читати з регістра 0x00 (відстань)
        data = i2c.readfrom(TOF_ADDR, 2) # очікую два байти
    except OSError:
        return -1                        # модуль не відповів
    hi, lo = data[0], data[1]            # старший, молодший байт
    return (hi << 8) | lo                # мм

while True:
    mm = read_distance_mm()
    if mm >= 0:
        print(mm, "mm")
    time.sleep_ms(100)                   # ~10 разів на секунду
