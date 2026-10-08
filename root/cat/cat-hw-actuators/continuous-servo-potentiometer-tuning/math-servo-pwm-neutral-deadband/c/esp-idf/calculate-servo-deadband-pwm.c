#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define SERVO_PWM_NEUTRAL_US   1500
#define SERVO_PWM_MIN_US       1000
#define SERVO_PWM_MAX_US       2000

/**
 * @brief Обчислює скориговану тривалість ШІМ-імпульсу з урахуванням deadband та масштабування.
 * @param t_in_us Вхідна тривалість керуючого імпульсу (мкс).
 * @param deadband_half_us Половина ширини розрахованої зони нечутливості (мкс).
 * @return Скоригована тривалість імпульсу ШІМ для вихідного таймера (мкс).
 */
uint16_t calculate_servo_deadband_pwm(uint16_t t_in_us, uint16_t deadband_half_us) {
    if (t_in_us < SERVO_PWM_MIN_US) t_in_us = SERVO_PWM_MIN_US;
    if (t_in_us > SERVO_PWM_MAX_US) t_in_us = SERVO_PWM_MAX_US;

    int32_t offset = (int32_t)t_in_us - SERVO_PWM_NEUTRAL_US;

    if (abs(offset) <= (int32_t)deadband_half_us) {
        return SERVO_PWM_NEUTRAL_US;
    }

    int32_t max_span = SERVO_PWM_MAX_US - SERVO_PWM_NEUTRAL_US;
    int32_t active_span = max_span - (int32_t)deadband_half_us;
    int32_t scaled_offset;

    if (offset > 0) {
        scaled_offset = ((offset - (int32_t)deadband_half_us) * max_span) / active_span;
    } else {
        scaled_offset = ((offset + (int32_t)deadband_half_us) * max_span) / active_span;
    }

    return (uint16_t)(SERVO_PWM_NEUTRAL_US + scaled_offset);
}
