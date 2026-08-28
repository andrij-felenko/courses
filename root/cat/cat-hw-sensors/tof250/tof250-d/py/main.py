from smbus2 import SMBus, i2c_msg
import time

TOF_ADDR = 0x52          # 7-бітна адреса модуля (байт 0xA4 → 0x52)

def read_distance_mm(bus):
    try:
        write = i2c_msg.write(TOF_ADDR, [0x00])  # хочу читати з регістра 0x00 (відстань)
        read = i2c_msg.read(TOF_ADDR, 2)         # очікую два байти
        bus.i2c_rdwr(write, read)                # повторний старт, не відпускаючи шину
    except OSError:
        return -1                                # модуль не відповів
    hi, lo = list(read)                          # старший, молодший байт
    return (hi << 8) | lo                        # мм

with SMBus(1) as bus:
    while True:
        mm = read_distance_mm(bus)
        if mm >= 0:
            print(mm, "mm")
        time.sleep(0.1)                          # ~10 разів на секунду
