#include <stdatomic.h>
#include <stdint.h>
#include <stddef.h>

// Вирівнювання комірки пам'яті для виключення false sharing
typedef struct {
    _Atomic uint32_t value;
    uint8_t padding[64 - sizeof(_Atomic uint32_t)];
} _Alignas(64) padded_cell_t;

typedef struct {
    _Atomic uint32_t base;
    padded_cell_t slots[4];
} embedded_long_adder_t;

void embedded_long_adder_init(embedded_long_adder_t* adder) {
    atomic_init(&adder->base, 0);
    for (size_t i = 0; i < 4; ++i) {
        atomic_init(&adder->slots[i].value, 0);
    }
}

void embedded_long_adder_add(embedded_long_adder_t* adder, uint32_t val, uint32_t core_id) {
    uint32_t expected = atomic_load_explicit(&adder->base, memory_order_relaxed);
    
    // Спроба оновлення базової змінної через CAS
    if (atomic_compare_exchange_weak_explicit(&adder->base, &expected, expected + val,
                                              memory_order_relaxed, memory_order_relaxed)) {
        return;
    }

    // Модифікація посмугованої комірки за індексом ядра
    size_t idx = core_id % 4;
    atomic_fetch_add_explicit(&adder->slots[idx].value, val, memory_order_relaxed);
}

uint32_t embedded_long_adder_sum(const embedded_long_adder_t* adder) {
    uint32_t total = atomic_load_explicit(&adder->base, memory_order_relaxed);
    for (size_t i = 0; i < 4; ++i) {
        total += atomic_load_explicit(&adder->slots[i].value, memory_order_relaxed);
    }
    return total;
}
