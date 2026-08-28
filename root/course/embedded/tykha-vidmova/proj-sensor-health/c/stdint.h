#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Бітові прапорці діагностичного стану сенсора */
typedef enum {
    SENSOR_HEALTH_OK               = 0x00,
    SENSOR_FAULT_OUT_OF_RANGE_LOW  = 0x01, /* Нижче мінімуму (обрив / 0 В) */
    SENSOR_FAULT_OUT_OF_RANGE_HIGH = 0x02, /* Вище максимуму (КЗ / Vdd) */
    SENSOR_FAULT_SLEW_RATE         = 0x04, /* Стрибок dY/dt вище ліміту */
    SENSOR_FAULT_ZERO_VARIANCE     = 0x08, /* Нульова дисперсія (завислий кристал) */
    SENSOR_FAULT_CROSS_CHECK       = 0x10  /* Розбіжність із кворумом або моделлю */
} sensor_health_flags_t;

/* Налаштування меж та чутливості діагностики */
typedef struct {
    float min_plausible;       /* Нижня фізична межа величини */
    float max_plausible;       /* Верхня фізична межа величини */
    float max_slew_rate;       /* Максимально допустима швидкість зміни (|Δy| / c) */
    float min_variance;        /* Поріг мертвого сенсора (мінімальна дисперсія) */
    uint32_t min_samples_var;  /* Кількість відліків для накопичення дисперсії */
} sensor_guard_config_t;

/* Стан накопичувача та алгоритму Уелфорда */
typedef struct {
    sensor_guard_config_t cfg;
    float last_value;
    uint32_t last_timestamp_ms;
    bool has_prev_sample;

    /* Змінні однопрохідного розрахунку середнього та дисперсії (Welford) */
    uint32_t sample_count;
    float mean;
    float m2;

    /* Поточний діагностичний статус */
    uint8_t flags;
} sensor_guard_t;

/* Результат мажоритарного голосування 2oo3 */
typedef struct {
    float voted_value;
    bool quorum_valid;
    uint8_t faulty_sensor_mask; /* Біти 0, 1, 2 показують несправний канал */
} quorum_result_t;

void sensor_guard_init(sensor_guard_t *guard, const sensor_guard_config_t *cfg);
uint8_t sensor_guard_update(sensor_guard_t *guard, float value, uint32_t timestamp_ms);
quorum_result_t sensor_guard_vote_2oo3(float s1, float s2, float s3, float max_allowed_spread);
