typedef enum {
    MOTOR_OK = 0,
    MOTOR_ERR_INVALID_ARG,
    MOTOR_ERR_PWM_INIT
} motor_status_t;

typedef struct {
    uint8_t pin_pwm;        // Канал таймера ШІМ
    uint8_t pin_dir1;       // Цифровий вивід напрямку 1
    uint8_t pin_dir2;       // Цифровий вивід напрямку 2
    uint8_t pin_current;    // Канал АЦП датчика струму
    uint32_t pwm_freq_hz;   // Частота ШІМ, типово 20000..25000 Гц
} motor_config_t;

motor_status_t motor_init(motor_t *dev, const motor_config_t *cfg);
