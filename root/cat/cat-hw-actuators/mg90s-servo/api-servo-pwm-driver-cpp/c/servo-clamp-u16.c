#include "servo_driver.h"
#include <math.h>

static inline uint16_t servo_clamp_u16(uint16_t val, uint16_t min_v, uint16_t max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

static inline float servo_clamp_float(float val, float min_v, float max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

servo_status_t servo_init(servo_t *servo,
                          void *timer_instance,
                          uint32_t channel,
                          const servo_hal_ops_t *ops,
                          uint16_t min_pulse_us,
                          uint16_t max_pulse_us,
                          float max_angle_deg) {
    if (servo == NULL || ops == NULL || ops->write_pulse == NULL || ops->set_enabled == NULL) {
        return SERVO_ERR_INVALID_ARG;
    }
    if (min_pulse_us >= max_pulse_us || max_angle_deg <= 0.0f) {
        return SERVO_ERR_OUT_OF_RANGE;
    }

    servo->timer_instance = timer_instance;
    servo->channel = channel;
    servo->hal_write_pulse = ops->write_pulse;
    servo->hal_set_pwm_enabled = ops->set_enabled;

    servo->min_pulse_us = min_pulse_us;
    servo->max_pulse_us = max_pulse_us;
    servo->max_angle_deg = max_angle_deg;

    servo->current_angle_deg = 0.0f;
    servo->target_angle_deg = 0.0f;
    servo->speed_deg_per_s = 180.0f; // Типова швидкість за замовчуванням
    servo->current_pulse_us = min_pulse_us;
    servo->is_attached = false;

    return SERVO_OK;
}

servo_status_t servo_attach(servo_t *servo) {
    if (servo == NULL) return SERVO_ERR_INVALID_ARG;
    if (servo->is_attached) return SERVO_OK;

    // Встановлюємо безпечну тривалість імпульсу перед активацією виводу
    servo_write_angle(servo, servo->current_angle_deg);
    servo->hal_set_pwm_enabled(servo->timer_instance, servo->channel, true);
    servo->is_attached = true;
    return SERVO_OK;
}

servo_status_t servo_detach(servo_t *servo) {
    if (servo == NULL) return SERVO_ERR_INVALID_ARG;
    if (!servo->is_attached) return SERVO_OK;

    servo->hal_set_pwm_enabled(servo->timer_instance, servo->channel, false);
    servo->is_attached = false;
    return SERVO_OK;
}

servo_status_t servo_write_microseconds(servo_t *servo, uint16_t pulse_us) {
    if (servo == NULL) return SERVO_ERR_INVALID_ARG;
    if (!servo->is_attached) return SERVO_ERR_NOT_ATTACHED;

    uint16_t safe_pulse = servo_clamp_u16(pulse_us, servo->min_pulse_us, servo->max_pulse_us);
    servo->hal_write_pulse(servo->timer_instance, servo->channel, safe_pulse);
    servo->current_pulse_us = safe_pulse;

    // Оновлюємо поточний кут для збереження взаємної узгодженості
    float pulse_range = (float)(servo->max_pulse_us - servo->min_pulse_us);
    servo->current_angle_deg = ((float)(safe_pulse - servo->min_pulse_us) * servo->max_angle_deg) / pulse_range;

    return SERVO_OK;
}

servo_status_t servo_write_angle(servo_t *servo, float angle_deg) {
    if (servo == NULL) return SERVO_ERR_INVALID_ARG;
    if (!servo->is_attached) return SERVO_ERR_NOT_ATTACHED;

    float safe_angle = servo_clamp_float(angle_deg, 0.0f, servo->max_angle_deg);
    float pulse_range = (float)(servo->max_pulse_us - servo->min_pulse_us);
    
    uint16_t pulse_us = servo->min_pulse_us + (uint16_t)(((safe_angle * pulse_range) / servo->max_angle_deg) + 0.5f);
    
    servo->hal_write_pulse(servo->timer_instance, servo->channel, pulse_us);
    servo->current_pulse_us = pulse_us;
    servo->current_angle_deg = safe_angle;

    return SERVO_OK;
}

servo_status_t servo_set_target_angle(servo_t *servo, float target_angle_deg, float speed_deg_per_s) {
    if (servo == NULL) return SERVO_ERR_INVALID_ARG;
    if (speed_deg_per_s <= 0.0f) return SERVO_ERR_OUT_OF_RANGE;

    servo->target_angle_deg = servo_clamp_float(target_angle_deg, 0.0f, servo->max_angle_deg);
    servo->speed_deg_per_s = speed_deg_per_s;
    return SERVO_OK;
}

bool servo_update(servo_t *servo, uint32_t dt_ms) {
    if (servo == NULL || !servo->is_attached) return true;

    float error = servo->target_angle_deg - servo->current_angle_deg;
    if (fabsf(error) < 0.05f) {
        servo->current_angle_deg = servo->target_angle_deg;
        servo_write_angle(servo, servo->current_angle_deg);
        return true;
    }

    float max_step = (servo->speed_deg_per_s * (float)dt_ms) / 1000.0f;
    if (fabsf(error) <= max_step) {
        servo->current_angle_deg = servo->target_angle_deg;
    } else {
        servo->current_angle_deg += (error > 0.0f) ? max_step : -max_step;
    }

    servo_write_angle(servo, servo->current_angle_deg);
    return false;
}
