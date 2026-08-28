// Крок 2: жодного реєстру, жодного strcmp — прямий виклик davача
static int bmp280_read(int32_t *out) {
    *out = bmp280_read_centi_celsius();
    return 0;
}

int sensor_read(float *celsius) {
    int32_t raw;
    if (bmp280_read(&raw) != 0) return -2;
    *celsius = (float)raw * 0.01f;
    return 0;
}
