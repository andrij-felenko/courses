#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double upper_bound;
    double lower_bound;
    double* s_sums;
    size_t max_k;
    bool converged;
} bonferroni_result_t;

/* Оракул перетину подій для тестової моделі незалежних або частково залежних подій */
typedef double (*intersection_oracle_f)(const size_t* indices, size_t r, void* user_data);

/* Допоміжна функція для рекурсивного перебору комбінацій C(n, r) */
static void compute_s_r_recursive(size_t start_idx, size_t depth, size_t r, size_t n,
                                  size_t* current_comb, double* accum,
                                  intersection_oracle_f oracle, void* user_data) {
    if (depth == r) {
        double p_intersect = oracle(current_comb, r, user_data);
        *accum += p_intersect;
        return;
    }

    for (size_t i = start_idx; i < n; ++i) {
        current_comb[depth] = i;
        compute_s_r_recursive(i + 1, depth + 1, r, n, current_comb, accum, oracle, user_data);
    }
}

bonferroni_result_t* bonferroni_calculate(size_t n, size_t max_k, 
                                          intersection_oracle_f oracle, void* user_data) {
    if (n == 0 || max_k == 0) return NULL;
    if (max_k > n) max_k = n;

    bonferroni_result_t* res = (bonferroni_result_t*)malloc(sizeof(bonferroni_result_t));
    if (!res) return NULL;

    res->s_sums = (double*)calloc(max_k + 1, sizeof(double));
    size_t* comb_buf = (size_t*)malloc(max_k * sizeof(size_t));
    if (!res->s_sums || !comb_buf) {
        free(res->s_sums);
        free(comb_buf);
        free(res);
        return NULL;
    }

    res->max_k = max_k;
    res->upper_bound = 1.0;
    res->lower_bound = 0.0;
    res->converged = false;

    double current_val = 0.0;

    for (size_t r = 1; r <= max_k; ++r) {
        double s_r = 0.0;
        compute_s_r_recursive(0, 0, r, n, comb_buf, &s_r, oracle, user_data);
        res->s_sums[r] = s_r;

        if (r % 2 == 1) {
            current_val += s_r;
            if (current_val < res->upper_bound) {
                res->upper_bound = current_val;
            }
        } else {
            current_val -= s_r;
            if (current_val > res->lower_bound) {
                res->lower_bound = current_val;
            }
        }
    }

    /* Гарантуємо коридор ймовірності [0, 1] */
    if (res->upper_bound > 1.0) res->upper_bound = 1.0;
    if (res->lower_bound < 0.0) res->lower_bound = 0.0;
    if (res->lower_bound > res->upper_bound) res->lower_bound = res->upper_bound;

    free(comb_buf);
    return res;
}

void bonferroni_free(bonferroni_result_t* res) {
    if (res) {
        free(res->s_sums);
        free(res);
    }
}
