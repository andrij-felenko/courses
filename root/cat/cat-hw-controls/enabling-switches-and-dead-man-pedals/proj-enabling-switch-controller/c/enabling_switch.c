#include "enabling_switch.h"

void EnablingSwitch_Init(EnablingSwitch_t *sw, const EnablingSwitchConfig_t *config) {
    if (!sw || !config) return;

    sw->raw_ch1 = false;
    sw->raw_ch2 = false;
    sw->debounced_ch1 = CONTACT_OPEN;
    sw->debounced_ch2 = CONTACT_OPEN;
    sw->ch1_debounce_timer = 0;
    sw->ch2_debounce_timer = 0;
    sw->discrepancy_active = false;
    sw->discrepancy_timer = 0;
    sw->current_state = ENABLING_STATE_RELEASED;
    sw->config = *config;
}

EnablingState_t EnablingSwitch_Update(EnablingSwitch_t *sw, bool ch1_raw, bool ch2_raw, uint32_t delta_ms) {
    if (!sw) return ENABLING_STATE_FAULT;

    // Збереження сирих сигналів
    sw->raw_ch1 = ch1_raw;
    sw->raw_ch2 = ch2_raw;

    // 1. Цифровий симетричний фільтр антидребезгу для Каналу 1
    ContactState_t raw_state_ch1 = ch1_raw ? CONTACT_CLOSED : CONTACT_OPEN;
    if (raw_state_ch1 != sw->debounced_ch1) {
        sw->ch1_debounce_timer += delta_ms;
        if (sw->ch1_debounce_timer >= sw->config.debounce_time_ms) {
            sw->debounced_ch1 = raw_state_ch1;
            sw->ch1_debounce_timer = 0;
        }
    } else {
        sw->ch1_debounce_timer = 0;
    }

    // 2. Цифровий симетричний фільтр антидребезгу для Каналу 2
    ContactState_t raw_state_ch2 = ch2_raw ? CONTACT_CLOSED : CONTACT_OPEN;
    if (raw_state_ch2 != sw->debounced_ch2) {
        sw->ch2_debounce_timer += delta_ms;
        if (sw->ch2_debounce_timer >= sw->config.debounce_time_ms) {
            sw->debounced_ch2 = raw_state_ch2;
            sw->ch2_debounce_timer = 0;
        }
    } else {
        sw->ch2_debounce_timer = 0;
    }

    // Якщо FSM перебуває в стані аварійної відмови, вихід залишається заблокованим до скидання
    if (sw->current_state == ENABLING_STATE_FAULT) {
        return ENABLING_STATE_FAULT;
    }

    // 3. Моніторинг розсинхронізму каналів (ISO 13849 Discrepancy Monitoring)
    if (sw->debounced_ch1 != sw->debounced_ch2) {
        if (!sw->discrepancy_active) {
            sw->discrepancy_active = true;
            sw->discrepancy_timer = 0;
        } else {
            sw->discrepancy_timer += delta_ms;
            if (sw->discrepancy_timer > sw->config.discrepancy_time_ms) {
                // Часове вікно вичерпано — канали неузгоджені (обрив або коротке замикання)
                sw->current_state = ENABLING_STATE_FAULT;
                return ENABLING_STATE_FAULT;
            }
        }
    } else {
        // Канали дзеркалюють один одного — скидаємо таймер розсинхронізму
        sw->discrepancy_active = false;
        sw->discrepancy_timer = 0;
    }

    // 4. Логіка скінченного автомата (FSM) при синхронних каналах
    if (sw->debounced_ch1 == CONTACT_CLOSED && sw->debounced_ch2 == CONTACT_CLOSED) {
        // Замкнені обидва канали — Позиція 2 (ENABLE, дозвіл роботи)
        sw->current_state = ENABLING_STATE_ENABLED;
    } else if (sw->debounced_ch1 == CONTACT_OPEN && sw->debounced_ch2 == CONTACT_OPEN) {
        // Розімкнені обидва канали — утримання або повернення у Позицію 1
        sw->current_state = ENABLING_STATE_RELEASED;
    }

    return sw->current_state;
}

EnablingState_t EnablingSwitch_GetState(const EnablingSwitch_t *sw) {
    return sw ? sw->current_state : ENABLING_STATE_FAULT;
}

void EnablingSwitch_ResetFault(EnablingSwitch_t *sw) {
    if (!sw) return;
    if (sw->debounced_ch1 == CONTACT_OPEN && sw->debounced_ch2 == CONTACT_OPEN) {
        sw->discrepancy_active = false;
        sw->discrepancy_timer = 0;
        sw->current_state = ENABLING_STATE_RELEASED;
    }
}
