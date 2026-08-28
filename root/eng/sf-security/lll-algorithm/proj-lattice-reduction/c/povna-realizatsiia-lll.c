#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define LLL_DELTA 0.75

typedef struct {
    int rows;
    int cols;
    int64_t **data;
} IntMatrix;

typedef struct {
    int rows;
    int cols;
    double **data;
} DoubleMatrix;

IntMatrix create_int_matrix(int rows, int cols) {
    IntMatrix m;
    m.rows = rows;
    m.cols = cols;
    m.data = (int64_t **)malloc(rows * sizeof(int64_t *));
    for (int i = 0; i < rows; i++) {
        m.data[i] = (int64_t *)calloc(cols, sizeof(int64_t));
    }
    return m;
}

void free_int_matrix(IntMatrix *m) {
    if (!m || !m->data) return;
    for (int i = 0; i < m->rows; i++) {
        free(m->data[i]);
    }
    free(m->data);
    m->data = NULL;
}

DoubleMatrix create_double_matrix(int rows, int cols) {
    DoubleMatrix m;
    m.rows = rows;
    m.cols = cols;
    m.data = (double **)malloc(rows * sizeof(double *));
    for (int i = 0; i < rows; i++) {
        m.data[i] = (double *)calloc(cols, sizeof(double));
    }
    return m;
}

void free_double_matrix(DoubleMatrix *m) {
    if (!m || !m->data) return;
    for (int i = 0; i < m->rows; i++) {
        free(m->data[i]);
    }
    free(m->data);
    m->data = NULL;
}

/* Обчислення скалярного добутку дійсних векторів */
double dot_product_double(const double *u, const double *v, int dim) {
    double sum = 0.0;
    for (int i = 0; i < dim; i++) {
        sum += u[i] * v[i];
    }
    return sum;
}

/* Оновлення ортогоналізації Грама — Шмідта */
void compute_gram_schmidt(const IntMatrix *B, DoubleMatrix *B_star, DoubleMatrix *mu, double *B_star_norm_sq) {
    int n = B->rows;
    int m = B->cols;

    for (int i = 0; i < n; i++) {
        for (int c = 0; c < m; c++) {
            B_star->data[i][c] = (double)B->data[i][c];
        }

        for (int j = 0; j < i; j++) {
            double dot = 0.0;
            for (int c = 0; c < m; c++) {
                dot += (double)B->data[i][c] * B_star->data[j][c];
            }
            mu->data[i][j] = dot / B_star_norm_sq[j];

            for (int c = 0; c < m; c++) {
                B_star->data[i][c] -= mu->data[i][j] * B_star->data[j][c];
            }
        }
        mu->data[i][i] = 1.0;
        B_star_norm_sq[i] = dot_product_double(B_star->data[i], B_star->data[i], m);
    }
}

/* Розмірне редукування вектора b_k відносно b_j */
void size_reduce(IntMatrix *B, DoubleMatrix *mu, int k, int j) {
    if (fabs(mu->data[k][j]) > 0.5) {
        int64_t q = (int64_t)round(mu->data[k][j]);
        for (int c = 0; c < B->cols; c++) {
            B->data[k][c] -= q * B->data[j][c];
        }
        for (int l = 0; l < j; l++) {
            mu->data[k][l] -= (double)q * mu->data[j][l];
        }
        mu->data[k][j] -= (double)q;
    }
}

/* Обмін двох векторів місцями */
void swap_rows(IntMatrix *B, int i, int j) {
    int64_t *tmp = B->data[i];
    B->data[i] = B->data[j];
    B->data[j] = tmp;
}

/* Головна функція LLL-редукції */
void lll_reduce(IntMatrix *B, double delta) {
    int n = B->rows;
    int m = B->cols;

    DoubleMatrix B_star = create_double_matrix(n, m);
    DoubleMatrix mu = create_double_matrix(n, n);
    double *B_star_norm_sq = (double *)malloc(n * sizeof(double));

    compute_gram_schmidt(B, &B_star, &mu, B_star_norm_sq);

    int k = 1;
    while (k < n) {
        /* Крок 1: Розмірне редукування для пари (k, k-1) */
        size_reduce(B, &mu, k, k - 1);

        /* Крок 2: Перевірка умови Ловаса */
        double lhs = B_star_norm_sq[k];
        double rhs = (delta - mu.data[k][k - 1] * mu.data[k][k - 1]) * B_star_norm_sq[k - 1];

        if (lhs < rhs) {
            /* Умова Ловаса порушена -> Обмін b_k та b_{k-1} */
            swap_rows(B, k, k - 1);
            compute_gram_schmidt(B, &B_star, &mu, B_star_norm_sq);
            if (k > 1) {
                k--;
            }
        } else {
            /* Умова виконана -> Повне розмірне редукування для всіх j < k-1 */
            for (int j = k - 2; j >= 0; j--) {
                size_reduce(B, &mu, k, j);
            }
            k++;
        }
    }

    free(B_star_norm_sq);
    free_double_matrix(&B_star);
    free_double_matrix(&mu);
}
