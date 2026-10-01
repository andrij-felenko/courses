#include "servo_tester.h"
#include <stddef.h>

void servo_tester_init(servo_tester_t *tester) {
    if (tester == NULL) {
        return;
    }
    tester->mode = SERVO_MODE_NEUTRAL;
    tester->current_pulse_us = SERVO_PWM_NEUTRAL_US;
    tester->sweep_dir = 1;
    tester->last_sweep_ms = 0;
    tester->last_button_state = false;
    tester->button_debounce_ms = 0;
    tester->calib_state = ESC_CALIB_IDLE;
    tester->calib_timer_ms = 0;
}

uint16_t servo_tester_adc_to_pulse(uint16_t adc_val) {
    if (adc_val > SERVO_ADC_MAX_VALUE) {
        adc_val = SERVO_ADC_MAX_VALUE;
    }
    /* Масштабування діапазону [0..4095] у [1000..2000] мкс */
    uint32_t pulse = SERVO_PWM_MIN_US + (((uint32_t)adc_val * (SERVO_PWM_MAX_US - SERVO_PWM_MIN_US)) / SERVO_ADC_MAX_VALUE);
    return (uint16_t)pulse;
}

void servo_tester_set_mode(servo_tester_t *tester, servo_mode_t mode) {
    if (tester == NULL) {
        return;
    }
    tester->mode = mode;
    if (mode == SERVO_MODE_NEUTRAL) {
        tester->current_pulse_us = SERVO_PWM_NEUTRAL_US;
    } else if (mode == SERVO_MODE_AUTO_SWEEP) {
        tester->sweep_dir = 1;
    }
}

void servo_tester_update_manual(servo_tester_t *tester, uint16_t adc_val) {
    if (tester == NULL || tester->mode != SERVO_MODE_MANUAL) {
        return;
    }
    /* Якщо проводиться калібрування ESC, ручне оновлення блокується */
    if (tester->calib_state != ESC_CALIB_IDLE) {
        return;
    }
    tester->current_pulse_us = servo_tester_adc_to_pulse(adc_val);
}

void servo_tester_update_sweep(servo_tester_t *tester, uint32_t current_ms) {
    if (tester == NULL || tester->mode != SERVO_MODE_AUTO_SWEEP) {
        return;
    }
    if (tester->calib_state != ESC_CALIB_IDLE) {
        return;
    }

    /* Перевірка інтервалу автосканування */
    if (current_ms - tester->last_sweep_ms >= SERVO_SWEEP_INTERVAL_MS) {
        tester->last_sweep_ms = current_ms;

        if (tester->sweep_dir > 0) {
            if (tester->current_pulse_us + SERVO_SWEEP_STEP_US >= SERVO_PWM_MAX_US) {
                tester->current_pulse_us = SERVO_PWM_MAX_US;
                tester->sweep_dir = -1;
            } else {
                tester->current_pulse_us += SERVO_SWEEP_STEP_US;
            }
        } else {
            if (tester->current_pulse_us <= SERVO_PWM_MIN_US + SERVO_SWEEP_STEP_US) {
                tester->current_pulse_us = SERVO_PWM_MIN_US;
                tester->sweep_dir = 1;
            } else {
                tester->current_pulse_us -= SERVO_SWEEP_STEP_US;
            }
        }
    }
}

void servo_tester_process_button(servo_tester_t *tester, bool raw_button_state, uint32_t current_ms) {
    if (tester == NULL) {
        return;
    }

    /* Фільтрація антидребезгу кнопки */
    if (raw_button_state != tester->last_button_state) {
        if (current_ms - tester->button_debounce_ms >= SERVO_DEBOUNCE_MS) {
            tester->button_debounce_ms = current_ms;
            tester->last_button_state = raw_button_state;

            /* Подія натискання кнопки (Front edge) */
            if (raw_button_state) {
                servo_mode_t next_mode = (servo_mode_t)((tester->mode + 1) % 3);
                servo_tester_set_mode(tester, next_mode);
            }
        }
    }
}

void servo_tester_start_esc_calibration(servo_tester_t *tester, uint32_t current_ms) {
    if (tester == NULL) {
        return;
    }
    tester->calib_state = ESC_CALIB_MAX_THROTTLE;
    tester->calib_timer_ms = current_ms;
    tester->current_pulse_us = SERVO_PWM_MAX_US; /* Подача максимального газу (2000 мкс) */
}

void servo_tester_update_esc_calibration(servo_tester_t *tester, uint32_t current_ms) {
    if (tester == NULL || tester->calib_state == ESC_CALIB_IDLE) {
        return;
    }

    switch (tester->calib_state) {
        case ESC_CALIB_MAX_THROTTLE:
            /* Подача 100% газу протягом 3000 мс для фіксації максимуму регулятором */
            tester->current_pulse_us = SERVO_PWM_MAX_US;
            if (current_ms - tester->calib_timer_ms >= 3000U) {
                tester->calib_state = ESC_CALIB_MIN_THROTTLE;
                tester->calib_timer_ms = current_ms;
                tester->current_pulse_us = SERVO_PWM_MIN_US; /* Подача мінімального газу (1000 мкс) */
            }
            break;

        case ESC_CALIB_MIN_THROTTLE:
            /* Подача 0% газу протягом 3000 мс для фіксації нуля та завершення армування */
            tester->current_pulse_us = SERVO_PWM_MIN_US;
            if (current_ms - tester->calib_timer_ms >= 3000U) {
                tester->calib_state = ESC_CALIB_COMPLETED;
                tester->calib_timer_ms = current_ms;
            }
            break;

        case ESC_CALIB_COMPLETED:
            /* Перехід у безпечний режим нейтралі після завершення калібрування */
            tester->calib_state = ESC_CALIB_IDLE;
            servo_tester_set_mode(tester, SERVO_MODE_NEUTRAL);
            break;

        default:
            tester->calib_state = ESC_CALIB_IDLE;
            break;
    }
}
