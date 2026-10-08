#include "mcu_pwm_gpio.h"
#include <stdio.h>
#include <stdbool.h>

/**
 * @file mcu_pwm_gpio.c
 * @brief Реалізація низькорівневого керування периферією мікроконтролера (GPIO, ШІМ-таймер, затримки).
 */

#define MCU_SYSTEM_CLOCK_HZ 72000000UL  /* Імітація системної частоти тактування 72 МГц */

/* Внутрішній стан симульованого таймера ШІМ */
typedef struct {
    bool is_active;
    uint32_t frequency_hz;
    uint32_t prescaler;
    uint32_t arr_period;
    uint32_t current_ccr;
    uint8_t duty_percent;
} mcu_simulated_timer_t;

static mcu_simulated_timer_t s_pwm_timer = {0};
static mcu_gpio_state_t s_gpio_states[32] = {MCU_GPIO_LOW};
static bool s_gpio_configured[32] = {false};

mcu_err_t mcu_gpio_init_output(uint8_t pin) {
    if (pin >= 32) {
        return MCU_ERR_INVALID_ARG;
    }
    s_gpio_configured[pin] = true;
    s_gpio_states[pin] = MCU_GPIO_LOW;
    return MCU_OK;
}

mcu_err_t mcu_gpio_write(uint8_t pin, mcu_gpio_state_t state) {
    if (pin >= 32 || !s_gpio_configured[pin]) {
        return MCU_ERR_INVALID_ARG;
    }
    s_gpio_states[pin] = state;
    return MCU_OK;
}

mcu_err_t mcu_gpio_read(uint8_t pin, mcu_gpio_state_t *out_state) {
    if (pin >= 32 || !s_gpio_configured[pin] || !out_state) {
        return MCU_ERR_INVALID_ARG;
    }
    *out_state = s_gpio_states[pin];
    return MCU_OK;
}

mcu_err_t mcu_pwm_init(mcu_pwm_config_t *config) {
    if (!config || config->frequency_hz == 0 || config->pwm_channel == 0) {
        return MCU_ERR_INVALID_ARG;
    }

    /*
     * Математика конфігурування ШІМ-таймера:
     * F_pwm = SystemCoreClock / ((PSC + 1) * (ARR + 1))
     * Для забезпечення високої точності ШІМ (0..100%) фіксуємо ARR = 999 (період 1000 відліків).
     * Дільник PSC обчислюється як: PSC = (SystemCoreClock / (F_pwm * (ARR + 1))) - 1
     */
    uint32_t target_arr = 999;
    uint32_t psc_val = (MCU_SYSTEM_CLOCK_HZ / (config->frequency_hz * (target_arr + 1))) - 1;

    config->prescaler = psc_val;
    config->auto_reload_arr = target_arr;

    s_pwm_timer.is_active = true;
    s_pwm_timer.frequency_hz = config->frequency_hz;
    s_pwm_timer.prescaler = psc_val;
    s_pwm_timer.arr_period = target_arr;
    s_pwm_timer.current_ccr = 0;
    s_pwm_timer.duty_percent = 0;

    return MCU_OK;
}

mcu_err_t mcu_pwm_set_duty_cycle(uint8_t channel, uint8_t duty_percent) {
    if (channel == 0 || duty_percent > 100 || !s_pwm_timer.is_active) {
        return MCU_ERR_INVALID_ARG;
    }

    /* Обчислення значення регістру CCR: CCR = ((ARR + 1) * duty_percent) / 100 */
    uint32_t ccr_val = ((s_pwm_timer.arr_period + 1) * duty_percent) / 100;
    s_pwm_timer.current_ccr = ccr_val;
    s_pwm_timer.duty_percent = duty_percent;

    return MCU_OK;
}

mcu_err_t mcu_pwm_set_ccr_value(uint8_t channel, uint32_t ccr_val) {
    if (channel == 0 || !s_pwm_timer.is_active || ccr_val > (s_pwm_timer.arr_period + 1)) {
        return MCU_ERR_INVALID_ARG;
    }

    s_pwm_timer.current_ccr = ccr_val;
    s_pwm_timer.duty_percent = (uint8_t)((ccr_val * 100) / (s_pwm_timer.arr_period + 1));

    return MCU_OK;
}

mcu_err_t mcu_pwm_stop(uint8_t channel) {
    if (channel == 0 || !s_pwm_timer.is_active) {
        return MCU_ERR_INVALID_ARG;
    }

    s_pwm_timer.current_ccr = 0;
    s_pwm_timer.duty_percent = 0;

    return MCU_OK;
}

void mcu_delay_us(uint32_t us) {
    /* Симуляція мікросекундної затримки */
    (void)us;
}

void mcu_delay_ms(uint32_t ms) {
    /* Симуляція мілісекундної затримки */
    (void)ms;
}
