#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    size_t dim;
    double *data;
} TriangularMatrix;

/* Ініціалізація нижньотрикутної матриці */
bool tri_matrix_init(TriangularMatrix *mat, size_t dim) {
    mat->dim = dim;
    size_t total_elements = dim * (dim + 1) / 2;
    mat->data = (double *)calloc(total_elements, sizeof(double));
    return mat->data != NULL;
}

/* Звільнення пам'яті */
void tri_matrix_free(TriangularMatrix *mat) {
    if (mat->data) {
        free(mat->data);
        mat->data = NULL;
    }
    mat->dim = 0;
}

/* Пряме отримання елемента (i, j) */
double tri_matrix_get(const TriangularMatrix *mat, size_t i, size_t j) {
    if (j > i || i >= mat->dim) return 0.0;
    size_t flat_idx = i * (i + 1) / 2 + j;
    return mat->data[flat_idx];
}

/* Запис елемента (i, j) */
bool tri_matrix_set(TriangularMatrix *mat, size_t i, size_t j, double val) {
    if (j > i || i >= mat->dim) return false;
    size_t flat_idx = i * (i + 1) / 2 + j;
    mat->data[flat_idx] = val;
    return true;
}

/* Обернена функція: відновлення (i, j) за flat_idx */
void tri_matrix_map_inverse(size_t flat_idx, size_t *out_i, size_t *out_j) {
    uint64_t disc = 8 * (uint64_t)flat_idx + 1;
    uint64_t s = 0;
    while ((s + 1) * (s + 1) <= disc) {
        s++;
    }
    size_t i = (size_t)(s - 1) / 2;
    size_t j = flat_idx - i * (i + 1) / 2;
    
    if (out_i) *out_i = i;
    if (out_j) *out_j = j;
}
