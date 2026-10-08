#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    uint8_t gpio_num;
    int16_t offset_us;
    uint16_t deadband_us;
    float current_pulse_us;
    float target_pulse_us;
    float max_ramp_step_us;
} continuous_servo_c_driver_t;

void continuous_servo_c_init(continuous_servo_c_driver_t* drv, uint8_t gpio) {
    drv->gpio_num = gpio;
    drv->offset_us = 0;
    drv->deadband_us = 12;
    drv->current_pulse_us = 1500.0f;
    drv->target_pulse_us = 1500.0f;
    drv->max_ramp_step_us = 25.0f;
}

void continuous_servo_c_set_speed(continuous_servo_c_driver_t* drv, float speed) {
    if (speed > 1.0f) speed = 1.0f;
    if (speed < -1.0f) speed = -1.0f;

    float abs_s = fabsf(speed);
    float db_norm = (float)drv->deadband_us / 500.0f;
    float neutral = 1500.0f + drv->offset_us;

    if (abs_s <= db_norm) {
        drv->target_pulse_us = neutral;
        return;
    }

    float scaled = (abs_s - db_norm) / (1.0f - db_norm);
    if (speed < 0.0f) scaled = -scaled;

    drv->target_pulse_us = neutral + (scaled * 500.0f);
}

uint32_t continuous_servo_c_update(continuous_servo_c_driver_t* drv) {
    float diff = drv->target_pulse_us - drv->current_pulse_us;
    if (fabsf(diff) <= drv->max_ramp_step_us) {
        drv->current_pulse_us = drv->target_pulse_us;
    } else {
        drv->current_pulse_us += (diff > 0.0f) ? drv->max_ramp_step_us : -drv->max_ramp_step_us;
    }

    uint32_t out_us = (uint32_t)lroundf(drv->current_pulse_us);
    if (out_us < 500) out_us = 500;
    if (out_us > 2500) out_us = 2500;
    
    return out_us;
}
