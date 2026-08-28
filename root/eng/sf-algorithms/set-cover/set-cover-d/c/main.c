#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_SETS 64

typedef struct {
    uint64_t mask;
    double cost;
    int id;
} BitSubset;

/* Швидкий жадібний вибір на 64-бітному універсумі */
int run_greedy_step(const BitSubset* subsets, int m, uint64_t covered, int* out_best_idx) {
    int best_idx = -1;
    double best_ratio = 1e18;

    for (int i = 0; i < m; ++i) {
        uint64_t newly_covered = subsets[i].mask & (~covered);
        /* Апаратний підрахунок кількості одиничних бітів */
        int count = __builtin_popcountll(newly_covered);

        if (count > 0) {
            double ratio = subsets[i].cost / (double)count;
            if (ratio < best_ratio) {
                best_ratio = ratio;
                best_idx = i;
            }
        }
    }

    *out_best_idx = best_idx;
    return (best_idx != -1) ? 0 : -1;
}
