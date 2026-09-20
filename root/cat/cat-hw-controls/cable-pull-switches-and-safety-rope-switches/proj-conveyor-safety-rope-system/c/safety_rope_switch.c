#include "safety_rope_switch.h"
#include <stddef.h>

static void update_channel_debounce(safety_channel_t *ch, bool raw_pin, uint16_t dt_ms, uint16_t debounce_target_ms) {
    ch->raw_state = raw_pin;
    if (ch->raw_state != ch->debounced_state) {
        ch->debounce_timer += dt_ms;
        if (ch->debounce_timer >= debounce_target_ms) {
            ch->debounced_state = ch->raw_state;
            ch->debounce_timer = 0;
        }
    } else {
        ch->debounce_timer = 0;
    }
}

void safety_rope_switch_init(safety_rope_switch_t *sw, uint16_t max_discrepancy_ms, uint16_t debounce_time_ms) {
    if (sw == NULL) return;

    sw->channel1.raw_state = true;
    sw->channel1.debounced_state = true;
    sw->channel1.debounce_timer = 0;

    sw->channel2.raw_state = true;
    sw->channel2.debounced_state = true;
    sw->channel2.debounce_timer = 0;

    sw->state = SAFETY_STATE_NORMAL;
    sw->discrepancy_timer_ms = 0;
    sw->max_discrepancy_ms = (max_discrepancy_ms > 0) ? max_discrepancy_ms : 40;
    sw->debounce_time_ms = (debounce_time_ms > 0) ? debounce_time_ms : 5;
    sw->safety_output = true;
    sw->fault_latched = false;
}

void safety_rope_switch_update(safety_rope_switch_t *sw, bool ch1_raw, bool ch2_raw, uint16_t dt_ms) {
    if (sw == NULL) return;

    // Фільтрація дребезгу контактів для обох незалежних NC-каналів
    update_channel_debounce(&sw->channel1, ch1_raw, dt_ms, sw->debounce_time_ms);
    update_channel_debounce(&sw->channel2, ch2_raw, dt_ms, sw->debounce_time_ms);

    bool ch1_ok = sw->channel1.debounced_state;
    bool ch2_ok = sw->channel2.debounced_state;

    // Скінченний автомат опитування двоканального контуру безпеки
    switch (sw->state) {
        case SAFETY_STATE_NORMAL:
            if (ch1_ok && ch2_ok) {
                sw->safety_output = true;
                sw->discrepancy_timer_ms = 0;
            } else if (!ch1_ok && !ch2_ok) {
                // Одночасне розмикання обох NC-контактів — звичайне аварійне спрацьовування
                sw->state = SAFETY_STATE_TRIPPED_EMERGENCY;
                sw->safety_output = false;
            } else {
                // Розсинхрон: один контакт розімкнений, інший ще замкнений
                sw->discrepancy_timer_ms += dt_ms;
                sw->safety_output = false; // Негайно знімаємо вихід безпеки
                if (sw->discrepancy_timer_ms >= sw->max_discrepancy_ms) {
                    // Перевищено допуск розсинхронізації — засув помилки обладнання
                    sw->state = SAFETY_STATE_DISCREPANCY_FAULT;
                    sw->fault_latched = true;
                }
            }
            break;

        case SAFETY_STATE_TRIPPED_EMERGENCY:
            sw->safety_output = false;
            // Перевіряємо чи не виник розсинхрон під час відпускання/повернення
            if (ch1_ok != ch2_ok) {
                sw->discrepancy_timer_ms += dt_ms;
                if (sw->discrepancy_timer_ms >= sw->max_discrepancy_ms) {
                    sw->state = SAFETY_STATE_DISCREPANCY_FAULT;
                    sw->fault_latched = true;
                }
            } else if (ch1_ok && ch2_ok) {
                // Обидва контакти повернулися в норму — переходимо в очікування ручного скидання
                sw->state = SAFETY_STATE_WAIT_MANUAL_RESET;
                sw->discrepancy_timer_ms = 0;
            }
            break;

        case SAFETY_STATE_DISCREPANCY_FAULT:
            sw->safety_output = false;
            sw->fault_latched = true;
            // Перебуває у засуві блокування до усунення причин та виклику safety_rope_switch_reset()
            break;

        case SAFETY_STATE_WAIT_MANUAL_RESET:
            sw->safety_output = false;
            if (!ch1_ok || !ch2_ok) {
                // Якщо контакти знову розімкнулися до скидання
                sw->state = SAFETY_STATE_TRIPPED_EMERGENCY;
            }
            break;

        default:
            sw->state = SAFETY_STATE_DISCREPANCY_FAULT;
            sw->safety_output = false;
            break;
    }
}

bool safety_rope_switch_reset(safety_rope_switch_t *sw) {
    if (sw == NULL) return false;

    // Скидання дозволено лише якщо обидва NC-контакти знаходяться в нормальному замкненому стані
    if (sw->channel1.debounced_state && sw->channel2.debounced_state) {
        sw->state = SAFETY_STATE_NORMAL;
        sw->discrepancy_timer_ms = 0;
        sw->safety_output = true;
        sw->fault_latched = false;
        return true;
    }
    return false;
}

bool safety_rope_switch_is_safe(const safety_rope_switch_t *sw) {
    return (sw != NULL) ? sw->safety_output : false;
}
