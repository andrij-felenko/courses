typedef enum {
    PT100_OK = 0,
    PT100_ERR_OPEN_CIRCUIT = -1,
    PT100_ERR_SHORT_CIRCUIT = -2,
    PT100_ERR_OUT_OF_RANGE = -3,
    PT100_ERR_CALIBRATION = -4
} pt100_status_t;

pt100_status_t pt100_get_temperature(pt100_t *dev, float *temp_c) {
    if (!dev || !dev->is_initialized) return PT100_ERR_CALIBRATION;

    float resistance = 0.0f;
    // 1. Зчитування коду АЦП та обчислення опору
    pt100_read_resistance(dev, &resistance);

    // 2. Перевірка на апаратні аварії
    if (resistance > 400.0f) return PT100_ERR_OPEN_CIRCUIT;
    if (resistance < 18.0f)  return PT100_ERR_SHORT_CIRCUIT;

    // 3. Лінеаризація за рівнянням Каллендара — Ван Дюзена
    float t = pt100_process_cvd(resistance);

    if (t < -200.0f || t > 850.0f) return PT100_ERR_OUT_OF_RANGE;

    *temp_c = t;
    return PT100_OK;
}
