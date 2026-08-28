from machine import I2C, Pin
import time

TOF_ADDR = 0x52
i2c = I2C(0, scl=Pin(22), sda=Pin(21))         # типові виводи плати

def tof_read():
    try:
        raw = i2c.readfrom_mem(TOF_ADDR, 0x00, 2)   # регістр живої відстані
    except OSError:
        return None
    return (raw[0] << 8) | raw[1]

print("TOF250 готовий")
while True:
    mm = tof_read()
    if mm is not None:
        print(mm, "mm")
    else:
        print("немає відповіді (перевір адресу й дроти)")
    time.sleep_ms(100)                         # ~10 замірів на секунду
