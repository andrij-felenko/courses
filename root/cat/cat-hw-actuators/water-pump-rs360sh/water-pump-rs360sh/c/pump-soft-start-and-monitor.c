#include <stdint.h>
#include <stdbool.h>

#define PWM_DEAD_ZONE 60
#define PWM_TARGET    200
#define ADC_SHUNTPIN  0

#define CURRENT_DRY_RUN_RAW  150
#define CURRENT_STALL_RAW    800

void pump_soft_start_and_monitor(void) {
    for (uint8_t duty = PWM_DEAD_ZONE; duty <= PWM_TARGET; duty += 5) {
        set_pump_pwm(duty);
        delay_ms(20);
    }
    delay_ms(300);

    uint16_t current = read_adc_raw(ADC_SHUNTPIN);
    if (current < CURRENT_DRY_RUN_RAW || current > CURRENT_STALL_RAW) {
        set_pump_pwm(0);
    }
}
