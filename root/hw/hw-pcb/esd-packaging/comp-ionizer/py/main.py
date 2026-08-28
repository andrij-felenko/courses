# поле впало під безпечний поріг? (12-біт АЦП, 0.806 мВ/крок)
ADC_THRESHOLD = 124              # ≈ 100 В на поверхні
SETTLE_MS     = 300              # підряд триматись нижче порогу

def surface_is_safe() -> bool:
    below = 0
    while below < SETTLE_MS:
        if adc_read(FIELD_SENSOR) < ADC_THRESHOLD:
            below += 10           # ще 10 мс «чисто»
        else:
            below = 0             # підскочило — лік спочатку
        time.sleep_ms(10)
    return True                   # тримається нижче порогу → нейтралізовано
