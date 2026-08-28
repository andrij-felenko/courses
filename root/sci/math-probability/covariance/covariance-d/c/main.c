#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Обчислення нижньотрикутної матриці Холецького: A = L * L^T */
bool cholesky_factorize(const double *a, size_t n, double *l) {
    for (size_t i = 0; i < n * n; ++i) l[i] = 0.0;

    for (size_t j = 0; j < n; ++j) {
        double sum_sq = 0.0;
        for (size_t k = 0; k < j; ++k) {
            sum_sq += l[j * n + k] * l[j * n + k];
        }

        double diag = a[j * n + j] - sum_sq;
        if (diag <= 1e-15) {
            return false; /* Матриця не є строго додатно визначеною */
        }

        double l_jj = sqrt(diag);
        l[j * n + j] = l_jj;
        double inv_l_jj = 1.0 / l_jj;

        for (size_t i = j + 1; i < n; ++i) {
            double sum_prod = 0.0;
            for (size_t k = 0; k < j; ++k) {
                sum_prod += l[i * n + k] * l[j * n + k];
            }
            l[i * n + j] = (a[i * n + j] - sum_prod) * inv_l_jj;
        }
    }
    return true;
}
