import machine
import gc
import time

# У MicroPython USB-CDC уже піднято до старту скрипта,
# а print() пише саме в нього — окремо чекати порту не треба.
print()
print("ESP32-S3 SuperMini живий.")
freq = machine.freq()  # тактова частота, Гц
print("Чип: ESP32-S3, частота: {} МГц".format(freq // 1_000_000))
print("Вільна купа: {} байт".format(gc.mem_free()))

while True:
    print("аптайм: {} мс".format(time.ticks_ms()))
    time.sleep_ms(1000)
