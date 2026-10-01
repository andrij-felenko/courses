#include "servo_tester.h"

#define MIN_PULSE_US 1000
#define MAX_PULSE_US 2000
#define NEUTRAL_PULSE_US 1500
#define PWM_PERIOD_US 20000
#define SWEEP_STEP_US 10
#define SWEEP_INTERVAL_MS 15
#define DEBOUNCE_DELAY_MS 50

static uint16_t g_simulated_adc_raw = 512;
static uint16_t g_hardware_pwm_compare_us = NEUTRAL_PULSE_US;

void servo_tester_init(servo_tester_t *tester) {
    if (!tester) return;
    tester->mode = SERVO_MODE_MANUAL;
    tester->pulse_width_us = NEUTRAL_PULSE_US;
    tester->sweep_dir = 1;
    tester->last_sweep_ms = 0;
    tester->last_button_ms = 0;
    tester->last_button_state = false;
    tester->esc_calibrated = false;
}

void servo_tester_hw_init(void) {
    g_hardware_pwm_compare_us = NEUTRAL_PULSE_US;
}

void servo_tester_set_pulse_us(servo_tester_t *tester, uint16_t pulse_us) {
    if (!tester) return;
    
    if (pulse_us < MIN_PULSE_US) {
        pulse_us = MIN_PULSE_US;
    } else if (pulse_us > MAX_PULSE_US) {
        pulse_us = MAX_PULSE_US;
    }
    
    tester->pulse_width_us = pulse_us;
    g_hardware_pwm_compare_us = pulse_us;
}

uint16_t servo_tester_read_adc_pulse(void) {
    uint32_t pulse = MIN_PULSE_US + ((uint32_t)g_simulated_adc_raw * (MAX_PULSE_US - MIN_PULSE_US)) / 1023;
    return (uint16_t)pulse;
}

void servo_tester_next_mode(servo_tester_t *tester) {
    if (!tester) return;
    tester->mode = (servo_tester_mode_t)((tester->mode + 1) % 3);
    
    if (tester->mode == SERVO_MODE_NEUTRAL) {
        servo_tester_set_pulse_us(tester, NEUTRAL_PULSE_US);
    }
}

void servo_tester_update(servo_tester_t *tester, uint32_t current_ms, bool button_pressed) {
    if (!tester) return;

    if (button_pressed != tester->last_button_state) {
        tester->last_button_ms = current_ms;
        tester->last_button_state = button_pressed;
    }

    if (button_pressed && (current_ms - tester->last_button_ms >= DEBOUNCE_DELAY_MS)) {
        servo_tester_next_mode(tester);
        tester->last_button_ms = current_ms + 200; 
    }

    switch (tester->mode) {
        case SERVO_MODE_MANUAL: {
            uint16_t adc_pulse = servo_tester_read_adc_pulse();
            servo_tester_set_pulse_us(tester, adc_pulse);
            break;
        }
        case SERVO_MODE_NEUTRAL: {
            servo_tester_set_pulse_us(tester, NEUTRAL_PULSE_US);
            break;
        }
        case SERVO_MODE_SWEEP: {
            if (current_ms - tester->last_sweep_ms >= SWEEP_INTERVAL_MS) {
                tester->last_sweep_ms = current_ms;
                int32_t new_pulse = (int32_t)tester->pulse_width_us + (tester->sweep_dir * SWEEP_STEP_US);
                
                if (new_pulse >= MAX_PULSE_US) {
                    new_pulse = MAX_PULSE_US;
                    tester->sweep_dir = -1;
                } else if (new_pulse <= MIN_PULSE_US) {
                    new_pulse = MIN_PULSE_US;
                    tester->sweep_dir = 1;
                }
                
                servo_tester_set_pulse_us(tester, (uint16_t)new_pulse);
            }
            break;
        }
    }
}

void servo_tester_calibrate_esc(servo_tester_t *tester) {
    if (!tester) return;
    
    servo_tester_set_pulse_us(tester, MAX_PULSE_US);
    servo_tester_set_pulse_us(tester, MIN_PULSE_US);
    
    tester->esc_calibrated = true;
    tester->mode = SERVO_MODE_MANUAL;
}
