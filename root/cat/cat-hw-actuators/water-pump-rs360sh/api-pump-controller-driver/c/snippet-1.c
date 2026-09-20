// Опис параметрів приводу та гідравліки на C
typedef struct {
    uint8_t  gpio_pin;            // Вивід керування силовим ключем
    uint8_t  pwm_channel;         // Апаратний канал таймера ШІМ
    uint32_t pwm_freq_hz;         // Частота ШІМ (20 кГц для безшумної роботи)
    uint8_t  deadband_duty;       // Поріг рушання ротора (0..255)
    float    flow_rate_max_ml_s;  // Витрата при максимальній шпаруватості
    uint32_t max_continuous_ms;   // Захисний ліміт безперервної роботи
} pump_config_t;

typedef enum {
    PUMP_OK = 0,
    PUMP_ERR_INVALID_PARAM
} pump_err_t;

pump_err_t pump_init(const pump_config_t *config);
