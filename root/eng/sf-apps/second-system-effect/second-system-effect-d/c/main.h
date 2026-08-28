// Друга система: роздута "на виріст". Гнучкість, якої ніхто не просив.
typedef struct {
    const char *name;
    int   (*read)(void *ctx, float *out);
    void  *ctx;
    float  offset_cal;       // калібрування — раптом знадобиться
    float  scale_cal;        // і масштаб — теж про запас
    uint16_t sample_rate_hz; // налаштовна частота — а раптом
    uint8_t  filter_order;   // фільтр ковзного середнього — на майбутнє
    bool     enable_crc;     // перевірка цілісності по шині — про всяк
} sensor_driver_t;

static sensor_driver_t drivers[MAX_DRIVERS];   // реєстр драйверів
static int driver_count = 0;

int  sensor_register(sensor_driver_t d);                 // ...25 рядків...
int  sensor_read_by_name(const char *n, float *out);     // ...пошук у реєстрі...
void sensor_set_calibration(const char *n, float o, float s);
void sensor_set_filter(const char *n, uint8_t order);
// ...ще сотня рядків під випадки, яких поки нема...
