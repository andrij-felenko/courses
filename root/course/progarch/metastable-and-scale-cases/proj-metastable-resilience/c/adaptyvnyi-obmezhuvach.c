/* C Implementation: Adaptive Load Shedder and Circuit Breaker */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <time.h>

typedef enum {
    CB_STATE_CLOSED = 0,
    CB_STATE_OPEN,
    CB_STATE_HALF_OPEN
} circuit_state_t;

typedef struct {
    atomic_int active_requests;
    int max_concurrency;
    atomic_int failure_count;
    int failure_threshold;
    atomic_uint_fast64_t last_state_change_ms;
    uint64_t cooldown_period_ms;
    _Atomic circuit_state_t state;
} resilience_guard_t;

uint64_t get_current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

void resilience_guard_init(resilience_guard_t *guard, int max_concurrency, int failure_threshold, uint64_t cooldown_ms) {
    atomic_store(&guard->active_requests, 0);
    guard->max_concurrency = max_concurrency;
    atomic_store(&guard->failure_count, 0);
    guard->failure_threshold = failure_threshold;
    atomic_store(&guard->last_state_change_ms, get_current_time_ms());
    guard->cooldown_period_ms = cooldown_ms;
    atomic_store(&guard->state, CB_STATE_CLOSED);
}

bool resilience_guard_allow(resilience_guard_t *guard) {
    uint64_t now = get_current_time_ms();
    circuit_state_t current_state = atomic_load(&guard->state);

    if (current_state == CB_STATE_OPEN) {
        uint64_t last_change = atomic_load(&guard->last_state_change_ms);
        if (now - last_change > guard->cooldown_period_ms) {
            if (atomic_compare_exchange_strong(&guard->state, &current_state, CB_STATE_HALF_OPEN)) {
                atomic_store(&guard->last_state_change_ms, now);
                current_state = CB_STATE_HALF_OPEN;
            }
        } else {
            return false; /* Rejected by Circuit Breaker */
        }
    }

    int active = atomic_load(&guard->active_requests);
    if (active >= guard->max_concurrency) {
        return false; /* Load Shedding: Concurrency Bulkhead limit exceeded */
    }

    atomic_fetch_add(&guard->active_requests, 1);
    return true;
}

void resilience_guard_on_result(resilience_guard_t *guard, bool is_success) {
    atomic_fetch_sub(&guard->active_requests, 1);
    uint64_t now = get_current_time_ms();
    circuit_state_t current_state = atomic_load(&guard->state);

    if (is_success) {
        if (current_state == CB_STATE_HALF_OPEN) {
            atomic_store(&guard->state, CB_STATE_CLOSED);
            atomic_store(&guard->failure_count, 0);
            atomic_store(&guard->last_state_change_ms, now);
        } else if (current_state == CB_STATE_CLOSED) {
            atomic_store(&guard->failure_count, 0);
        }
    } else {
        int failures = atomic_fetch_add(&guard->failure_count, 1) + 1;
        if (failures >= guard->failure_threshold && current_state != CB_STATE_OPEN) {
            atomic_store(&guard->state, CB_STATE_OPEN);
            atomic_store(&guard->last_state_change_ms, now);
        }
    }
}
