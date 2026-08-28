#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Злиття двох рівномірних резервуарів у єдиний вихідний резервуар */
bool merge_reservoirs_uniform(
    const uint64_t *res_a, size_t size_a, uint64_t total_a,
    const uint64_t *res_b, size_t size_b, uint64_t total_b,
    uint64_t *out_reservoir, size_t target_k, uint64_t seed
) {
    if (!res_a || !res_b || !out_reservoir || target_k == 0) return false;

    ares_sampler_t merger;
    if (!ares_sampler_init(&merger, target_k, seed)) return false;

    /* Розрахунок вагових коефіцієнтів елементів кожного резервуара */
    double weight_a = (size_a > 0) ? ((double)total_a / (double)size_a) : 0.0;
    double weight_b = (size_b > 0) ? ((double)total_b / (double)size_b) : 0.0;

    /* Додавання елементів першого резервуара */
    for (size_t i = 0; i < size_a; ++i) {
        ares_sampler_push(&merger, res_a[i], weight_a);
    }

    /* Додавання елементів другого резервуара */
    for (size_t i = 0; i < size_b; ++i) {
        ares_sampler_push(&merger, res_b[i], weight_b);
    }

    /* Копіювання результуючої вибірки */
    for (size_t i = 0; i < merger.current_size; ++i) {
        out_reservoir[i] = merger.heap[i].item;
    }

    ares_sampler_destroy(&merger);
    return true;
}
