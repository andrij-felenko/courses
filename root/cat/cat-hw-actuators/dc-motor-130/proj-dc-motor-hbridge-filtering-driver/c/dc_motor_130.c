/**
 * @file dc_motor_130.c
 * @brief Реалізація процедурного драйвера колекторного двигуна 130 для H-моста.
 */

#include "dc_motor_130.h"
#include <math.h>

#define FLOAT_EPSILON 1e-4f

/**
 * @brief Допоміжна функція обмеження значення з рухомою комою
 */
static inline float clamp_float(float val, float min, float max)
{
    if (val < min) {
        return min;
    }
    if (val > max) {
        return max;
    }
    return val;
}

/**
 * @brief Встановлення логічних рівнів виводів напівплечей H-моста для заданого стану
 *
 * Таблиця станів для стандартного інтегрального H-моста (наприклад, TB6612 / L298N / DRV8833):
 *  - COAST (Hi-Z):        IN1 = 0, IN2 = 0 (всі транзистори розімкнені)
 *  - DEAD-TIME:           IN1 = 0, IN2 = 0 (захисне зняття керування)
 *  - FORWARD (CW):        IN1 = 1, IN2 = 0 (діагональ Q1-Q4)
 *  - REVERSE (CCW):       IN1 = 0, IN2 = 1 (діагональ Q3-Q2)
 *  - DYNAMIC BRAKE:       IN1 = 1, IN2 = 1 (закорочування нижніх або верхніх ключів)
 */
static void apply_bridge_pins(dc_motor_t *motor, dc_motor_state_t state)
{
    if (motor == NULL || motor->config.pins_set == NULL) {
        return;
    }

    switch (state) {
    case DC_MOTOR_STATE_FORWARD:
        motor->config.pins_set(DC_MOTOR_PIN_HIGH, DC_MOTOR_PIN_LOW, motor->config.user_data);
        break;

    case DC_MOTOR_STATE_REVERSE:
        motor->config.pins_set(DC_MOTOR_PIN_LOW, DC_MOTOR_PIN_HIGH, motor->config.user_data);
        break;

    case DC_MOTOR_STATE_BRAKE:
        /* Закорочення клем двигуна для активного динамічного гасіння проти-ЕРС */
        motor->config.pins_set(DC_MOTOR_PIN_HIGH, DC_MOTOR_PIN_HIGH, motor->config.user_data);
        break;

    case DC_MOTOR_STATE_COAST:
    case DC_MOTOR_STATE_DEADTIME:
    default:
        /* Високоімпедансний стан Hi-Z: обидва входи притиснуті до нуля, всі ключі закриті */
        motor->config.pins_set(DC_MOTOR_PIN_LOW, DC_MOTOR_PIN_LOW, motor->config.user_data);
        break;
    }
}

/**
 * @brief Безпечний перехід у режим мертвого часу (dead-time)
 *
 * Негайно вимикає ШІМ, переводить виводи моста у нульовий безпечний рівень (Hi-Z)
 * та фіксує цільовий стан, до якого автомат перейде після завершення паузи dead-time.
 */
static void enter_deadtime(dc_motor_t *motor, dc_motor_state_t next_state)
{
    motor->target_state = next_state;
    motor->state = DC_MOTOR_STATE_DEADTIME;
    motor->deadtime_timer_us = 0;
    motor->current_pwm_duty = 0;

    /* Безпечне скидання силових ключів */
    apply_bridge_pins(motor, DC_MOTOR_STATE_DEADTIME);
    if (motor->config.pwm_set != NULL) {
        motor->config.pwm_set(0, motor->config.user_data);
    }
}

bool dc_motor_init(dc_motor_t *motor, const dc_motor_config_t *config)
{
    if (motor == NULL || config == NULL) {
        return false;
    }

    if (config->pins_set == NULL || config->pwm_set == NULL) {
        return false;
    }

    if (config->max_pwm_duty == 0) {
        return false;
    }

    if (config->accel_rate <= 0.0f || config->decel_rate <= 0.0f) {
        return false;
    }

    motor->config = *config;

    /* Застосування безпечних значень за замовчуванням, якщо не вказані */
    if (motor->config.deadtime_us == 0) {
        motor->config.deadtime_us = DC_MOTOR_130_DEFAULT_DEADTIME_US;
    }

    motor->target_speed = 0.0f;
    motor->current_speed = 0.0f;
    motor->current_pwm_duty = 0;
    motor->deadtime_timer_us = 0;

    /* Початковий безпечний стан: вільний вибіг або режим за замовчуванням */
    if (motor->config.default_stop_mode == DC_MOTOR_STOP_MODE_BRAKE) {
        motor->state = DC_MOTOR_STATE_BRAKE;
        apply_bridge_pins(motor, DC_MOTOR_STATE_BRAKE);
        motor->config.pwm_set(motor->config.max_pwm_duty, motor->config.user_data);
    } else {
        motor->state = DC_MOTOR_STATE_COAST;
        apply_bridge_pins(motor, DC_MOTOR_STATE_COAST);
        motor->config.pwm_set(0, motor->config.user_data);
    }

    motor->target_state = motor->state;
    motor->initialized = true;

    return true;
}

void dc_motor_set_speed(dc_motor_t *motor, float speed)
{
    if (motor == NULL || !motor->initialized) {
        return;
    }

    motor->target_speed = clamp_float(speed, -1.0f, 1.0f);
}

void dc_motor_set_speed_immediate(dc_motor_t *motor, float speed)
{
    if (motor == NULL || !motor->initialized) {
        return;
    }

    float clamped_speed = clamp_float(speed, -1.0f, 1.0f);
    motor->target_speed = clamped_speed;

    if (fabsf(clamped_speed) < FLOAT_EPSILON) {
        dc_motor_stop(motor);
        return;
    }

    dc_motor_state_t desired_state = (clamped_speed > 0.0f) ? DC_MOTOR_STATE_FORWARD : DC_MOTOR_STATE_REVERSE;

    /* Якщо поточний стан відрізняється від бажаного напрямку, обов'язково витримуємо dead-time */
    if (motor->state != desired_state) {
        motor->current_speed = 0.0f;
        enter_deadtime(motor, desired_state);
    } else {
        motor->current_speed = clamped_speed;
        uint32_t duty = (uint32_t)(fabsf(clamped_speed) * (float)motor->config.max_pwm_duty + 0.5f);
        if (duty > motor->config.max_pwm_duty) {
            duty = motor->config.max_pwm_duty;
        }
        motor->current_pwm_duty = duty;
        apply_bridge_pins(motor, motor->state);
        motor->config.pwm_set(duty, motor->config.user_data);
    }
}

void dc_motor_stop(dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return;
    }

    /* Плавне уповільнення до нуля через стандартний алгоритм рампи */
    motor->target_speed = 0.0f;
}

void dc_motor_coast(dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return;
    }

    motor->target_speed = 0.0f;
    motor->current_speed = 0.0f;
    motor->current_pwm_duty = 0;
    motor->state = DC_MOTOR_STATE_COAST;
    motor->target_state = DC_MOTOR_STATE_COAST;

    /* Зняття ШІМ та відкриття всіх ключів (Hi-Z) */
    apply_bridge_pins(motor, DC_MOTOR_STATE_COAST);
    if (motor->config.pwm_set != NULL) {
        motor->config.pwm_set(0, motor->config.user_data);
    }
}

void dc_motor_brake(dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return;
    }

    motor->target_speed = 0.0f;
    motor->current_speed = 0.0f;

    /*
     * Якщо двигун перебуває в активному обертанні (FORWARD або REVERSE),
     * для запобігання наскрізним струмам стійки обов'язково робимо паузу dead-time
     * перед закорочуванням клем на загальну шину!
     */
    if (motor->state == DC_MOTOR_STATE_FORWARD || motor->state == DC_MOTOR_STATE_REVERSE) {
        enter_deadtime(motor, DC_MOTOR_STATE_BRAKE);
    } else {
        motor->state = DC_MOTOR_STATE_BRAKE;
        motor->target_state = DC_MOTOR_STATE_BRAKE;
        motor->current_pwm_duty = motor->config.max_pwm_duty;

        apply_bridge_pins(motor, DC_MOTOR_STATE_BRAKE);
        if (motor->config.pwm_set != NULL) {
            motor->config.pwm_set(motor->config.max_pwm_duty, motor->config.user_data);
        }
    }
}

void dc_motor_emergency_stop(dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return;
    }

    /* Аварійне негайне зняття тяги та вмикання активного гальма */
    motor->target_speed = 0.0f;
    motor->current_speed = 0.0f;
    motor->state = DC_MOTOR_STATE_BRAKE;
    motor->target_state = DC_MOTOR_STATE_BRAKE;
    motor->current_pwm_duty = motor->config.max_pwm_duty;

    apply_bridge_pins(motor, DC_MOTOR_STATE_BRAKE);
    if (motor->config.pwm_set != NULL) {
        motor->config.pwm_set(motor->config.max_pwm_duty, motor->config.user_data);
    }
}

void dc_motor_update(dc_motor_t *motor, uint32_t dt_us)
{
    if (motor == NULL || !motor->initialized || dt_us == 0) {
        return;
    }

    float dt_s = (float)dt_us / 1000000.0f;

    /* ========================================================================
     * 1. ОБРОБКА ЗАХИСНОГО СТАНУ МЕРТВОГО ЧАСУ (DEAD-TIME)
     * ======================================================================== */
    if (motor->state == DC_MOTOR_STATE_DEADTIME) {
        motor->deadtime_timer_us += dt_us;

        /* Перевірка завершення захисної паузи */
        if (motor->deadtime_timer_us >= motor->config.deadtime_us) {
            /* Мертвий час витримано: перемикаємося у цільовий силовой стан */
            motor->state = motor->target_state;
            apply_bridge_pins(motor, motor->state);

            if (motor->state == DC_MOTOR_STATE_BRAKE) {
                motor->current_pwm_duty = motor->config.max_pwm_duty;
                motor->config.pwm_set(motor->config.max_pwm_duty, motor->config.user_data);
            } else if (motor->state == DC_MOTOR_STATE_COAST) {
                motor->current_pwm_duty = 0;
                motor->config.pwm_set(0, motor->config.user_data);
            } else {
                /* Для FORWARD або REVERSE швидкість стартує від 0 і нарощується рампою */
                motor->current_pwm_duty = 0;
                motor->config.pwm_set(0, motor->config.user_data);
            }
        }
        return;
    }

    /* ========================================================================
     * 2. ОБРОБКА СТАНІВ СПОКОЮ (COAST / BRAKE)
     * ======================================================================== */
    if (motor->state == DC_MOTOR_STATE_COAST || motor->state == DC_MOTOR_STATE_BRAKE) {
        /* Якщо надійшла ненульова цільова швидкість — ініціюємо запуск через dead-time */
        if (fabsf(motor->target_speed) > FLOAT_EPSILON) {
            dc_motor_state_t next = (motor->target_speed > 0.0f) ? DC_MOTOR_STATE_FORWARD : DC_MOTOR_STATE_REVERSE;
            motor->current_speed = 0.0f;
            enter_deadtime(motor, next);
        }
        return;
    }

    /* ========================================================================
     * 3. РУХ УПЕРЕД (FORWARD) ТА ЛІНІЙНИЙ РОЗГОН / УПОВІЛЬНЕННЯ
     * ======================================================================== */
    if (motor->state == DC_MOTOR_STATE_FORWARD) {
        /* Сценарій 3.1: Цільова швидкість у прямому напрямку (або зупинка) */
        if (motor->target_speed >= 0.0f) {
            if (motor->target_speed > motor->current_speed) {
                /* Плавний пуск (Soft-Start): лінійне нарощування шпаруватості ШІМ */
                float max_step = motor->config.accel_rate * dt_s;
                motor->current_speed += max_step;
                if (motor->current_speed > motor->target_speed) {
                    motor->current_speed = motor->target_speed;
                }
            } else if (motor->target_speed < motor->current_speed) {
                /* Кероване лінійне уповільнення (Deceleration) */
                float max_step = motor->config.decel_rate * dt_s;
                motor->current_speed -= max_step;
                if (motor->current_speed < motor->target_speed) {
                    motor->current_speed = motor->target_speed;
                }
            }

            /* Перевірка досягнення нульової швидкості (зупинка) */
            if (motor->current_speed <= FLOAT_EPSILON && motor->target_speed == 0.0f) {
                motor->current_speed = 0.0f;
                motor->current_pwm_duty = 0;

                if (motor->config.default_stop_mode == DC_MOTOR_STOP_MODE_BRAKE) {
                    enter_deadtime(motor, DC_MOTOR_STATE_BRAKE);
                } else {
                    motor->state = DC_MOTOR_STATE_COAST;
                    apply_bridge_pins(motor, DC_MOTOR_STATE_COAST);
                    motor->config.pwm_set(0, motor->config.user_data);
                }
                return;
            }

            /* Розрахунок та оновлення шпаруватості таймера ШІМ */
            uint32_t duty = (uint32_t)(motor->current_speed * (float)motor->config.max_pwm_duty + 0.5f);
            if (duty > motor->config.max_pwm_duty) {
                duty = motor->config.max_pwm_duty;
            }
            motor->current_pwm_duty = duty;
            motor->config.pwm_set(duty, motor->config.user_data);

        } else {
            /* Сценарій 3.2: Запит реверсу під час руху вперед!
             * Спочатку плавно гасимо швидкість вперед до нуля */
            float max_step = motor->config.decel_rate * dt_s;
            motor->current_speed -= max_step;

            if (motor->current_speed <= 0.0f) {
                /* Вал зупинився — безпечний перехід через нуль з обов'язковим dead-time! */
                motor->current_speed = 0.0f;
                enter_deadtime(motor, DC_MOTOR_STATE_REVERSE);
            } else {
                uint32_t duty = (uint32_t)(motor->current_speed * (float)motor->config.max_pwm_duty + 0.5f);
                if (duty > motor->config.max_pwm_duty) {
                    duty = motor->config.max_pwm_duty;
                }
                motor->current_pwm_duty = duty;
                motor->config.pwm_set(duty, motor->config.user_data);
            }
        }
        return;
    }

    /* ========================================================================
     * 4. ЗВОРОТНИЙ РУХ (REVERSE) ТА ЛІНІЙНИЙ РОЗГОН / УПОВІЛЬНЕННЯ
     * ======================================================================== */
    if (motor->state == DC_MOTOR_STATE_REVERSE) {
        /* Сценарій 4.1: Цільова швидкість у зворотному напрямку (або зупинка) */
        if (motor->target_speed <= 0.0f) {
            if (motor->target_speed < motor->current_speed) {
                /* Збільшення швидкості реверсу (за модулем) */
                float max_step = motor->config.accel_rate * dt_s;
                motor->current_speed -= max_step;
                if (motor->current_speed < motor->target_speed) {
                    motor->current_speed = motor->target_speed;
                }
            } else if (motor->target_speed > motor->current_speed) {
                /* Зменшення швидкості реверсу до нуля */
                float max_step = motor->config.decel_rate * dt_s;
                motor->current_speed += max_step;
                if (motor->current_speed > motor->target_speed) {
                    motor->current_speed = motor->target_speed;
                }
            }

            /* Перевірка досягнення нульової швидкості (зупинка) */
            if (motor->current_speed >= -FLOAT_EPSILON && motor->target_speed == 0.0f) {
                motor->current_speed = 0.0f;
                motor->current_pwm_duty = 0;

                if (motor->config.default_stop_mode == DC_MOTOR_STOP_MODE_BRAKE) {
                    enter_deadtime(motor, DC_MOTOR_STATE_BRAKE);
                } else {
                    motor->state = DC_MOTOR_STATE_COAST;
                    apply_bridge_pins(motor, DC_MOTOR_STATE_COAST);
                    motor->config.pwm_set(0, motor->config.user_data);
                }
                return;
            }

            /* Оновлення шпаруватості ШІМ для реверсу (за модулем) */
            uint32_t duty = (uint32_t)(fabsf(motor->current_speed) * (float)motor->config.max_pwm_duty + 0.5f);
            if (duty > motor->config.max_pwm_duty) {
                duty = motor->config.max_pwm_duty;
            }
            motor->current_pwm_duty = duty;
            motor->config.pwm_set(duty, motor->config.user_data);

        } else {
            /* Сценарій 4.2: Запит реверсу на прямий рух (перехід із від'ємної швидкості в додатну) */
            float max_step = motor->config.decel_rate * dt_s;
            motor->current_speed += max_step;

            if (motor->current_speed >= 0.0f) {
                /* Нульова точка: обов'язкова пауза dead-time перед комутацією протилежної діагоналі */
                motor->current_speed = 0.0f;
                enter_deadtime(motor, DC_MOTOR_STATE_FORWARD);
            } else {
                uint32_t duty = (uint32_t)(fabsf(motor->current_speed) * (float)motor->config.max_pwm_duty + 0.5f);
                if (duty > motor->config.max_pwm_duty) {
                    duty = motor->config.max_pwm_duty;
                }
                motor->current_pwm_duty = duty;
                motor->config.pwm_set(duty, motor->config.user_data);
            }
        }
        return;
    }
}

dc_motor_state_t dc_motor_get_state(const dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return DC_MOTOR_STATE_COAST;
    }
    return motor->state;
}

float dc_motor_get_current_speed(const dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return 0.0f;
    }
    return motor->current_speed;
}

float dc_motor_get_target_speed(const dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return 0.0f;
    }
    return motor->target_speed;
}

uint32_t dc_motor_get_pwm_duty(const dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return 0;
    }
    return motor->current_pwm_duty;
}

bool dc_motor_is_target_reached(const dc_motor_t *motor)
{
    if (motor == NULL || !motor->initialized) {
        return true;
    }
    return (fabsf(motor->current_speed - motor->target_speed) < FLOAT_EPSILON);
}

const char *dc_motor_state_to_str(dc_motor_state_t state)
{
    switch (state) {
    case DC_MOTOR_STATE_COAST:
        return "COAST (Hi-Z вибіг)";
    case DC_MOTOR_STATE_BRAKE:
        return "BRAKE (динамічне гальмо)";
    case DC_MOTOR_STATE_FORWARD:
        return "FORWARD (прямий хід)";
    case DC_MOTOR_STATE_REVERSE:
        return "REVERSE (зворотний хід)";
    case DC_MOTOR_STATE_DEADTIME:
        return "DEAD-TIME (пауза захисту)";
    default:
        return "НЕВІДОМИЙ СТАН";
    }
}
