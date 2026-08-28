// Дві чесні функції спершу — кожна робить рівно своє
static bool read_bmp280(float *celsius) {
    int32_t raw = bmp280_read_centi_celsius();
    *celsius = (float)raw * 0.01f;
    return true;
}

static bool read_max31855(float *celsius) {
    int32_t raw;
    if (!max31855_read_raw(&raw)) return false;  // термопара сигналить обрив
    *celsius = (float)raw * 0.25f;               // інша ціна молодшого біта
    return true;
}
