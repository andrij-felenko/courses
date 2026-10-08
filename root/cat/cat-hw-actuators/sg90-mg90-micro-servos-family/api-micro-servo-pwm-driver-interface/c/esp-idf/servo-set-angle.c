// C (ESP-IDF / Embedded C) - Перевірка меж та функція detach
#include <stdbool.h>

typedef enum {
    SERVO_OK = 0,
    SERVO_ERR_OUT_OF_BOUNDS = -3,
    SERVO_ERR_NOT_INITIALIZED = -4
} servo_status_t;

// Встановлення кута з обмеженням та обробкою помилок
servo_status_t servo_set_angle(servo_t *handle, float angle) {
    if (!handle || !handle->is_initialized) {
        return SERVO_ERR_NOT_INITIALIZED;
    }

    servo_status_t status = SERVO_OK;
    float safe_angle = angle;

    // Перевірка та обмеження (clamping) кута
    if (angle < handle->config.angle_min) {
        safe_angle = handle->config.angle_min;
        status = SERVO_ERR_OUT_OF_BOUNDS;
    } else if (angle > handle->config.angle_max) {
        safe_angle = handle->config.angle_max;
        status = SERVO_ERR_OUT_OF_BOUNDS;
    }

    // Перетворення кута в мікросекунди
    float span_us = handle->config.us_max - handle->config.us_min;
    float span_ang = handle->config.angle_max - handle->config.angle_min;
    uint16_t us = handle->config.us_min + (uint16_t)((safe_angle - handle->config.angle_min) * span_us / span_ang);

    handle->current_us = us + handle->config.trim_offset_us;
    // Оновлення регістра порівняння апаратного таймера
    // hal_pwm_set_duty_us(handle->config.gpio_pin, handle->current_us);

    return status;
}

// Відключення ШІМ-сигналу для економії енергії
void servo_detach(servo_t *handle) {
    if (handle && handle->is_initialized) {
        // Зупинка генерації ШІМ-сигналу на фізичному піні
        // hal_pwm_stop(handle->config.gpio_pin);
    }
}
