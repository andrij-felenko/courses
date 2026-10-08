#include "dc_motor_130.h"
#include <stdio.h>
#include <stddef.h>

/**
 * @file dc_motor_130.c
 * @brief Реалізація процедурного C-драйвера колекторного двигуна типорозміру 130.
 * 
 * Містить алгоритми безпечної перекомутації силового H-моста, програмну реалізацію
 * захисного Dead Time для відсікання наскрізних струмів, керування коефіцієнтом
 * заповнення ШІМ та логіку гальмування (вибіг COAST vs активний BRAKE).
 */

/**
 * @brief Внутрішня функція безпечного відключення обох плечей H-моста
 *        та виконання захисного Dead Time затримки.
 * 
 * @param motor Вказівник на дескриптор мотора.
 */
static void apply_dead_time(dc_motor_t *motor) {
    /* 1. Миттєво скидаємо ШІМ-сигнал на виході Enable у 0 */
    mcu_pwm_set_duty_cycle(motor->config.pwm_channel, 0);

    /* 2. Переводимо обоє плечей керування IN1 та IN2 в низький логічний рівень */
    mcu_gpio_write(motor->config.pin_in1, MCU_GPIO_LOW);
    mcu_gpio_write(motor->config.pin_in2, MCU_GPIO_LOW);

    /* 3. Оновлюємо внутрішній стан драйвера */
    motor->state = DC_MOTOR_STATE_DEAD_TIME;

    /* 4. Витримуємо точну програмну мікросекундну затримку (Dead Time) */
    if (motor->config.dead_time_us > 0) {
        mcu_delay_us(motor->config.dead_time_us);
    }
}

dc_motor_err_t dc_motor_init(dc_motor_t *motor, const dc_motor_config_t *config) {
    if (!motor || !config) {
        return DC_MOTOR_ERR_NULL_PTR;
    }

    /* Зберігаємо конфігурацію у структурі мотора */
    motor->config = *config;
    motor->direction = DC_MOTOR_DIR_STOP;
    motor->stop_mode = config->default_stop;
    motor->state = DC_MOTOR_STATE_IDLE;
    motor->duty_cycle = 0;
    motor->is_initialized = false;

    /* Налаштовуємо виводи GPIO IN1 та IN2 у режим цифрового виходу */
    if (mcu_gpio_init_output(config->pin_in1) != MCU_OK ||
        mcu_gpio_init_output(config->pin_in2) != MCU_OK) {
        return DC_MOTOR_ERR_INVALID_PARAM;
    }

    /* Налаштовуємо апаратний ШІМ-таймер */
    mcu_pwm_config_t pwm_cfg = {
        .frequency_hz = config->pwm_frequency_hz,
        .pwm_channel = config->pwm_channel
    };

    if (mcu_pwm_init(&pwm_cfg) != MCU_OK) {
        return DC_MOTOR_ERR_INVALID_PARAM;
    }

    /* Переводимо H-міст у безпечний початковий стан (обоє виводів у 0, ШІМ = 0) */
    mcu_gpio_write(config->pin_in1, MCU_GPIO_LOW);
    mcu_gpio_write(config->pin_in2, MCU_GPIO_LOW);
    mcu_pwm_set_duty_cycle(config->pwm_channel, 0);

    motor->is_initialized = true;
    return DC_MOTOR_OK;
}

dc_motor_err_t dc_motor_set_speed(dc_motor_t *motor, uint8_t duty_percent) {
    if (!motor) {
        return DC_MOTOR_ERR_NULL_PTR;
    }
    if (!motor->is_initialized) {
        return DC_MOTOR_ERR_NOT_INIT;
    }
    if (duty_percent > 100) {
        return DC_MOTOR_ERR_INVALID_DUTY;
    }

    motor->duty_cycle = duty_percent;

    /* Передаємо значення заповнення в регістр порівняння таймера лише якщо двигун у русі */
    if (motor->direction != DC_MOTOR_DIR_STOP) {
        if (mcu_pwm_set_duty_cycle(motor->config.pwm_channel, duty_percent) != MCU_OK) {
            return DC_MOTOR_ERR_INVALID_PARAM;
        }
    }

    return DC_MOTOR_OK;
}

dc_motor_err_t dc_motor_set_direction(dc_motor_t *motor, dc_motor_direction_t dir) {
    if (!motor) {
        return DC_MOTOR_ERR_NULL_PTR;
    }
    if (!motor->is_initialized) {
        return DC_MOTOR_ERR_NOT_INIT;
    }
    if (dir != DC_MOTOR_DIR_STOP && dir != DC_MOTOR_DIR_FORWARD && dir != DC_MOTOR_DIR_REVERSE) {
        return DC_MOTOR_ERR_INVALID_PARAM;
    }

    /* Якщо напрямок не змінюється, нічого не робимо */
    if (motor->direction == dir) {
        return DC_MOTOR_OK;
    }

    /*
     * КРИТИЧНА СЕКЦІЯ БЕЗПЕКИ (Dead Time):
     * Якщо двигун змінює напрямок руху (наприклад, з FORWARD на REVERSE),
     * обов'язково розмикаємо всі транзистори H-моста та чекаємо dead_time_us.
     * Це запобігає стану Shoot-Through, коли верхнє та нижнє плече моста
     * на коротку мить відкриті одночасно, створюючи коротке замикання джерела живлення!
     */
    if (motor->direction != DC_MOTOR_DIR_STOP && dir != DC_MOTOR_DIR_STOP) {
        apply_dead_time(motor);
    }

    motor->direction = dir;

    switch (dir) {
        case DC_MOTOR_DIR_FORWARD:
            /* Таблиця істинності H-моста для ПРЯМОГО руху: IN1 = HIGH, IN2 = LOW */
            mcu_gpio_write(motor->config.pin_in1, MCU_GPIO_HIGH);
            mcu_gpio_write(motor->config.pin_in2, MCU_GPIO_LOW);
            motor->state = DC_MOTOR_STATE_RUNNING;
            mcu_pwm_set_duty_cycle(motor->config.pwm_channel, motor->duty_cycle);
            break;

        case DC_MOTOR_DIR_REVERSE:
            /* Таблиця істинності H-моста для РЕВЕРСУ: IN1 = LOW, IN2 = HIGH */
            mcu_gpio_write(motor->config.pin_in1, MCU_GPIO_LOW);
            mcu_gpio_write(motor->config.pin_in2, MCU_GPIO_HIGH);
            motor->state = DC_MOTOR_STATE_RUNNING;
            mcu_pwm_set_duty_cycle(motor->config.pwm_channel, motor->duty_cycle);
            break;

        case DC_MOTOR_DIR_STOP:
        default:
            dc_motor_stop(motor, motor->stop_mode);
            break;
    }

    return DC_MOTOR_OK;
}

dc_motor_err_t dc_motor_drive(dc_motor_t *motor, dc_motor_direction_t dir, uint8_t duty_percent) {
    if (!motor) {
        return DC_MOTOR_ERR_NULL_PTR;
    }
    if (!motor->is_initialized) {
        return DC_MOTOR_ERR_NOT_INIT;
    }
    if (duty_percent > 100) {
        return DC_MOTOR_ERR_INVALID_DUTY;
    }

    /* Спочатку зберігаємо бажаний коефіцієнт заповнення ШІМ */
    motor->duty_cycle = duty_percent;

    /* Викликаємо безпечне встановлення напрямку з перевіркою Dead Time */
    return dc_motor_set_direction(motor, dir);
}

dc_motor_err_t dc_motor_stop(dc_motor_t *motor, dc_motor_stop_mode_t mode) {
    if (!motor) {
        return DC_MOTOR_ERR_NULL_PTR;
    }
    if (!motor->is_initialized) {
        return DC_MOTOR_ERR_NOT_INIT;
    }

    motor->direction = DC_MOTOR_DIR_STOP;
    motor->stop_mode = mode;

    if (mode == DC_MOTOR_STOP_COAST) {
        /*
         * РЕЖИМ 1: Інерційний вибіг (COAST / Fast Decay)
         * - Сигнали IN1 = LOW, IN2 = LOW
         * - ШІМ EN = 0%
         * Вал двигуна обертається вільно за рахунок власної інерції.
         * Струм обмоток загасає через зворотні діоди H-моста.
         */
        mcu_pwm_set_duty_cycle(motor->config.pwm_channel, 0);
        mcu_gpio_write(motor->config.pin_in1, MCU_GPIO_LOW);
        mcu_gpio_write(motor->config.pin_in2, MCU_GPIO_LOW);
        motor->state = DC_MOTOR_STATE_IDLE;

    } else if (mode == DC_MOTOR_STOP_BRAKE) {
        /*
         * РЕЖИМ 2: Активне гальмування (BRAKE / Slow Decay)
         * - Сигнали IN1 = HIGH, IN2 = HIGH (або IN1=LOW, IN2=LOW при активному EN=100%)
         * - Замикання обох виводів мотора на спільну шину (GND або VCC).
         * Проти-ЕРС обертання ротора створює замкнений струмовий контур,
         * що викликає швидке електромагнітне гальмування вала.
         */
        motor->state = DC_MOTOR_STATE_BRAKING;
        mcu_gpio_write(motor->config.pin_in1, MCU_GPIO_HIGH);
        mcu_gpio_write(motor->config.pin_in2, MCU_GPIO_HIGH);
        mcu_pwm_set_duty_cycle(motor->config.pwm_channel, 100);
    }

    return DC_MOTOR_OK;
}

dc_motor_err_t dc_motor_emergency_stop(dc_motor_t *motor) {
    if (!motor) {
        return DC_MOTOR_ERR_NULL_PTR;
    }

    /* Негайне відключення периферії незалежно від стану ініціалізації */
    mcu_pwm_stop(motor->config.pwm_channel);
    mcu_gpio_write(motor->config.pin_in1, MCU_GPIO_LOW);
    mcu_gpio_write(motor->config.pin_in2, MCU_GPIO_LOW);

    motor->direction = DC_MOTOR_DIR_STOP;
    motor->duty_cycle = 0;
    motor->state = DC_MOTOR_STATE_IDLE;

    return DC_MOTOR_OK;
}

const char* dc_motor_err_to_string(dc_motor_err_t err) {
    switch (err) {
        case DC_MOTOR_OK:
            return "Успішно (OK)";
        case DC_MOTOR_ERR_NULL_PTR:
            return "Передано нульовий вказівник";
        case DC_MOTOR_ERR_INVALID_DUTY:
            return "Некоректне значення ШІМ (перевищує 100%)";
        case DC_MOTOR_ERR_INVALID_PARAM:
            return "Некоректні параметри конфігурації або периферії";
        case DC_MOTOR_ERR_NOT_INIT:
            return "Драйвер двигуна не ініціалізовано";
        default:
            return "Невідома помилка";
    }
}

const char* dc_motor_dir_to_string(dc_motor_direction_t dir) {
    switch (dir) {
        case DC_MOTOR_DIR_STOP:
            return "ЗУПИНЕНИЙ";
        case DC_MOTOR_DIR_FORWARD:
            return "ПРЯМИЙ (FORWARD)";
        case DC_MOTOR_DIR_REVERSE:
            return "РЕВЕРС (REVERSE)";
        default:
            return "НЕВІДОМИЙ";
    }
}

const char* dc_motor_stop_mode_to_string(dc_motor_stop_mode_t mode) {
    switch (mode) {
        case DC_MOTOR_STOP_COAST:
            return "ІНЕРЦІЙНИЙ ВИБІГ (COAST)";
        case DC_MOTOR_STOP_BRAKE:
            return "АКТИВНЕ ГАЛЬМУВАННЯ (BRAKE)";
        default:
            return "НЕВІДОМИЙ";
    }
}
