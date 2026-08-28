// --- sensor.c ---
static sensor_driver_t *find(const char *name) {
    for (uint8_t i = 0; i < g_driver_count; i++)          // лінійний пошук
        if (strcmp(g_drivers[i].name, name) == 0)         // порівняння рядків
            return &g_drivers[i];
    return 0;
}

int sensor_register(const sensor_driver_t *d) {
    if (g_driver_count >= MAX_DRIVERS) return -1;
    g_drivers[g_driver_count++] = *d;                     // копія 40+ байтів
    return 0;
}

void sensor_set_calibration(const char *name, float off, float scale) {
    sensor_driver_t *d = find(name);
    if (d) { d->offset_cal = off; d->scale_cal = scale; }
}

void sensor_set_filter(const char *name, uint8_t order) {
    sensor_driver_t *d = find(name);
    if (d && order <= 8) d->filter_order = order;
}

int sensor_read_by_name(const char *name, float *celsius) {
    sensor_driver_t *d = find(name);                      // пошук на КОЖНЕ читання
    if (!d) return -1;

    int32_t raw;
    if (d->read_raw(d->ctx, &raw) != 0) return -2;        // непрямий виклик

    if (d->filter_order > 1) {                            // ковзне середнє
        d->hist[d->hist_pos++ % 8] = raw;
        int32_t sum = 0;
        for (uint8_t i = 0; i < d->filter_order; i++)
            sum += d->hist[i];
        raw = sum / d->filter_order;
    }
    float t = (float)raw * 0.01f;                         // сирі 0.01 °C
    t = t * d->scale_cal + d->offset_cal;                 // калібрування
    *celsius = t;
    return 0;
}
