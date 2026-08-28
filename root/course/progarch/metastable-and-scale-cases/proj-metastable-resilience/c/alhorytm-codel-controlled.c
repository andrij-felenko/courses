/* C Implementation: CoDel Queue Latency Shedder */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

typedef struct {
    uint64_t target_sojourn_ms;
    uint64_t interval_ms;
    uint64_t first_above_time_ms;
    uint64_t drop_next_ms;
    bool dropping;
    int count;
} codel_state_t;

void codel_init(codel_state_t *state, uint64_t target_ms, uint64_t interval_ms) {
    state->target_sojourn_ms = target_ms;
    state->interval_ms = interval_ms;
    state->first_above_time_ms = 0;
    state->drop_next_ms = 0;
    state->dropping = false;
    state->count = 0;
}

bool codel_should_drop(codel_state_t *state, uint64_t sojourn_time_ms, uint64_t now_ms) {
    bool ok_to_drop = false;

    if (sojourn_time_ms < state->target_sojourn_ms) {
        state->first_above_time_ms = 0;
    } else {
        if (state->first_above_time_ms == 0) {
            state->first_above_time_ms = now_ms + state->interval_ms;
        } else if (now_ms >= state->first_above_time_ms) {
            ok_to_drop = true;
        }
    }

    if (state->dropping) {
        if (!ok_to_drop) {
            state->dropping = false;
        } else if (now_ms >= state->drop_next_ms) {
            state->count++;
            /* Inverse square root control interval decay */
            uint64_t next_interval = state->interval_ms / (uint64_t)(1.0 + (double)state->count);
            state->drop_next_ms = now_ms + (next_interval > 2 ? next_interval : 2);
            return true;
        }
    } else if (ok_to_drop) {
        state->dropping = true;
        state->count = 1;
        state->drop_next_ms = now_ms + state->interval_ms;
        return true;
    }

    return false;
}
