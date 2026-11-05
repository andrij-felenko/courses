#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

// Структурний тип для збереження атомарного стану
typedef struct {
    _Atomic uint32_t state;
} state_manager_t;

// Ініціалізація модуля стану
void state_manager_init(state_manager_t *mgr, uint32_t initial_val) {
    atomic_init(&mgr->state, initial_val);
}

// Безблокувальне оновлення стану за допомогою CAS-петлі
uint32_t state_manager_update(state_manager_t *mgr, uint32_t addend) {
    uint32_t expected = atomic_load_explicit(&mgr->state, memory_order_relaxed);
    uint32_t desired;

    do {
        desired = expected + addend;
        // atomic_compare_exchange_weak оновлює expected актуальним значенням при невдачі
    } while (!atomic_compare_exchange_weak_explicit(
        &mgr->state,
        &expected,
        desired,
        memory_order_release,
        memory_order_relaxed));

    return desired;
}
