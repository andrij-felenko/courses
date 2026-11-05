#include <stdatomic.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    _Atomic uint32_t counter;
} event_counter_t;

void event_counter_init(event_counter_t *self, uint32_t initial_val) {
    atomic_init(&self->counter, initial_val);
}

// Безблокове збільшення лічильника на задану величину
uint32_t event_counter_add(event_counter_t *self, uint32_t value) {
    uint32_t expected = atomic_load_explicit(&self->counter, memory_order_relaxed);
    uint32_t desired;
    
    // Використовуємо слабкий CAS у циклі оновлення для максимальної швидкодії
    do {
        desired = expected + value;
    } while (!atomic_compare_exchange_weak_explicit(
        &self->counter,
        &expected,
        desired,
        memory_order_release, // Порядок пам'яті у разі успіху
        memory_order_relaxed  // Порядок пам'яті у разі невдачі
    ));
    
    return desired;
}
