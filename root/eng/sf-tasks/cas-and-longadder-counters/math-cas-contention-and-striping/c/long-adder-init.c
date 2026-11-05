#include <stdatomic.h>
#include <stdint.h>
#include <stdlib.h>

// Вирівнювання комірки на 64 байти для виключення false sharing
typedef struct {
    _Atomic int64_t value;
    uint8_t padding[64 - sizeof(_Atomic int64_t)];
} _Alignas(64) PaddedCellC;

typedef struct {
    _Atomic int64_t base;
    PaddedCellC* cells;
    size_t num_cells;
} StripedLongAdderC;

void long_adder_init(StripedLongAdderC* adder, size_t num_cells) {
    atomic_init(&adder->base, 0);
    adder->num_cells = num_cells;
    adder->cells = (PaddedCellC*)aligned_alloc(64, num_cells * sizeof(PaddedCellC));
    for (size_t i = 0; i < num_cells; ++i) {
        atomic_init(&adder->cells[i].value, 0);
    }
}

void long_adder_add(StripedLongAdderC* adder, int64_t x, uintptr_t thread_id) {
    int64_t expected = atomic_load_explicit(&adder->base, memory_order_relaxed);
    if (atomic_compare_exchange_weak_explicit(&adder->base, &expected, expected + x,
                                              memory_order_relaxed, memory_order_relaxed)) {
        return;
    }

    size_t idx = thread_id % adder->num_cells;
    atomic_fetch_add_explicit(&adder->cells[idx].value, x, memory_order_relaxed);
}

int64_t long_adder_sum(const StripedLongAdderC* adder) {
    int64_t total = atomic_load_explicit(&adder->base, memory_order_relaxed);
    for (size_t i = 0; i < adder->num_cells; ++i) {
        total += atomic_load_explicit(&adder->cells[i].value, memory_order_relaxed);
    }
    return total;
}
