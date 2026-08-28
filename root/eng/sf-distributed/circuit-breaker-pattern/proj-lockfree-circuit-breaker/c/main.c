#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define CB_WINDOW_SIZE 64
#define CB_WINDOW_MASK (CB_WINDOW_SIZE - 1)

typedef enum {
    CB_STATE_CLOSED = 0,
    CB_STATE_OPEN = 1,
    CB_STATE_HALF_OPEN = 2
} cb_state_t;

typedef struct {
    uint32_t failure_rate_threshold;    /* Відсоток збоїв для розмикання (напр. 50) */
    uint32_t minimum_number_of_calls;   /* Поріг вибірки для розрахунку відсотка */
    uint64_t wait_duration_in_open_ns;  /* Час очікування в стані OPEN (наносекунди) */
    uint32_t permitted_half_open_calls; /* Дозволена кількість пробних запитів */
} cb_config_t;

typedef struct {
    _Alignas(64) atomic_int state;
    _Alignas(64) atomic_uint_fast64_t head_index;
    _Alignas(64) atomic_bool ring_buffer[CB_WINDOW_SIZE]; /* true = помилка, false = успіх */
    _Alignas(64) atomic_uint_fast64_t last_state_change_ns;
    _Alignas(64) atomic_uint_fast32_t half_open_probe_count;
    _Alignas(64) atomic_uint_fast32_t half_open_failure_count;
    cb_config_t config;
} circuit_breaker_t;

static inline uint64_t cb_get_monotonic_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

void cb_init(circuit_breaker_t *cb, const cb_config_t *cfg) {
    atomic_init(&cb->state, CB_STATE_CLOSED);
    atomic_init(&cb->head_index, 0);
    atomic_init(&cb->last_state_change_ns, cb_get_monotonic_ns());
    atomic_init(&cb->half_open_probe_count, 0);
    atomic_init(&cb->half_open_failure_count, 0);
    cb->config = *cfg;
    for (int i = 0; i < CB_WINDOW_SIZE; i++) {
        atomic_init(&cb->ring_buffer[i], false);
    }
}

static void cb_transition_to(circuit_breaker_t *cb, cb_state_t expected, cb_state_t next) {
    int exp = expected;
    if (atomic_compare_exchange_strong_explicit(&cb->state, &exp, next,
                                                memory_order_release, memory_order_relaxed)) {
        atomic_store_explicit(&cb->last_state_change_ns, cb_get_monotonic_ns(), memory_order_release);
        if (next == CB_STATE_HALF_OPEN) {
            atomic_store_explicit(&cb->half_open_probe_count, 0, memory_order_release);
            atomic_store_explicit(&cb->half_open_failure_count, 0, memory_order_release);
        } else if (next == CB_STATE_CLOSED) {
            atomic_store_explicit(&cb->head_index, 0, memory_order_release);
            for (int i = 0; i < CB_WINDOW_SIZE; i++) {
                atomic_store_explicit(&cb->ring_buffer[i], false, memory_order_relaxed);
            }
        }
    }
}

bool cb_allow_request(circuit_breaker_t *cb) {
    cb_state_t current_state = (cb_state_t)atomic_load_explicit(&cb->state, memory_order_acquire);

    if (current_state == CB_STATE_CLOSED) {
        return true;
    }

    if (current_state == CB_STATE_OPEN) {
        uint64_t now = cb_get_monotonic_ns();
        uint64_t last_change = atomic_load_explicit(&cb->last_state_change_ns, memory_order_acquire);
        if (now - last_change >= cb->config.wait_duration_in_open_ns) {
            cb_transition_to(cb, CB_STATE_OPEN, CB_STATE_HALF_OPEN);
            return cb_allow_request(cb);
        }
        return false;
    }

    if (current_state == CB_STATE_HALF_OPEN) {
        uint32_t probe_idx = atomic_fetch_add_explicit(&cb->half_open_probe_count, 1, memory_order_acq_rel);
        if (probe_idx < cb->config.permitted_half_open_calls) {
            return true;
        }
        return false;
    }

    return false;
}

void cb_record_result(circuit_breaker_t *cb, bool is_failure) {
    cb_state_t current_state = (cb_state_t)atomic_load_explicit(&cb->state, memory_order_acquire);

    if (current_state == CB_STATE_HALF_OPEN) {
        if (is_failure) {
            cb_transition_to(cb, CB_STATE_HALF_OPEN, CB_STATE_OPEN);
        } else {
            uint32_t probes = atomic_load_explicit(&cb->half_open_probe_count, memory_order_acquire);
            if (probes >= cb->config.permitted_half_open_calls) {
                cb_transition_to(cb, CB_STATE_HALF_OPEN, CB_STATE_CLOSED);
            }
        }
        return;
    }

    if (current_state == CB_STATE_CLOSED) {
        uint64_t idx = atomic_fetch_add_explicit(&cb->head_index, 1, memory_order_acq_rel);
        atomic_store_explicit(&cb->ring_buffer[idx & CB_WINDOW_MASK], is_failure, memory_order_release);

        uint64_t total_recorded = idx + 1;
        if (total_recorded >= cb->config.minimum_number_of_calls) {
            uint32_t window_size = total_recorded < CB_WINDOW_SIZE ? (uint32_t)total_recorded : CB_WINDOW_SIZE;
            uint32_t failures = 0;
            for (uint32_t i = 0; i < window_size; i++) {
                if (atomic_load_explicit(&cb->ring_buffer[i], memory_order_relaxed)) {
                    failures++;
                }
            }
            uint32_t failure_rate = (failures * 100) / window_size;
            if (failure_rate >= cb->config.failure_rate_threshold) {
                cb_transition_to(cb, CB_STATE_CLOSED, CB_STATE_OPEN);
            }
        }
    }
}
