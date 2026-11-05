#include <stdio.h>
#include "debouncer.h"

int main(void) {
    debouncer_t button;
    debouncer_init(&button, 20, 500);

    // Simulated noisy button press waveform (milliseconds 0 to 45)
    // 0..10ms: bounce (0, 1, 0, 1, 1, 0, 1...)
    // 10..35ms: solid press (1)
    // 35..45ms: release
    bool raw_trace[] = {
        0, 1, 0, 1, 0, 1, 1, 1, 1, 1, // 0..9 ms (bounce)
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, // 10..19 ms (stable)
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, // 20..29 ms (stable)
        1, 1, 1, 1, 1, 0, 1, 0, 0, 0  // 30..39 ms (release bounce)
    };
    size_t trace_len = sizeof(raw_trace) / sizeof(raw_trace[0]);

    printf("Simulating button debouncing (time step = 2 ms):\n");
    for (size_t i = 0; i < trace_len; i++) {
        uint16_t time_ms = (uint16_t)(i * 2);
        btn_event_t evt = debouncer_update_fsm(&button, raw_trace[i], 2);
        bool shift_active = debouncer_update_shift(&button, raw_trace[i]);

        if (evt == BTN_EVENT_PRESSED) {
            printf("[%03u ms] EVENT: Button Pressed (FSM confirmed)\n", time_ms);
        } else if (evt == BTN_EVENT_RELEASED) {
            printf("[%03u ms] EVENT: Button Released (FSM confirmed)\n", time_ms);
        }

        if (shift_active && i == 14) {
            printf("[%03u ms] Shift Register: 8 consecutive 1s detected\n", time_ms);
        }
    }

    return 0;
}
