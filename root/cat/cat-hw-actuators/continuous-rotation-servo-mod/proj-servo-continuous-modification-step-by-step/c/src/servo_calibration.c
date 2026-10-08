#include "servo_calibration.h"
#include "servo_cr_pwm.h"
#include <stddef.h>

void servo_calibration_init_default(servo_calibration_params_t *params)
{
    if (params == NULL) {
        return;
    }
    params->trim_offset_us = 0;
    params->deadband_us = 20U;
    params->min_pulse_us = SERVO_CR_PULSE_MIN_US;
    params->max_pulse_us = SERVO_CR_PULSE_MAX_US;
}

int servo_calibration_set_trim(servo_calibration_params_t *params, int16_t trim_offset_us)
{
    if (params == NULL) {
        return -1;
    }
    if (trim_offset_us < SERVO_TRIM_MIN_US || trim_offset_us > SERVO_TRIM_MAX_US) {
        return -1;
    }
    params->trim_offset_us = trim_offset_us;
    return 0;
}

int servo_calibration_set_deadband(servo_calibration_params_t *params, uint16_t deadband_us)
{
    if (params == NULL) {
        return -1;
    }
    if (deadband_us > SERVO_DEADBAND_MAX_US) {
        return -1;
    }
    params->deadband_us = deadband_us;
    return 0;
}

uint16_t servo_calibration_apply(const servo_calibration_params_t *params, float requested_speed_pct)
{
    if (params == NULL) {
        return SERVO_CR_PULSE_NEUTRAL_US;
    }

    /* Обчислення фізичного нуля нейтралі з урахуванням апаратного триммінгу */
    int32_t calibrated_neutral = (int32_t)SERVO_CR_PULSE_NEUTRAL_US + (int32_t)params->trim_offset_us;

    /* Нормалізація вхідної швидкості [-100.0f, +100.0f] */
    if (requested_speed_pct < SERVO_CR_SPEED_MIN_PCT) {
        requested_speed_pct = SERVO_CR_SPEED_MIN_PCT;
    } else if (requested_speed_pct > SERVO_CR_SPEED_MAX_PCT) {
        requested_speed_pct = SERVO_CR_SPEED_MAX_PCT;
    }

    /* 
     * Розрахунок мінімального порогу швидкості, який відповідає мертвій зоні.
     * Якщо абсолютна величина швидкості занадто мала, видаємо нейтральний імпульс.
     */
    float deadband_speed_threshold = ((float)params->deadband_us / 500.0f) * 100.0f;

    if (requested_speed_pct > -deadband_speed_threshold && requested_speed_pct < deadband_speed_threshold) {
        /* Знаходження всередині зони нечутливості — примусова зупинка */
        return (uint16_t)calibrated_neutral;
    }

    int32_t pulse_result = calibrated_neutral;

    if (requested_speed_pct > 0.0f) {
        /*
         * Прямий хід: мапінг швидкості (від deadband_speed_threshold до 100%)
         * у діапазон імпульсу (від calibrated_neutral + deadband_us до max_pulse_us)
         */
        float active_span = 100.0f - deadband_speed_threshold;
        float normalized_active = (requested_speed_pct - deadband_speed_threshold) / (active_span > 0.001f ? active_span : 1.0f);
        
        int32_t min_active_pulse = calibrated_neutral + (int32_t)params->deadband_us;
        int32_t pulse_range = (int32_t)params->max_pulse_us - min_active_pulse;
        
        pulse_result = min_active_pulse + (int32_t)(normalized_active * (float)pulse_range + 0.5f);
    } else {
        /*
         * Реверс: мапінг швидкості (від -deadband_speed_threshold до -100%)
         * у діапазон імпульсу (від calibrated_neutral - deadband_us до min_pulse_us)
         */
        float active_span = 100.0f - deadband_speed_threshold;
        float normalized_active = (-requested_speed_pct - deadband_speed_threshold) / (active_span > 0.001f ? active_span : 1.0f);
        
        int32_t max_active_pulse = calibrated_neutral - (int32_t)params->deadband_us;
        int32_t pulse_range = max_active_pulse - (int32_t)params->min_pulse_us;
        
        pulse_result = max_active_pulse - (int32_t)(normalized_active * (float)pulse_range + 0.5f);
    }

    /* Захисне обмеження імпульсу в межах дозволеного діапазону */
    if (pulse_result < (int32_t)params->min_pulse_us) {
        pulse_result = (int32_t)params->min_pulse_us;
    } else if (pulse_result > (int32_t)params->max_pulse_us) {
        pulse_result = (int32_t)params->max_pulse_us;
    }

    return (uint16_t)pulse_result;
}

bool servo_calibration_is_in_deadband(const servo_calibration_params_t *params, uint16_t pulse_us)
{
    if (params == NULL) {
        return false;
    }

    int32_t calibrated_neutral = (int32_t)SERVO_CR_PULSE_NEUTRAL_US + (int32_t)params->trim_offset_us;
    int32_t deadband_low = calibrated_neutral - (int32_t)params->deadband_us;
    int32_t deadband_high = calibrated_neutral + (int32_t)params->deadband_us;

    return ((int32_t)pulse_us >= deadband_low && (int32_t)pulse_us <= deadband_high);
}
