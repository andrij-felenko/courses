#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Рекурсивна функція обходу всіх перестановок */
static void permute_naive(const double *matrix, size_t n, size_t row,
                          size_t *p, uint8_t *used, double *acc) {
    if (row == n) {
        double prod = 1.0;
        for (size_t i = 0; i < n; ++i) {
            prod *= matrix[i * n + p[i]];
        }
        *acc += prod;
        return;
    }

    for (size_t col = 0; col < n; ++col) {
        if (!used[col]) {
            used[col] = 1;
            p[row] = col;
            permute_naive(matrix, n, row + 1, p, used, acc);
            used[col] = 0;
        }
    }
}

/* Публічна функція наївного обчислення перманента */
double permanent_naive(const double *matrix, size_t n) {
    if (!matrix || n == 0) return 0.0;
    
    size_t *p = (size_t *)malloc(n * sizeof(size_t));
    uint8_t *used = (uint8_t *)calloc(n, sizeof(uint8_t));
    double result = 0.0;

    if (p && used) {
        permute_naive(matrix, n, 0, p, used, &result);
    }

    free(p);
    free(used);
    return result;
}
