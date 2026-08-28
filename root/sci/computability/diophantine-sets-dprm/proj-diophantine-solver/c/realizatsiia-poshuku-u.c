#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef int64_t (*DiophantinePoly)(const int64_t* vars, size_t n);

typedef struct {
    size_t num_vars;
    int64_t max_bound;
    uint64_t evaluated_points;
} SearchStats;

// Рекурсивний обхід граней гіперкуба з поточною нормою B
static bool search_layer(DiophantinePoly poly, int64_t* current, size_t idx, 
                         size_t n, int64_t bound, bool has_boundary, SearchStats* stats) {
    if (idx == n) {
        if (!has_boundary) {
            return false; // Точка вже перевірялася на попередніх кроках
        }
        stats->evaluated_points++;
        return poly(current, n) == 0;
    }

    for (int64_t val = 0; val <= bound; ++val) {
        current[idx] = val;
        bool on_bound = has_boundary || (val == bound);
        if (search_layer(poly, current, idx + 1, n, bound, on_bound, stats)) {
            return true;
        }
    }
    return false;
}

bool diophantine_dovetail_search(DiophantinePoly poly, size_t n, int64_t max_bound, 
                                 int64_t* out_solution, SearchStats* stats) {
    stats->num_vars = n;
    stats->max_bound = max_bound;
    stats->evaluated_points = 0;

    int64_t current[16] = {0};
    if (n > 16) return false; // Захист стеку від переповнення

    for (int64_t b = 0; b <= max_bound; ++b) {
        if (search_layer(poly, current, 0, n, b, (b == 0), stats)) {
            for (size_t i = 0; i < n; ++i) {
                out_solution[i] = current[i];
            }
            return true;
        }
    }
    return false;
}
