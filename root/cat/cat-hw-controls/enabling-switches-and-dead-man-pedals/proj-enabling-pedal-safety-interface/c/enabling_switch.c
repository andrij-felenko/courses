/**
 * @file enabling_switch.c
 * @brief Реалізація завадостійкого драйвера трипозиційного пристрою дозволу.
 */

#include "enabling_switch.h"
#include <stddef.h>

void enabling_switch_init(EnablingSwitch *sw, EnablingSwitchConfig config) {
    if (!sw) return;
    
    sw->config = config;
    sw->current_state = ENABLING_STATE_RELEASED;
    
    sw->ch1_debounced = false;
    sw->ch2_debounced = false;
    
    sw->ch1_raw_last = false;
    sw->ch2_raw_last = false;
    
    sw->ch1_last_change_ms = 0;
    sw->ch2_last_change_ms = 0;
    
    sw->discrepancy_start_ms = 0;
    sw->discrepancy_active = false;
    
    sw->requires_reset = false;
    sw->cross_fault_detected = false;
}

static void debounce_channel(bool raw_in, bool *debounced_out, bool *raw_last, 
                             uint32_t *last_change_ms, uint32_t current_ms, uint32_t debounce_time) {
    if (raw_in != *raw_last) {
        *raw_last = raw_in;
        *last_change_ms = current_ms;
    } else {
        if ((current_ms - *last_change_ms) >= debounce_time) {
            *debounced_out = raw_in;
        }
    }
}

EnablingState enabling_switch_update(EnablingSwitch *sw, bool ch1_raw, bool ch2_raw, 
                                     uint32_t current_time_ms, 
                                     bool (*test_pulse_fn)(uint8_t channel)) {
    if (!sw) return ENABLING_STATE_FAULT;

    /* 1. Тестування короткого замикання каналів імпульсним контролем */
    if (sw->config.enable_pulse_test && test_pulse_fn) {
        bool ch1_fault = test_pulse_fn(1);
        bool ch2_fault = test_pulse_fn(2);
        if (ch1_fault || ch2_fault) {
            sw->cross_fault_detected = true;
            sw->current_state = ENABLING_STATE_FAULT;
            sw->requires_reset = true;
            return sw->current_state;
        }
    }

    /* 2. Фільтрація брязкіту контактів для кожного каналу окремо */
    debounce_channel(ch1_raw, &sw->ch1_debounced, &sw->ch1_raw_last, 
                     &sw->ch1_last_change_ms, current_time_ms, sw->config.debounce_ms);
    debounce_channel(ch2_raw, &sw->ch2_debounced, &sw->ch2_raw_last, 
                     &sw->ch2_last_change_ms, current_time_ms, sw->config.debounce_ms);

    /* 3. Перевірка часового розсуву (discrepancy) між каналами */
    if (sw->ch1_debounced != sw->ch2_debounced) {
        if (!sw->discrepancy_active) {
            sw->discrepancy_active = true;
            sw->discrepancy_start_ms = current_time_ms;
        } else if ((current_time_ms - sw->discrepancy_start_ms) >= sw->config.discrepancy_timeout_ms) {
            sw->current_state = ENABLING_STATE_FAULT;
            sw->requires_reset = true;
            return sw->current_state;
        }
    } else {
        sw->discrepancy_active = false;
    }

    /* Якщо зафіксовано апаратну помилку або очікується скидання Reset */
    if (sw->cross_fault_detected) {
        sw->current_state = ENABLING_STATE_FAULT;
        return sw->current_state;
    }

    /* 4. Кінцевий автомат станів (FSM) */
    if (!sw->ch1_debounced && !sw->ch2_debounced) {
        /* Обидва канали вказують на Положення 1 (Відпущено) */
        if (sw->requires_reset) {
            /* При відпущенні в нуль знімаємо вимогу скидання */
            sw->requires_reset = false;
        }
        sw->current_state = ENABLING_STATE_RELEASED;
    } else if (sw->ch1_debounced && sw->ch2_debounced) {
        /* Обидва канали замкнені */
        if (sw->requires_reset) {
            /* Заборона активації без попереднього повернення в нуль */
            sw->current_state = ENABLING_STATE_FAULT;
        } else {
            sw->current_state = ENABLING_STATE_ACTIVE;
        }
    } else {
        /* Перехідний стан або розсинхронізація у межах таймауту */
        if (sw->current_state == ENABLING_STATE_ACTIVE && sw->requires_reset) {
            sw->current_state = ENABLING_STATE_FAULT;
        }
    }

    return sw->current_state;
}

void enabling_switch_reset(EnablingSwitch *sw) {
    if (!sw) return;
    if (sw->current_state == ENABLING_STATE_RELEASED) {
        sw->cross_fault_detected = false;
        sw->requires_reset = false;
        sw->discrepancy_active = false;
    }
}

const char* enabling_switch_state_to_str(EnablingState state) {
    switch (state) {
        case ENABLING_STATE_RELEASED: return "ВІДПУЩЕНО (RELEASED)";
        case ENABLING_STATE_ACTIVE:   return "РОБОЧИЙ ДОЗВІЛ (ACTIVE)";
        case ENABLING_STATE_PANIC:    return "ПАНІЧНИЙ НАТИСК (PANIC)";
        case ENABLING_STATE_FAULT:    return "АВАРІЯ / ПОМИЛКА (FAULT)";
        default:                      return "НЕВІДОМИЙ СТАН";
    }
}
