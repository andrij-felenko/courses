#ifndef DEBOUNCER_H
#define DEBOUNCER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BTN_EVENT_NONE = 0,
    BTN_EVENT_PRESSED,
    BTN_EVENT_RELEASED,
    BTN_EVENT_LONG_PRESS
} btn_event_t;

typedef enum {
    BTN_STATE_RELEASED = 0,
    BTN_STATE_DEBOUNCE_PRESS,
    BTN_STATE_PRESSED,
    BTN_STATE_DEBOUNCE_RELEASE
} btn_state_t;

typedef struct {
    btn_state_t state;
    uint16_t debounce_timer_ms;
    uint16_t hold_timer_ms;
    uint16_t debounce_threshold_ms;
    uint16_t long_press_threshold_ms;
    bool long_press_fired;
    uint16_t shift_history;
} debouncer_t;

void debouncer_init(debouncer_t *btn, uint16_t debounce_ms, uint16_t long_press_ms);
btn_event_t debouncer_update_fsm(debouncer_t *btn, bool raw_pressed, uint16_t elapsed_ms);
bool debouncer_update_shift(debouncer_t *btn, bool raw_pressed);

#ifdef __cplusplus
}
#endif

#endif // DEBOUNCER_H
