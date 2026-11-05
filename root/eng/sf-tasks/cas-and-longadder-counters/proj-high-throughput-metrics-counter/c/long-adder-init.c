#include <stdatomic.h>
#include <stdint.h>
#include <stddef.h>

#define CACHE_LINE_BYTES 64
#define NUM_CELLS_MAX 8

// Вирівнювання комірки за межею кеш-лінії для усунення false sharing
typedef struct {
    _Atomic uint64_t value;
    uint8_t padding[CACHE_LINE_BYTES - sizeof(_Atomic uint64_t)];
} __attribute__((aligned(CACHE_LINE_BYTES))) Cell;

typedef struct {
    _Atomic uint64_t base;
    Cell cells[NUM_CELLS_MAX];
    size_t active_cells;
} LongAdder;

void long_adder_init(LongAdder *adder, size_t cell_count) {
    atomic_init(&adder->base, 0);
    adder->active_cells = (cell_count > NUM_CELLS_MAX) ? NUM_CELLS_MAX : cell_count;
    for (size_t i = 0; i < adder->active_cells; i++) {
        atomic_init(&adder->cells[i].value, 0);
    }
}

void long_adder_add(LongAdder *adder, uint64_t val, size_t thread_id) {
    uint64_t b = atomic_load_explicit(&adder->base, memory_order_relaxed);
    if (atomic_compare_exchange_weak_explicit(&adder->base, &b, b + val,
                                              memory_order_relaxed, memory_order_relaxed)) {
        return;
    }

    size_t index = thread_id % adder->active_cells;
    uint64_t c = atomic_load_explicit(&adder->cells[index].value, memory_order_relaxed);
    while (!atomic_compare_exchange_weak_explicit(&adder->cells[index].value, &c, c + val,
                                                  memory_order_relaxed, memory_order_relaxed)) {
        // Повторна спроба при колізії на комірці
    }
}

uint64_t long_adder_sum(const LongAdder *adder) {
    uint64_t sum = atomic_load_explicit(&adder->base, memory_order_relaxed);
    for (size_t i = 0; i < adder->active_cells; i++) {
        sum += atomic_load_explicit(&adder->cells[i].value, memory_order_relaxed);
    }
    return sum;
}
