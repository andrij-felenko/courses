# поле впало під безпечний поріг? (12-біт АЦП, 0.806 мВ/крок)
from machine import ADC, Pin
import time

ADC_THRESHOLD = 124              # ≈ 100 В на поверхні
SETTLE_MS     = 300              # підряд триматись нижче порогу
field = ADC(Pin(34))            # польовий датчик

def surface_is_safe():
    below = 0
    while below < SETTLE_MS:
        if field.read() < ADC_THRESHOLD:
            below += 10           # ще 10 мс «чисто»
        else:
            below = 0             # підскочило — лік спочатку
        time.sleep_ms(10)
    return True                   # тримається нижче порогу → нейтралізовано
