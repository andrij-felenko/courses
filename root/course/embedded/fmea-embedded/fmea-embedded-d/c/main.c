// Читаємо висоту; повертаємо false, якщо давач мовчить або бреше.
bool altimeter_read(float *out_m) {
    uint16_t raw;
    // тайм-аут шини: мовчання довше за поріг — це теж відмова, не «ще трішки»
    esp_err_t err = i2c_read_timeout(ALT_ADDR, &raw, /*ms=*/50);
    if (err != ESP_OK) {
        return false;                       // шина зависла / давач не відповів
    }
    float m = raw_to_metres(raw);
    if (m < -500.0f || m > 9000.0f) {       // фізично неможлива висота — давач бреше
        return false;
    }
    *out_m = m;
    return true;
}
