// --- main.c: як воно насправді викликається ---
static int bmp280_read(void *ctx, int32_t *out) {
    (void)ctx;
    *out = bmp280_read_centi_celsius();   // сотні градуса від мікросхеми
    return 0;
}

void app_init(void) {
    sensor_driver_t d = {
        .name = "bmp280",
        .read_raw = bmp280_read,
        .ctx = 0,
        .offset_cal = 0.0f,
        .scale_cal = 1.0f,          // калібрування = "нічого не робити"
        .filter_order = 1,          // фільтр = "нічого не робити"
        .enable_crc = false,
    };
    sensor_register(&d);
}

float read_temperature(void) {
    float t;
    sensor_read_by_name("bmp280", &t);   // пошук за рядком "bmp280"
    return t;
}
