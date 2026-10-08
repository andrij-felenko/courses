#include "driver/mcpwm.h"
#include "soc/mcpwm_periph.h"

typedef struct {
    mcpwm_unit_t unit;
    mcpwm_timer_t timer;
    mcpwm_io_signals_t signal;
    uint16_t neutral_us;
    uint16_t delta_us;
} continuous_servo_t;

void continuous_servo_init(continuous_servo_t *servo, int gpio_pin) {
    mcpwm_gpio_init(servo->unit, servo->signal, gpio_pin);
    mcpwm_config_t pwm_config = {
        .frequency = 50, // 50 Гц (період 20 мс)
        .cmpr_a = 0,
        .counter_mode = MCPWM_UP_COUNTER,
        .duty_mode = MCPWM_DUTY_MODE_0
    };
    mcpwm_init(servo->unit, servo->timer, &pwm_config);
}

void continuous_servo_set_speed(continuous_servo_t *servo, int8_t speed_percent) {
    if (speed_percent > 100) speed_percent = 100;
    if (speed_percent < -100) speed_percent = -100;

    uint32_t pulse_us = servo->neutral_us + ((int32_t)speed_percent * servo->delta_us) / 100;
    mcpwm_set_us(servo->unit, servo->timer, MCPWM_OPR_A, pulse_us);
}
