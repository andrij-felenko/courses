// Спекулятивно: гнучкість "на виріст", якої ніхто не просив.
// Реєстр драйверів, вибір протоколу, конфіг — усе заради ОДНОГО давача.
typedef struct {
    const char *name;
    int  (*read)(void *ctx, float *out);
    void *ctx;
} sensor_driver_t;

static sensor_driver_t drivers[MAX_DRIVERS];   // місце під те, чого нема
static int driver_count = 0;

int sensor_register(sensor_driver_t d) { /* ...25 рядків... */ }
int sensor_read_by_name(const char *n, float *out) { /* ...пошук у реєстрі... */ }

// Те саме, чесно за потребою: рівно те, що просили.
float read_temperature(void) {
    return bmp280_read_celsius();   // один давач — один виклик
}
