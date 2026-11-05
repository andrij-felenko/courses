#include <stdatomic.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct {
    _Atomic int64_t value;
    char padding[56]; // Захист від хибного розділення кешу
} Cell;

typedef struct {
    Cell* cells;
    size_t mask;
    _Atomic int64_t base;
} StripedAccumulator;

void striped_accumulator_init(StripedAccumulator* acc, size_t num_cells) {
    acc->mask = num_cells - 1;
    acc->cells = (Cell*)calloc(num_cells, sizeof(Cell));
    atomic_init(&acc->base, 0);
}

void striped_accumulator_add(StripedAccumulator* acc, int64_t val, size_t thread_probe) {
    size_t idx = thread_probe & acc->mask;
    atomic_fetch_add_explicit(&acc->cells[idx].value, val, memory_order_relaxed);
}

int64_t striped_accumulator_sum(const StripedAccumulator* acc) {
    int64_t total = atomic_load_explicit(&acc->base, memory_order_relaxed);
    for (size_t i = 0; i <= acc->mask; ++i) {
        total += atomic_load_explicit(&acc->cells[i].value, memory_order_relaxed);
    }
    return total;
}
