#include <stdio.h>
#include <stdbool.h>
#include <stddef.h>

/*
 * Дескриптор матриці з підтримкою віртуальної одиничної матриці.
 */
typedef struct {
    size_t rows;
    size_t cols;
    const double *data; /* NULL, якщо матриця є віртуальною одиничною */
    bool is_identity;
} matrix_view_t;

static inline double matrix_get(const matrix_view_t *mat, size_t r, size_t c) {
    if (mat->is_identity) {
        return (r == c) ? 1.0 : 0.0;
    }
    return mat->data[r * mat->cols + c];
}

/*
 * Оптимізоване множення: якщо другий операнд — одинична матриця,
 * виділення пам'яті та N^3 обчислень не потрібні.
 */
bool matrix_multiply_optimized(
    const matrix_view_t *A,
    const matrix_view_t *B,
    double *out_result
) {
    if (A->cols != B->rows) {
        return false;
    }

    if (B->is_identity) {
        /* A * I = A: пряме копіювання без множень */
        size_t total_elements = A->rows * A->cols;
        for (size_t i = 0; i < total_elements; ++i) {
            out_result[i] = A->data[i];
        }
        return true;
    }

    /* Стандартне множення O(N^3) для загального випадку */
    for (size_t i = 0; i < A->rows; ++i) {
        for (size_t j = 0; j < B->cols; ++j) {
            double sum = 0.0;
            for (size_t k = 0; k < A->cols; ++k) {
                sum += matrix_get(A, i, k) * matrix_get(B, k, j);
            }
            out_result[i * B->cols + j] = sum;
        }
    }
    return true;
}
