#include <stdatomic.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    _Atomic uint32_t value;
} AtomicCounter;

// Атомарне додавання значення до лічильника через цикл CAS з явними бар'єрами пам'яті
uint32_t atomic_counter_add(AtomicCounter* counter, uint32_t delta) {
    // Зчитуємо початковий стан із розслабленим впорядкуванням
    uint32_t expected = atomic_load_explicit(&counter->value, memory_order_relaxed);
    uint32_t desired;
    
    do {
        desired = expected + delta;
        // У разі успіху застосовуємо memory_order_release, при невдачі — memory_order_relaxed.
        // expected оновлюється автоматично при поверненні false.
    } while (!atomic_compare_exchange_weak_explicit(&counter->value,
                                                    &expected,
                                                    desired,
                                                    memory_order_release,
                                                    memory_order_relaxed));
                                                    
    return desired;
}
