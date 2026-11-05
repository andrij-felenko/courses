#include <stdatomic.h>
#include <stdint.h>

typedef struct {
    _Atomic int64_t counter;
} AtomicEventCounter;

void atomic_counter_init(AtomicEventCounter* counter) {
    atomic_init(&counter->counter, 0);
}

void atomic_counter_increment(AtomicEventCounter* counter) {
    int64_t current = atomic_load_explicit(&counter->counter, memory_order_relaxed);
    while (!atomic_compare_exchange_weak_explicit(&counter->counter, &current, current + 1,
                                                 memory_order_release,
                                                 memory_order_relaxed)) {
        // Змінна current оновлюється значенням з пам'яті
    }
}

int64_t atomic_counter_get_value(const AtomicEventCounter* counter) {
    return atomic_load_explicit(&counter->counter, memory_order_acquire);
}
