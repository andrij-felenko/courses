#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

/* Обчислення перманента за точною формулою Ґлінна */
double permanent_glynn_f64(const double *matrix, size_t n) {
    if (!matrix || n == 0 || n > 62) return 0.0;

    double *delta = (double *)malloc(n * sizeof(double));
    double *row_sum = (double *)malloc(n * sizeof(double));
    if (!delta || !row_sum) {
        free(delta);
        free(row_sum);
        return 0.0;
    }

    /* Ініціалізація δ = (+1, +1, ..., +1) */
    for (size_t j = 0; j < n; ++j) {
        delta[j] = 1.0;
    }

    /* Початкові рядкові суми */
    for (size_t i = 0; i < n; ++i) {
        double s = 0.0;
        for (size_t j = 0; j < n; ++j) {
            s += matrix[i * n + j];
        }
        row_sum[i] = s;
    }

    double total_sum = 0.0;
    uint64_t num_subsets = 1ULL << (n - 1);
    uint64_t prev_gray = 0;

    for (uint64_t i = 0; i < num_subsets; ++i) {
        uint64_t gray = i ^ (i >> 1);

        if (i > 0) {
            uint64_t diff = gray ^ prev_gray;
            size_t bit_idx = (size_t)__builtin_ctzll(diff) + 1; /* δ₁ зафіксовано */

            /* Перемикаємо знак δ[bit_idx] */
            delta[bit_idx] = -delta[bit_idx];
            double factor = 2.0 * delta[bit_idx];

            for (size_t r = 0; r < n; ++r) {
                row_sum[r] += factor * matrix[r * n + bit_idx];
            }
        }

        /* Обчислюємо добуток знаків та рядкових сум */
        double prod = 1.0;
        for (size_t r = 0; r < n; ++r) {
            prod *= row_sum[r];
        }

        double delta_prod = 1.0;
        for (size_t j = 0; j < n; ++j) {
            delta_prod *= delta[j];
        }

        total_sum += delta_prod * prod;
        prev_gray = gray;
    }

    free(delta);
    free(row_sum);

    return total_sum / (double)(1ULL << (n - 1));
}
