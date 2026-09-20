#include "drv8833.h"
#include <stddef.h>

/**
 * @brief Допоміжна функція отримання конфігураційних вказівок для заданого мотора.
 */
static const drv8833_motor_config_t *get_motor_config(const drv8833_t *handle, drv8833_motor_id_t motor)
{
    return (motor == DRV8833_MOTOR_A) ? &handle->config.motor_a : &handle->config.motor_b;
}

/**
 * @brief Допоміжна функція отримання вказівника на стан мотора.
 */
static drv8833_motor_state_t *get_motor_state_ptr(drv8833_t *handle, drv8833_motor_id_t motor)
{
    return (motor == DRV8833_MOTOR_A) ? &handle->state_a : &handle->state_b;
}

drv8833_status_t drv8833_init(drv8833_t *handle, const drv8833_config_t *config)
{
    if (handle == NULL || config == NULL) {
        return DRV8833_ERROR_INVALID_PARAM;
    }
    if (config->gpio_write == NULL || config->pwm_set == NULL) {
        return DRV8833_ERROR_INVALID_PARAM;
    }

    handle->config = *config;
    handle->is_initialized = false;
    handle->is_sleeping = false;

    /* Скинути стан обох моторів у початковий (вільний вибіг) */
    handle->state_a.mode = DRV8833_MODE_COAST;
    handle->state_a.speed_percent = 0;
    handle->state_b.mode = DRV8833_MODE_COAST;
    handle->state_b.speed_percent = 0;

    /* Активувати мікросхему DRV8833 через вивід nSLEEP (високий рівень = робота) */
    if (handle->config.pin_sleep != DRV8833_PIN_UNUSED) {
        handle->config.gpio_write(handle->config.pin_sleep, true);
    }

    /* Встановити виходи у стан вільного вибігу при старті */
    handle->config.pwm_set(handle->config.motor_a.pwm_ch_in1, 0);
    handle->config.pwm_set(handle->config.motor_a.pwm_ch_in2, 0);
    handle->config.pwm_set(handle->config.motor_b.pwm_ch_in1, 0);
    handle->config.pwm_set(handle->config.motor_b.pwm_ch_in2, 0);

    handle->is_initialized = true;
    return DRV8833_OK;
}

drv8833_status_t drv8833_set_motor(drv8833_t *handle, drv8833_motor_id_t motor, drv8833_mode_t mode, uint8_t speed_percent)
{
    if (handle == NULL || !handle->is_initialized) {
        return DRV8833_ERROR_NOT_INITIALIZED;
    }
    if (motor != DRV8833_MOTOR_A && motor != DRV8833_MOTOR_B) {
        return DRV8833_ERROR_INVALID_PARAM;
    }
    if (speed_percent > 100) {
        return DRV8833_ERROR_INVALID_PARAM;
    }
    if (handle->is_sleeping) {
        /* У режимі сну команди руху відхиляються */
        return DRV8833_ERROR_INVALID_PARAM;
    }

    const drv8833_motor_config_t *cfg = get_motor_config(handle, motor);
    drv8833_motor_state_t *st = get_motor_state_ptr(handle, motor);

    switch (mode) {
    case DRV8833_MODE_COAST:
        /* Обидва входи на 0%: мости відкриті, вільний вибіг */
        handle->config.pwm_set(cfg->pwm_ch_in1, 0);
        handle->config.pwm_set(cfg->pwm_ch_in2, 0);
        st->speed_percent = 0;
        break;

    case DRV8833_MODE_FORWARD:
        /* IN1 подає ШІМ пропорційно швидкості, IN2 фіксовано на LOW */
        handle->config.pwm_set(cfg->pwm_ch_in1, speed_percent);
        handle->config.pwm_set(cfg->pwm_ch_in2, 0);
        st->speed_percent = speed_percent;
        break;

    case DRV8833_MODE_REVERSE:
        /* IN1 фіксовано на LOW, IN2 подає ШІМ пропорційно швидкості */
        handle->config.pwm_set(cfg->pwm_ch_in1, 0);
        handle->config.pwm_set(cfg->pwm_ch_in2, speed_percent);
        st->speed_percent = speed_percent;
        break;

    case DRV8833_MODE_BRAKE:
        /* Обидва входи на 100%: активне гальмування закорочуванням обмоток */
        handle->config.pwm_set(cfg->pwm_ch_in1, 100);
        handle->config.pwm_set(cfg->pwm_ch_in2, 100);
        st->speed_percent = 0;
        break;

    default:
        return DRV8833_ERROR_INVALID_PARAM;
    }

    st->mode = mode;
    return DRV8833_OK;
}

drv8833_status_t drv8833_set_speed(drv8833_t *handle, drv8833_motor_id_t motor, uint8_t speed_percent)
{
    if (handle == NULL || !handle->is_initialized) {
        return DRV8833_ERROR_NOT_INITIALIZED;
    }

    drv8833_motor_state_t *st = get_motor_state_ptr(handle, motor);
    drv8833_mode_t current_mode = st->mode;

    /* Якщо мотор був зупинений чи загальмований, за замовчуванням рухаємося вперед */
    if (current_mode == DRV8833_MODE_COAST || current_mode == DRV8833_MODE_BRAKE) {
        current_mode = DRV8833_MODE_FORWARD;
    }

    return drv8833_set_motor(handle, motor, current_mode, speed_percent);
}

drv8833_status_t drv8833_brake(drv8833_t *handle, drv8833_motor_id_t motor)
{
    return drv8833_set_motor(handle, motor, DRV8833_MODE_BRAKE, 0);
}

drv8833_status_t drv8833_coast(drv8833_t *handle, drv8833_motor_id_t motor)
{
    return drv8833_set_motor(handle, motor, DRV8833_MODE_COAST, 0);
}

drv8833_status_t drv8833_set_sleep(drv8833_t *handle, bool sleep_enable)
{
    if (handle == NULL || !handle->is_initialized) {
        return DRV8833_ERROR_NOT_INITIALIZED;
    }

    if (sleep_enable) {
        /* Перед входом у сон вимикаємо генерацію сигналів на обидва мотори */
        drv8833_coast(handle, DRV8833_MOTOR_A);
        drv8833_coast(handle, DRV8833_MOTOR_B);

        if (handle->config.pin_sleep != DRV8833_PIN_UNUSED) {
            handle->config.gpio_write(handle->config.pin_sleep, false); /* nSLEEP = LOW */
        }
        handle->is_sleeping = true;
    } else {
        if (handle->config.pin_sleep != DRV8833_PIN_UNUSED) {
            handle->config.gpio_write(handle->config.pin_sleep, true);  /* nSLEEP = HIGH */
        }
        handle->is_sleeping = false;
    }

    return DRV8833_OK;
}

drv8833_status_t drv8833_get_motor_state(const drv8833_t *handle, drv8833_motor_id_t motor, drv8833_motor_state_t *state)
{
    if (handle == NULL || !handle->is_initialized) {
        return DRV8833_ERROR_NOT_INITIALIZED;
    }
    if (state == NULL) {
        return DRV8833_ERROR_INVALID_PARAM;
    }
    if (motor != DRV8833_MOTOR_A && motor != DRV8833_MOTOR_B) {
        return DRV8833_ERROR_INVALID_PARAM;
    }

    *state = (motor == DRV8833_MOTOR_A) ? handle->state_a : handle->state_b;
    return DRV8833_OK;
}
