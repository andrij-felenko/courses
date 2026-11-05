#include <stdio.h>
#include <stdatomic.h>
#include <stdbool.h>

typedef struct {
    _Atomic long value;
} atomic_counter_t;

void counter_init(atomic_counter_t* counter, long initial) {
    atomic_init(&counter->value, initial);
}

// Неблокувальне додавання до лічильника через цикл Read-Modify-CAS
long counter_add(atomic_counter_t* counter, long delta) {
    long current = atomic_load_explicit(&counter->value, memory_order_relaxed);
    long new_value;
    
    // Оптимістичний цикл повторних спроб
    do {
        new_value = current + delta;
        // Використовуємо слабий CAS у циклі для максимальної швидкодії на RISC-архітектурах
    } while (!atomic_compare_exchange_weak_explicit(
        &counter->value,
        &current,       // При невдачі current автоматично оновлюється значенням із пам'яті
        new_value,
        memory_order_release, // Семантика запису при успіху
        memory_order_relaxed  // Семантика зчитування при невдачі
    ));

    return new_value;
}
