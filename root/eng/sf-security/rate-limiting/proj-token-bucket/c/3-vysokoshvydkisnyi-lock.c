#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <time.h>

typedef struct {
    uint64_t emission_interval_ns; /* T = 1 / rate (наносекунди) */
    uint64_t burst_tolerance_ns;    /* tau (наносекунди) */
    _Atomic uint64_t tat_ns;        /* Теоретичний час прибуття (атомарний) */
} gcra_limiter_t;

static uint64_t gcra_get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

void gcra_init(gcra_limiter_t *limiter, uint64_t rate_per_sec, uint64_t burst_capacity) {
    limiter->emission_interval_ns = 1000000000ULL / rate_per_sec;
    limiter->burst_tolerance_ns = (burst_capacity - 1) * limiter->emission_interval_ns;
    atomic_init(&limiter->tat_ns, 0);
}

bool gcra_try_acquire(gcra_limiter_t *limiter) {
    uint64_t now = gcra_get_time_ns();
    uint64_t current_tat = atomic_load_explicit(&limiter->tat_ns, memory_order_relaxed);

    while (1) {
        /* Якщо прибуття раніше, ніж TAT - burst_tolerance: відхилити */
        if (current_tat > now + limiter->burst_tolerance_ns) {
            return false;
        }

        /* Новий очікуваний час прибуття */
        uint64_t base = (now > current_tat) ? now : current_tat;
        uint64_t next_tat = base + limiter->emission_interval_ns;

        /* Атомарна спроба зафіксувати новий TAT */
        if (atomic_compare_exchange_weak_explicit(
                &limiter->tat_ns,
                &current_tat,
                next_tat,
                memory_order_acq_rel,
                memory_order_relaxed)) {
            return true;
        }
        /* При колізії цикл повторюється з оновленим current_tat */
    }
}
