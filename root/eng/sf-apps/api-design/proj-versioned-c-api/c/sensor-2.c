// sensor.c  —  v2: читаємо нові поля ЛИШЕ якщо клієнт їх приніс
sensor_t *sensor_open(const sensor_config_t *cfg) {
    if (!cfg || cfg->size < sizeof(cfg->size)) return NULL;

    int      pin     = cfg->pin;
    uint32_t rate_hz = cfg->rate_hz;

    // калібрування — тільки якщо структура достатньо велика, щоб його вміщати:
    uint8_t gain   = 1;       // дефолти для старих клієнтів
    float   offset = 0.0f;
    if (cfg->size >= offsetof(sensor_config_t, gain) + sizeof cfg->gain)
        gain = cfg->gain;
    if (cfg->size >= offsetof(sensor_config_t, offset) + sizeof cfg->offset)
        offset = cfg->offset;
    /* … застосовуємо pin, rate_hz, gain, offset … */
}
