#include "debouncer.h"

void debouncer_init(debouncer_t *btn, uint16_t debounce_ms, uint16_t long_press_ms) {
    if (!btn) return;
    btn->state = BTN_STATE_RELEASED;
    btn->debounce_timer_ms = 0;
    btn->hold_timer_ms = 0;
    btn->debounce_threshold_ms = debounce_ms ? debounce_ms : 20;
    btn->long_press_threshold_ms = long_press_ms ? long_press_ms : 1000;
    btn->long_press_fired = false;
    btn->shift_history = 0xFFFF;
}

btn_event_t debouncer_update_fsm(debouncer_t *btn, bool raw_pressed, uint16_t elapsed_ms) {
    if (!btn) return BTN_EVENT_NONE;
    btn_event_t event = BTN_EVENT_NONE;

    switch (btn->state) {
        case BTN_STATE_RELEASED:
            if (raw_pressed) {
                btn->state = BTN_STATE_DEBOUNCE_PRESS;
                btn->debounce_timer_ms = 0;
            }
            break;

        case BTN_STATE_DEBOUNCE_PRESS:
            btn->debounce_timer_ms += elapsed_ms;
            if (btn->debounce_timer_ms >= btn->debounce_threshold_ms) {
                if (raw_pressed) {
                    btn->state = BTN_STATE_PRESSED;
                    btn->hold_timer_ms = 0;
                    btn->long_press_fired = false;
                    event = BTN_EVENT_PRESSED;
                } else {
                    btn->state = BTN_STATE_RELEASED;
                }
            }
            break;

        case BTN_STATE_PRESSED:
            if (!raw_pressed) {
                btn->state = BTN_STATE_DEBOUNCE_RELEASE;
                btn->debounce_timer_ms = 0;
            } else {
                btn->hold_timer_ms += elapsed_ms;
                if (!btn->long_press_fired && (btn->hold_timer_ms >= btn->long_press_threshold_ms)) {
                    btn->long_press_fired = true;
                    event = BTN_EVENT_LONG_PRESS;
                }
            }
            break;

        case BTN_STATE_DEBOUNCE_RELEASE:
            btn->debounce_timer_ms += elapsed_ms;
            if (btn->debounce_timer_ms >= btn->debounce_threshold_ms) {
                if (!raw_pressed) {
                    btn->state = BTN_STATE_RELEASED;
                    event = BTN_EVENT_RELEASED;
                } else {
                    btn->state = BTN_STATE_PRESSED;
                }
            }
            break;
    }

    return event;
}

bool debouncer_update_shift(debouncer_t *btn, bool raw_pressed) {
    if (!btn) return false;
    btn->shift_history = (uint16_t)((btn->shift_history << 1) | (raw_pressed ? 1 : 0));
    // 8 consecutive stable readings
    return ((btn->shift_history & 0x00FF) == 0x00FF);
}
