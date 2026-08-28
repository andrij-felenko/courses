from machine import Pin, time_pulse_us
from time import sleep_ms, sleep_us

TRIG = Pin(9, Pin.OUT)
ECHO = Pin(10, Pin.IN)

def measure_cm():
    # 1. Спусковий імпульс: 10 мкс високого рівня на TRIG
    TRIG.low()
    sleep_us(2)
    TRIG.high()
    sleep_us(10)
    TRIG.low()

    # 2. Ширина високого імпульсу на ECHO = час польоту в мкс.
    #    Тайм-аут 30000 мкс, щоб не зависнути, коли луни немає.
    t = time_pulse_us(ECHO, 1, 30000)

    if t < 0:                    # нічого не почули (порожньо/далеко)
        return -1
    return t // 58              # мкс → см

while True:
    cm = measure_cm()
    if cm < 0:
        print("out of range")
    else:
        print(cm, "cm")
    sleep_ms(60)                 # пауза між вимірами ≥ 60 мс
