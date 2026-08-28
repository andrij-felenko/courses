#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define EPSILON 1e-12

typedef enum {
    COV_SUCCESS = 0,
    COV_ERR_INVALID_ARG = 1,
    COV_ERR_NOT_ENOUGH_SAMPLES = 2,
    COV_ERR_NOT_POSITIVE_DEFINITE = 3
} CovStatus;

/* Обчислення вектора середніх і незсуненої коваріаційної матриці */
CovStatus compute_sample_covariance(
    const double *samples, /* масив розміру N * D (row-major) */
    size_t n,              /* кількість спостережень N */
    size_t d,              /* розмірність вектора D */
    double *out_mean,      /* буфер вихідного вектора середніх розміру D */
    double *out_cov        /* буфер вихідної матриці розміру D * D */
) {
    if (!samples || !out_mean || !out_cov || d == 0) {
        return COV_ERR_INVALID_ARG;
    }
    if (n < 2) {
        return COV_ERR_NOT_ENOUGH_SAMPLES;
    }

    /* 1. Обчислення вектора вибіркових середніх */
    for (size_t j = 0; j < d; ++j) {
        double sum = 0.0;
        for (size_t k = 0; k < n; ++k) {
            sum += samples[k * d + j];
        }
        out_mean[j] = sum / (double)n;
    }

    /* 2. Обчислення незсуненої матриці коваріації з поправкою Бесселя (N - 1) */
    double inv_df = 1.0 / (double)(n - 1);
    for (size_t i = 0; i < d; ++i) {
        for (size_t j = 0; j <= i; ++j) {
            double acc = 0.0;
            for (size_t k = 0; k < n; ++k) {
                double diff_i = samples[k * d + i] - out_mean[i];
                double diff_j = samples[k * d + j] - out_mean[j];
                acc += diff_i * diff_j;
            }
            double cov_val = acc * inv_df;
            out_cov[i * d + j] = cov_val;
            out_cov[j * d + i] = cov_val; /* симетричне заповнення */
        }
    }

    return COV_SUCCESS;
}

/* Розклад Холецького: A = L * L^T (A — симетрична, D x D) */
CovStatus cholesky_decompose(
    const double *a, /* вхідна матриця D * D */
    size_t d,        /* розмірність D */
    double *out_l    /* вихідна нижньотрикутна матриця L (D * D) */
) {
    if (!a || !out_l || d == 0) {
        return COV_ERR_INVALID_ARG;
    }

    /* Ініціалізація нулями */
    for (size_t i = 0; i < d * d; ++i) {
        out_l[i] = 0.0;
    }

    for (size_t j = 0; j < d; ++j) {
        double sum_sq = 0.0;
        for (size_t k = 0; k < j; ++k) {
            double val = out_l[j * d + k];
            sum_sq += val * val;
        }

        double diag_diff = a[j * d + j] - sum_sq;
        if (diag_diff <= EPSILON) {
            return COV_ERR_NOT_POSITIVE_DEFINITE;
        }

        double l_jj = sqrt(diag_diff);
        out_l[j * d + j] = l_jj;
        double inv_l_jj = 1.0 / l_jj;

        for (size_t i = j + 1; i < d; ++i) {
            double sum_prod = 0.0;
            for (size_t k = 0; k < j; ++k) {
                sum_prod += out_l[i * d + k] * out_l[j * d + k];
            }
            out_l[i * d + j] = (a[i * d + j] - sum_prod) * inv_l_jj;
        }
    }

    return COV_SUCCESS;
}

/* Генерація одного корельованого вектора: y = mean + L * z */
void transform_correlated_noise(
    const double *l,      /* нижньотрикутна матриця Холецького D * D */
    const double *mean,   /* вектор середніх D */
    const double *z,      /* некорельований білий шум N(0, 1) розміру D */
    size_t d,
    double *out_y         /* результуючий вектор D */
) {
    for (size_t i = 0; i < d; ++i) {
        double acc = mean ? mean[i] : 0.0;
        for (size_t k = 0; k <= i; ++k) {
            acc += l[i * d + k] * z[k];
        }
        out_y[i] = acc;
    }
}
