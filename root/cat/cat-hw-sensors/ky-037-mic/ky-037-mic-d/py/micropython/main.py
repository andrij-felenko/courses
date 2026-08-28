from machine import ADC, Pin
from time import ticks_ms, ticks_diff

mic = ADC(Pin(26))            # аналоговий вихід KY-037
WINDOW = 50                   # вікно вимірювання, мс

def measure_loudness():
    t0 = ticks_ms()
    hi, lo = 0, 65535         # межі діапазону read_u16 (16-біт)
    while ticks_diff(ticks_ms(), t0) < WINDOW:
        v = mic.read_u16()    # миттєва точка хвилі
        if v > hi:
            hi = v
        if v < lo:
            lo = v
    return hi - lo            # РОЗМАХ: тиша ≈ мало, гучно ≈ багато

while True:
    loud = measure_loudness()
    print(loud)               # спробуй у тиші й під оплеск — числа різні
