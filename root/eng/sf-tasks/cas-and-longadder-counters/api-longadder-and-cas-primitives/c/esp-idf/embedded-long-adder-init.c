#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Вирівнювання за розміром шини пам'яті мікроконтролера (32 байти або 64 байти)
#define EMBEDDED_ALIGNMENT 32
#define MAX_EMBEDDED_SLOTS 4

// Структура вирівняного локального слота лічильника
typedef struct {
    _Atomic int64_t value __attribute__((aligned(EMBEDDED_ALIGNMENT)));
} embedded_counter_slot_t;

// Основна структура неблокуючого лічильника для RTOS
typedef struct {
    _Atomic int64_t base __attribute__((aligned(EMBEDDED_ALIGNMENT)));
    embedded_counter_slot_t slots[MAX_EMBEDDED_SLOTS];
    _Atomic uint32_t active_slots;
} embedded_long_adder_t;

// Ініціалізація лічильника
void embedded_long_adder_init(embedded_long_adder_t *adder) {
    atomic_init(&adder->base, 0);
    atomic_init(&adder->active_slots, 1);
    for (size_t i = 0; i < MAX_EMBEDDED_SLOTS; i++) {
        atomic_init(&adder->slots[i].value, 0);
    }
}

// Швидкий та безпечний інкремент лічильника із задач або ISR
void embedded_long_adder_add(embedded_long_adder_t *adder, int64_t val) {
    int64_t current_base = atomic_load_explicit(&adder->base, memory_order_relaxed);
    
    // Спроба атомарного оновлення бази через CAS
    if (atomic_compare_exchange_weak_explicit(&adder->base, &current_base, 
                                             current_base + val, 
                                             memory_order_release, 
                                             memory_order_relaxed)) {
        return;
    }

    // При колізії розподіляємо навантаження по слотах на основі ID поточної задачі RTOS
    TaskHandle_t current_task = xTaskGetCurrentTaskHandle();
    uint32_t slot_idx = ((uintptr_t)current_task >> 4) % MAX_EMBEDDED_SLOTS;

    int64_t slot_val = atomic_load_explicit(&adder->slots[slot_idx].value, memory_order_relaxed);
    while (!atomic_compare_exchange_weak_explicit(&adder->slots[slot_idx].value, 
                                                   &slot_val, 
                                                   slot_val + val, 
                                                   memory_order_release, 
                                                   memory_order_relaxed)) {
        // Рехешування слота при конкуренції
        slot_idx = (slot_idx + 1) % MAX_EMBEDDED_SLOTS;
    }
}

// Зчитування підсумкового значення лічильника
int64_t embedded_long_adder_sum(const embedded_long_adder_t *adder) {
    int64_t total = atomic_load_explicit(&adder->base, memory_order_acquire);
    for (size_t i = 0; i < MAX_EMBEDDED_SLOTS; i++) {
        total += atomic_load_explicit(&adder->slots[i].value, memory_order_acquire);
    }
    return total;
}
