/* C Implementation: Decision Tree Complexity Analyzer */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_N 12

typedef struct {
    int n;
    uint8_t truth_table[1 << MAX_N];
} BooleanFn;

/* Перевірка, чи є функція константою на підпросторі, заданому fixed_mask та fixed_vals */
static bool is_constant(const BooleanFn *fn, uint32_t fixed_mask, uint32_t fixed_vals, uint8_t *const_val) {
    int total = 1 << fn->n;
    bool found_first = false;
    uint8_t first_val = 0;

    for (int x = 0; x < total; x++) {
        if ((x & fixed_mask) == fixed_vals) {
            uint8_t val = fn->truth_table[x];
            if (!found_first) {
                first_val = val;
                found_first = true;
            } else if (val != first_val) {
                return false;
            }
        }
    }
    if (const_val) *const_val = first_val;
    return true;
}

/* Рекурсивне обчислення D(f) (найменша глибина дерева рішень) */
static int compute_D_rec(const BooleanFn *fn, uint32_t fixed_mask, uint32_t fixed_vals) {
    uint8_t cval;
    if (is_constant(fn, fixed_mask, fixed_vals, &cval)) {
        return 0;
    }

    int min_worst_depth = fn->n + 1;

    for (int i = 0; i < fn->n; i++) {
        if (!(fixed_mask & (1U << i))) {
            /* Запит змінної x_i */
            uint32_t next_mask = fixed_mask | (1U << i);
            
            /* Гілка x_i = 0 */
            int depth0 = compute_D_rec(fn, next_mask, fixed_vals);
            /* Гілка x_i = 1 */
            int depth1 = compute_D_rec(fn, next_mask, fixed_vals | (1U << i));

            int worst = (depth0 > depth1 ? depth0 : depth1) + 1;
            if (worst < min_worst_depth) {
                min_worst_depth = worst;
            }
        }
    }
    return min_worst_depth;
}

/* Обчислення чутливості s(f) */
static int compute_sensitivity(const BooleanFn *fn) {
    int max_s = 0;
    int total = 1 << fn->n;

    for (int x = 0; x < total; x++) {
        int current_s = 0;
        for (int i = 0; i < fn->n; i++) {
            int neighbor = x ^ (1 << i);
            if (fn->truth_table[neighbor] != fn->truth_table[x]) {
                current_s++;
            }
        }
        if (current_s > max_s) {
            max_s = current_s;
        }
    }
    return max_s;
}

/* Обчислення складності сертифікатів C(f) */
static int compute_certificate_complexity(const BooleanFn *fn) {
    int max_cert = 0;
    int total = 1 << fn->n;

    for (int x = 0; x < total; x++) {
        uint8_t target_val = fn->truth_table[x];
        int min_size_for_x = fn->n;

        /* Перебираємо всі підмножини маски розміру від 1 до n */
        for (uint32_t mask = 1; mask < (1U << fn->n); mask++) {
            int size = 0;
            for (int i = 0; i < fn->n; i++) {
                if (mask & (1U << i)) size++;
            }
            if (size >= min_size_for_x) continue;

            uint32_t fixed_vals = x & mask;
            uint8_t cval;
            if (is_constant(fn, mask, fixed_vals, &cval) && cval == target_val) {
                min_size_for_x = size;
            }
        }
        if (min_size_for_x > max_cert) {
            max_cert = min_size_for_x;
        }
    }
    return max_cert;
}

int main(void) {
    BooleanFn maj3;
    maj3.n = 3;
    /* MAJ(x1, x2, x3): 1 якщо більшість бітів дорівнює 1 */
    for (int x = 0; x < 8; x++) {
        int cnt = 0;
        for (int i = 0; i < 3; i++) {
            if (x & (1 << i)) cnt++;
        }
        maj3.truth_table[x] = (cnt >= 2) ? 1 : 0;
    }

    printf("=== Аналіз складності функції MAJ(x1, x2, x3) ===\n");
    printf("Чутливість s(MAJ): %d\n", compute_sensitivity(&maj3));
    printf("Складність сертифікатів C(MAJ): %d\n", compute_certificate_complexity(&maj3));
    printf("Детермінована складність D(MAJ): %d\n", compute_D_rec(&maj3, 0, 0));

    return 0;
}
