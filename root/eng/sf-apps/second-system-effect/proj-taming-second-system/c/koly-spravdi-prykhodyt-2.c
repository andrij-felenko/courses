// Абстракція, ВИВЕДЕНА з двох реальних випадків, а не вгадана з одного
typedef bool (*temp_read_fn)(float *celsius);

// Один запис — одна функція. Жодних полів "про запас":
// калібрування, фільтр, ім'я з'являться ЛИШЕ коли їх попросить реальний давач.
static const temp_read_fn SENSORS[] = { read_bmp280, read_max31855 };
#define SENSOR_COUNT (sizeof SENSORS / sizeof SENSORS[0])

bool read_temperature_n(uint8_t idx, float *celsius) {
    if (idx >= SENSOR_COUNT) return false;
    return SENSORS[idx](celsius);
}
