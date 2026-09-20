typedef struct {
    uint16_t min_pulse_us;       // Апаратний мінімум імпульсу (наприклад, 540 мкс)
    uint16_t max_pulse_us;       // Апаратний максимум імпульсу (наприклад, 2460 мкс)
    uint16_t neutral_pulse_us;   // Імпульс центрального положення (зазвичай 1500 мкс)
    float min_angle_deg;         // Фізичний мінімальний кут (наприклад, 0.0f)
    float max_angle_deg;         // Фізичний максимальний кут (наприклад, 180.0f)
    float soft_limit_min_deg;    // Нижня програмна межа ходу
    float soft_limit_max_deg;    // Верхня програмна межа ходу
    void (*set_pwm_us)(uint16_t us); // Апаратний виклик генерації ШІМ
} servo_config_t;

typedef enum {
    SERVO_OK = 0,
    SERVO_ERR_INVALID_PARAM,
    SERVO_ERR_NO_PWM_CALLBACK
} servo_status_t;

typedef struct {
    servo_config_t cfg;
    float current_angle;
    bool is_attached;
} servo_t;

servo_status_t servo_init(servo_t *servo, const servo_config_t *config) {
    if (!servo || !config || !config->set_pwm_us) return SERVO_ERR_NO_PWM_CALLBACK;
    if (config->min_pulse_us >= config->max_pulse_us) return SERVO_ERR_INVALID_PARAM;
    if (config->neutral_pulse_us < config->min_pulse_us || config->neutral_pulse_us > config->max_pulse_us)
        return SERVO_ERR_INVALID_PARAM;
    if (config->soft_limit_min_deg < config->min_angle_deg || config->soft_limit_max_deg > config->max_angle_deg)
        return SERVO_ERR_INVALID_PARAM;
    if (config->soft_limit_min_deg >= config->soft_limit_max_deg) return SERVO_ERR_INVALID_PARAM;

    servo->cfg = *config;
    servo->current_angle = (config->soft_limit_min_deg + config->soft_limit_max_deg) * 0.5f;
    servo->is_attached = false;
    return SERVO_OK;
}
