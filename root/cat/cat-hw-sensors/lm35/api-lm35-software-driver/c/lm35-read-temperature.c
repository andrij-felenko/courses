// Коди помилок драйвера LM35
typedef enum {
    LM35_OK = 0,
    LM35_ERR_NULL_PTR,
    LM35_ERR_UNDERFLOW,   // Значення нижче допустимої межі (обрив або коротке на GND)
    LM35_ERR_OVERFLOW,    // Значення вище допустимої межі (коротке на VCC)
    LM35_ERR_INVALID_RAW  // Сирий код перевищує маску розрядності АЦП
} lm35_error_t;

// Зчитування та валідація температури
lm35_error_t lm35_read_temperature(const lm35_t *dev, uint32_t raw_adc, float *out_temp) {
    if (dev == NULL || out_temp == NULL) {
        return LM35_ERR_NULL_PTR;
    }
    if (raw_adc > dev->max_adc_raw) {
        return LM35_ERR_INVALID_RAW;
    }

    float temp = lm35_raw_to_celsius(dev, raw_adc);

    // Перевірка фізичних меж (для стандартної однополярної схеми: 0°C .. 100°C)
    if (temp < -5.0f) {
        return LM35_ERR_UNDERFLOW;
    }
    if (temp > 105.0f) {
        return LM35_ERR_OVERFLOW;
    }

    *out_temp = temp;
    return LM35_OK;
}
