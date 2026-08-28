// sensor.c
sensor_status_t sensor_read_v2(sensor_t *s, float *out) {
    if (!s || !out) return SENSOR_ERR_RANGE;
    /* … читаємо АЦП … */
    *out = /* виміряне зі scale/offset */ 0.0f;
    return SENSOR_OK;             // тепер клієнт РОЗРІЗНЯЄ помилку від валідного 0.0
}

float sensor_read(sensor_t *s) {         // стара форма — тонка обгортка над новою
    float v = 0.0f;
    sensor_read_v2(s, &v);               // помилку стара форма мовчки ковтає, як і раніше
    return v;                            // її контракт не змінився — 0.0 при збої
}
