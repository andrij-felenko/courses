// C (ESP-IDF / Generic Embedded C)
#include <stdint.h>
#include <stdbool.h>

// Коди результату виконання операцій драйвера
typedef enum {
    SERVO_OK = 0,
    SERVO_ERR_INVALID_ARG = -1,
    SERVO_ERR_HW_INIT_FAIL = -2
} servo_err_t;

// Структура конфігурації екземпляра сервоприводу
typedef struct {
    uint8_t gpio_pin;         // Номер виводу GPIO
    uint16_t us_min;          // Мінімальна тривалість імпульсу (мкс)
    uint16_t us_max;          // Максимальна тривалість імпульсу (мкс)
    float angle_min;          // Мінімальний кут (град)
    float angle_max;          // Максимальний кут (град)
    int16_t trim_offset_us;   // Калібрувальний зсув (мкс)
} servo_config_t;

// Дескриптор драйвера сервоприводу
typedef struct {
    servo_config_t config;
    bool is_initialized;
    uint16_t current_us;
} servo_t;

// Функція ініціалізації драйвера
servo_err_t servo_init(servo_t *handle, const servo_config_t *config) {
    if (handle == NULL || config == NULL) {
        return SERVO_ERR_INVALID_ARG;
    }
    // Захисна перевірка допустимості часових меж
    if (config->us_min >= config->us_max || config->us_min < 400 || config->us_max > 2600) {
        return SERVO_ERR_INVALID_ARG;
    }
    if (config->angle_min >= config->angle_max) {
        return SERVO_ERR_INVALID_ARG;
    }

    handle->config = *config;
    // Обчислення початкового нейтрального імпульсу (середина діапазону)
    uint16_t neutral_us = config->us_min + (config->us_max - config->us_min) / 2;
    handle->current_us = neutral_us + config->trim_offset_us;

    // Апаратна ініціалізація таймера/PWM каналу (псевдокод периферії)
    // hal_pwm_init_50hz(config->gpio_pin, handle->current_us);

    handle->is_initialized = true;
    return SERVO_OK;
}
