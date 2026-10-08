#include "towerpro_servo.h"
#include <stddef.h>

servo_profile_t towerpro_servo_get_profile(servo_model_t model)
{
    servo_profile_t profile;

    switch (model) {
        case SERVO_MODEL_SG90:
            profile.model = SERVO_MODEL_SG90;
            profile.model_name = "Tower Pro SG90 (Plastic)";
            profile.min_pulse_us = 500U;
            profile.max_pulse_us = 2400U;
            profile.max_angle_deg = 180.0f;
            profile.stall_current_limit_ma = 500.0f;
            profile.stall_timeout_ms = 400U;
            break;

        case SERVO_MODEL_SG92R:
            profile.model = SERVO_MODEL_SG92R;
            profile.model_name = "Tower Pro SG92R (Carbon)";
            profile.min_pulse_us = 500U;
            profile.max_pulse_us = 2450U;
            profile.max_angle_deg = 180.0f;
            profile.stall_current_limit_ma = 600.0f;
            profile.stall_timeout_ms = 400U;
            break;

        case SERVO_MODEL_MG90S:
            profile.model = SERVO_MODEL_MG90S;
            profile.model_name = "Tower Pro MG90S (Metal)";
            profile.min_pulse_us = 500U;
            profile.max_pulse_us = 2500U;
            profile.max_angle_deg = 180.0f;
            profile.stall_current_limit_ma = 750.0f;
            profile.stall_timeout_ms = 500U;
            break;

        case SERVO_MODEL_MG90D:
            profile.model = SERVO_MODEL_MG90D;
            profile.model_name = "Tower Pro MG90D (Digital Metal)";
            profile.min_pulse_us = 500U;
            profile.max_pulse_us = 2500U;
            profile.max_angle_deg = 180.0f;
            profile.stall_current_limit_ma = 900.0f;
            profile.stall_timeout_ms = 500U;
            break;

        default:
            profile.model = SERVO_MODEL_SG90;
            profile.model_name = "Tower Pro Generic SG90";
            profile.min_pulse_us = 500U;
            profile.max_pulse_us = 2400U;
            profile.max_angle_deg = 180.0f;
            profile.stall_current_limit_ma = 500.0f;
            profile.stall_timeout_ms = 400U;
            break;
    }

    return profile;
}

int towerpro_servo_init(towerpro_servo_t *servo, const servo_config_t *config)
{
    if (servo == NULL || config == NULL) {
        return -1;
    }
    if (config->pwm == NULL || config->adc == NULL) {
        return -1;
    }

    servo->config = *config;
    servo->profile = towerpro_servo_get_profile(config->model);
    servo->target_angle_deg = 90.0f;
    servo->current_angle_deg = 90.0f;
    servo->status = SERVO_STATUS_OK;
    servo->stall_start_time_ms = 0U;
    servo->is_stalled = false;

    /* Встановлення сервоприводу в нейтральну позицію (90 градусів) */
    return towerpro_servo_set_angle(servo, 90.0f);
}

int towerpro_servo_set_angle(towerpro_servo_t *servo, float angle_deg)
{
    if (servo == NULL) {
        return -1;
    }

    /* Якщо сервопривод у стані заклинювання, нові команди позиціювання блокуються */
    if (servo->is_stalled) {
        return -1;
    }

    /* Обмеження кута у допустимих межах моделі */
    if (angle_deg < 0.0f) {
        angle_deg = 0.0f;
    } else if (angle_deg > servo->profile.max_angle_deg) {
        angle_deg = servo->profile.max_angle_deg;
    }

    servo->target_angle_deg = angle_deg;

    /* Перерахунок кута у тривалість ШІМ-імпульсу */
    float span_pulse = (float)(servo->profile.max_pulse_us - servo->profile.min_pulse_us);
    float pulse_exact = (float)servo->profile.min_pulse_us + (angle_deg / servo->profile.max_angle_deg) * span_pulse;
    uint16_t pulse_us = (uint16_t)(pulse_exact + 0.5f);

    int res = pwm_driver_set_pulse_us(servo->config.pwm, pulse_us);
    if (res == 0) {
        servo->current_angle_deg = angle_deg;
    }

    return res;
}

int towerpro_servo_process(towerpro_servo_t *servo, uint16_t raw_adc_sample, uint32_t current_time_ms)
{
    if (servo == NULL || servo->config.adc == NULL || servo->config.pwm == NULL) {
        return -1;
    }

    /* Додавання вибірки до струмового сенсора */
    adc_sensor_push_sample(servo->config.adc, raw_adc_sample, current_time_ms);

    /* Обчислення поточного RMS-струму */
    float rms_ma = adc_sensor_calculate_rms(servo->config.adc);

    /* Якщо сервопривод вже вимкнено через аварію */
    if (servo->is_stalled) {
        return -1;
    }

    /* Перевірка перевищення порогового RMS-струму заклинювання */
    if (rms_ma >= servo->profile.stall_current_limit_ma) {
        if (servo->stall_start_time_ms == 0U) {
            servo->stall_start_time_ms = current_time_ms;
        } else if ((current_time_ms - servo->stall_start_time_ms) >= servo->profile.stall_timeout_ms) {
            /* Перевищення тривалості порогу заклинювання — аварійне вимкнення */
            servo->is_stalled = true;
            servo->status = SERVO_STATUS_STALLED;

            /* Негайно відключаємо ШІМ для зняття напруги з мотора */
            pwm_driver_detach(servo->config.pwm);

            /* Виклик аварійного callback-обробника, якщо зачіплено */
            if (servo->config.stall_cb != NULL) {
                servo->config.stall_cb(servo->config.user_data, servo->profile.model, rms_ma);
            }
            return -1;
        }
    } else {
        /* Струм у межах норми — скидаємо таймер заклинювання */
        servo->stall_start_time_ms = 0U;
        if (servo->status != SERVO_STATUS_STALLED) {
            servo->status = SERVO_STATUS_OK;
        }
    }

    return 0;
}

int towerpro_servo_reset_fault(towerpro_servo_t *servo)
{
    if (servo == NULL || servo->config.pwm == NULL || servo->config.adc == NULL) {
        return -1;
    }

    servo->is_stalled = false;
    servo->stall_start_time_ms = 0U;
    servo->status = SERVO_STATUS_OK;

    /* Очищаємо струмовий буфер для запобігання хибному відключенню при повторному старті */
    adc_sensor_reset_buffer(servo->config.adc);

    /* Відновлюємо ШІМ-сигнал */
    int res = pwm_driver_attach(servo->config.pwm);
    if (res == 0) {
        towerpro_servo_set_angle(servo, servo->current_angle_deg);
    }

    return res;
}

float towerpro_servo_get_current_rms(const towerpro_servo_t *servo)
{
    if (servo == NULL || servo->config.adc == NULL) {
        return 0.0f;
    }
    return servo->config.adc->last_rms_ma;
}

servo_status_t towerpro_servo_get_status(const towerpro_servo_t *servo)
{
    if (servo == NULL) {
        return SERVO_STATUS_ERROR;
    }
    return servo->status;
}
