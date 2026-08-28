#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Структура конфігурації та калібрування сервоприводу
 */
typedef struct {
    uint16_t min_pulse_us;   /* Мінімальна тривалість імпульсу (типово 1000 мкс) */
    uint16_t max_pulse_us;   /* Максимальна тривалість імпульсу (типово 2000 мкс) */
    float min_angle_deg;     /* Мінімальний кут у градусах (типово 0.0 або -90.0) */
    float max_angle_deg;     /* Максимальний кут у градусах (типово 180.0 або +90.0) */
    int16_t trim_us;         /* Зсув нейтралі (калібрувальний трим) */
    bool inverted;           /* Прапорець реверсу напрямку обертання */
} servo_config_t;

/**
 * @brief Вказівник на апаратну функцію запису значення в регістр порівняння таймера
 */
typedef void (*servo_pwm_write_fn)(void *hw_context, uint16_t pulse_us);

/**
 * @brief Дескриптор екземпляра сервоприводу
 */
typedef struct {
    servo_config_t config;
    servo_pwm_write_fn write_fn;
    void *hw_context;
    uint16_t current_pulse_us;
    float current_angle_deg;
    bool is_active;
} servo_handle_t;

/**
 * @brief Допоміжна функція обмеження величини в межах [min, max]
 */
static inline float servo_clampf(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

/**
 * @brief Допоміжна функція обмеження uint16_t в межах [min, max]
 */
static inline uint16_t servo_clampu16(uint16_t val, uint16_t min, uint16_t max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

/**
 * @brief Ініціалізація дескриптора сервоприводу
 */
bool servo_init(servo_handle_t *handle, const servo_config_t *config,
                servo_pwm_write_fn write_fn, void *hw_context) {
    if (!handle || !config || !write_fn) {
        return false;
    }
    if (config->min_pulse_us >= config->max_pulse_us ||
        config->min_angle_deg >= config->max_angle_deg) {
        return false;
    }

    handle->config = *config;
    handle->write_fn = write_fn;
    handle->hw_context = hw_context;
    handle->current_pulse_us = (config->min_pulse_us + config->max_pulse_us) / 2;
    handle->current_angle_deg = (config->min_angle_deg + config->max_angle_deg) / 2.0f;
    handle->is_active = false;

    return true;
}

/**
 * @brief Встановлення позиції сервоприводу безпосередньо в мікросекундах
 */
bool servo_write_microseconds(servo_handle_t *handle, uint16_t pulse_us) {
    if (!handle || !handle->write_fn) {
        return false;
    }

    /* Врахування калібрувального зсуву trim */
    int32_t target_us = (int32_t)pulse_us + handle->config.trim_us;

    /* Жорстке апаратне обмеження безпечними межами */
    uint16_t clamped_us = servo_clampu16((uint16_t)target_us,
                                         handle->config.min_pulse_us,
                                         handle->config.max_pulse_us);

    handle->write_fn(handle->hw_context, clamped_us);
    handle->current_pulse_us = clamped_us;

    /* Зворотний перерахунок встановлених мікросекунд у градуси */
    float span_us = (float)(handle->config.max_pulse_us - handle->config.min_pulse_us);
    float span_deg = handle->config.max_angle_deg - handle->config.min_angle_deg;
    float norm = (float)(clamped_us - handle->config.min_pulse_us) / span_us;

    if (handle->config.inverted) {
        norm = 1.0f - norm;
    }

    handle->current_angle_deg = handle->config.min_angle_deg + norm * span_deg;
    handle->is_active = true;
    return true;
}

/**
 * @brief Встановлення цільового кута в градусах
 */
bool servo_write_angle(servo_handle_t *handle, float angle_deg) {
    if (!handle) {
        return false;
    }

    float clamped_deg = servo_clampf(angle_deg,
                                     handle->config.min_angle_deg,
                                     handle->config.max_angle_deg);

    float span_deg = handle->config.max_angle_deg - handle->config.min_angle_deg;
    float norm = (clamped_deg - handle->config.min_angle_deg) / span_deg;

    if (handle->config.inverted) {
        norm = 1.0f - norm;
    }

    float span_us = (float)(handle->config.max_pulse_us - handle->config.min_pulse_us);
    uint16_t target_us = (uint16_t)(handle->config.min_pulse_us + norm * span_us + 0.5f);

    return servo_write_microseconds(handle, target_us);
}

/**
 * @brief Отримання поточного встановленого кута
 */
float servo_get_current_angle(const servo_handle_t *handle) {
    return handle ? handle->current_angle_deg : 0.0f;
}
