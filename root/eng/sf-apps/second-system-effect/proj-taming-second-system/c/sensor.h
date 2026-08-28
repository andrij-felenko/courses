// --- sensor.h: "гнучкий" драйвер під один реальний давач ---
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_DRIVERS   8      // "раптом буде вісім давачів"

typedef struct {
    const char *name;                       // ім'я для пошуку в реєстрі
    int  (*read_raw)(void *ctx, int32_t *out);  // вказівник на функцію читання
    void  *ctx;                             // контекст конкретного давача
    float  offset_cal;      // калібрування зсуву — "раптом знадобиться"
    float  scale_cal;       // калібрування масштабу — теж про запас
    uint16_t sample_rate_hz;// налаштовна частота — "а раптом"
    uint8_t  filter_order;  // порядок ковзного середнього — "на майбутнє"
    bool     enable_crc;    // перевірка цілісності по шині — "про всяк"
    int32_t  hist[8];       // буфер під фільтр — вісім відліків на кожен давач
    uint8_t  hist_pos;      // курсор кільцевого буфера
} sensor_driver_t;

static sensor_driver_t g_drivers[MAX_DRIVERS];
static uint8_t         g_driver_count;

int   sensor_register(const sensor_driver_t *d);
int   sensor_read_by_name(const char *name, float *celsius);
void  sensor_set_calibration(const char *name, float off, float scale);
void  sensor_set_filter(const char *name, uint8_t order);
