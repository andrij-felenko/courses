// поле впало під безпечний поріг? (12-біт АЦП, 0.806 мВ/крок)
#define ADC_THRESHOLD 124        // ≈ 100 В на поверхні
#define SETTLE_MS     300        // підряд триматись нижче порогу

bool surface_is_safe(void) {
    uint32_t below = 0;
    while (below < SETTLE_MS) {
        if (adc_read(FIELD_SENSOR) < ADC_THRESHOLD)
            below += 10;         // ще 10 мс «чисто»
        else
            below = 0;           // підскочило — лік спочатку
        delay_ms(10);
    }
    return true;                 // тримається нижче порогу → нейтралізовано
}
