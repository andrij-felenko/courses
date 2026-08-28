#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Бітова маска помилок здоров'я сенсора */
typedef enum {
    SENSOR_OK                  = 0x00,
    SENSOR_ERR_RANGE_LOW       = 0x01, /* Нижче фізичного мінімуму (обрив / 0 В) */
    SENSOR_ERR_RANGE_HIGH      = 0x02, /* Вище фізичного максимуму (КЗ / Vdd) */
    SENSOR_ERR_SLEW_RATE       = 0x04, /* Перевищено ліміт похідної |dY/dt| */
    SENSOR_ERR_ZERO_VARIANCE   = 0x08, /* Дисперсія = 0 (завислий цифровий регістр) */
    SENSOR_ERR_CROSS_CHECK     = 0x10  /* Розбіжність із перехресною моделлю */
} sensor_error_t;

/* Параметри конфігурації для конкретного типу давача */
typedef struct {
    float min_valid;          /* Нижня фізична межа */
    float max_valid;          /* Верхня фізична межа */
    float max_gradient_per_s; /* Максимальна швидкість наростання в одиницях/с */
    float min_noise_variance; /* Поріг шуму (якщо менше — давач мертвий) */
    uint32_t variance_window; /* Кількість відліків для розрахунку Уелфорда */
} sensor_guard_cfg_t;

/* Робочий контекст (стан) одного сенсорного каналу */
typedef struct {
    sensor_guard_cfg_t cfg;
    float prev_val;
    uint32_t prev_ts_ms;
    bool has_history;

    /* Стан накопичувача Уелфорда */
    uint32_t count;
    float mean;
    float m2;

    uint8_t status_flags;     /* Поточна бітова маска помилок */
} sensor_guard_t;

void sensor_guard_init(sensor_guard_t *g, const sensor_guard_cfg_t *cfg);
uint8_t sensor_guard_process(sensor_guard_t *g, float sample, uint32_t now_ms);
