#include "driver/mcpwm_prelude.h"
#include "esp_err.h"

typedef struct {
    mcpwm_cmpr_handle_t comparator;
    uint32_t neutral_us;  // Калібрована нейтраль у мікросекундах
    uint32_t deadband_us; // Напівширина мертвої зони
} continuous_servo_t;

esp_err_t continuous_servo_set_speed(continuous_servo_t *servo, int speed_percent) {
    if (speed_percent < -100) speed_percent = -100;
    if (speed_percent > 100) speed_percent = 100;

    uint32_t pulse_us = servo->neutral_us;

    if (speed_percent > 0) {
        pulse_us = servo->neutral_us + servo->deadband_us +
                   (speed_percent * (500 - servo->deadband_us)) / 100;
    } else if (speed_percent < 0) {
        pulse_us = servo->neutral_us - servo->deadband_us -
                   ((-speed_percent) * (500 - servo->deadband_us)) / 100;
    }

    return mcpwm_comparator_set_compare_value(servo->comparator, pulse_us);
}
