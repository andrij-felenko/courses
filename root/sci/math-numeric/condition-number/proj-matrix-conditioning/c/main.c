#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Створення динамічної матриці розміру n x n */
static double* allocate_matrix(int n) {
    return (double*)malloc((size_t)(n * n) * sizeof(double));
}

/* Генерація матриці Гільберта H[i, j] = 1.0 / (i + j + 1) */
static void fill_hilbert(int n, double* H) {
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            H[i * n + j] = 1.0 / ((double)(i + j + 1));
        }
    }
}

/* Обчислення норми 1 матриці: максимум сум абсолютних значень по стовпцях */
static double norm_1(int n, const double* A) {
    double max_col = 0.0;
    for (int j = 0; j < n; ++j) {
        double col_sum = 0.0;
        for (int i = 0; i < n; ++i) {
            col_sum += fabs(A[i * n + j]);
        }
        if (col_sum > max_col) {
            max_col = col_sum;
        }
    }
    return max_col;
}

/* Розв'язання A * x = b методом Гаусса з частковим півотингом */
static int solve_gauss(int n, const double* A, const double* b, double* x) {
    double* A_w = allocate_matrix(n);
    double* b_w = (double*)malloc((size_t)n * sizeof(double));
    if (!A_w || !b_w) {
        free(A_w);
        free(b_w);
        return -1;
    }

    for (int i = 0; i < n * n; ++i) A_w[i] = A[i];
    for (int i = 0; i < n; ++i) b_w[i] = b[i];

    for (int k = 0; k < n - 1; ++k) {
        int pivot = k;
        double max_val = fabs(A_w[k * n + k]);
        for (int i = k + 1; i < n; ++i) {
            double v = fabs(A_w[i * n + k]);
            if (v > max_val) {
                max_val = v;
                pivot = i;
            }
        }

        if (max_val < 1e-15) {
            free(A_w);
            free(b_w);
            return -1; /* Матриця чисельно сингулярна */
        }

        if (pivot != k) {
            for (int j = k; j < n; ++j) {
                double tmp = A_w[k * n + j];
                A_w[k * n + j] = A_w[pivot * n + j];
                A_w[pivot * n + j] = tmp;
            }
            double tmp_b = b_w[k];
            b_w[k] = b_w[pivot];
            b_w[pivot] = tmp_b;
        }

        for (int i = k + 1; i < n; ++i) {
            double factor = A_w[i * n + k] / A_w[k * n + k];
            for (int j = k; j < n; ++j) {
                A_w[i * n + j] -= factor * A_w[k * n + j];
            }
            b_w[i] -= factor * b_w[k];
        }
    }

    /* Зворотний хід */
    for (int i = n - 1; i >= 0; --i) {
        double sum = 0.0;
        for (int j = i + 1; j < n; ++j) {
            sum += A_w[i * n + j] * x[j];
        }
        x[i] = (b_w[i] - sum) / A_w[i * n + i];
    }

    free(A_w);
    free(b_w);
    return 0;
}

/* Регуляризація Тихонова: (AᵀA + λ²I) x = Aᵀb */
static int solve_tikhonov(int n, const double* A, const double* b, double lambda, double* x) {
    double* AtA = allocate_matrix(n);
    double* Atb = (double*)malloc((size_t)n * sizeof(double));
    if (!AtA || !Atb) {
        free(AtA);
        free(Atb);
        return -1;
    }

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            double sum = 0.0;
            for (int k = 0; k < n; ++k) {
                sum += A[k * n + i] * A[k * n + j];
            }
            if (i == j) sum += lambda * lambda;
            AtA[i * n + j] = sum;
        }
        double b_sum = 0.0;
        for (int k = 0; k < n; ++k) {
            b_sum += A[k * n + i] * b[k];
        }
        Atb[i] = b_sum;
    }

    int res = solve_gauss(n, AtA, Atb, x);
    free(AtA);
    free(Atb);
    return res;
}

int main(void) {
    int n = 4;
    double* H = allocate_matrix(n);
    double* x_exact = (double*)malloc((size_t)n * sizeof(double));
    double* b = (double*)malloc((size_t)n * sizeof(double));
    double* x_comp = (double*)malloc((size_t)n * sizeof(double));
    double* x_reg = (double*)malloc((size_t)n * sizeof(double));

    fill_hilbert(n, H);
    for (int i = 0; i < n; ++i) x_exact[i] = 1.0;

    /* b = H * x_exact */
    for (int i = 0; i < n; ++i) {
        b[i] = 0.0;
        for (int j = 0; j < n; ++j) {
            b[i] += H[i * n + j] * x_exact[j];
        }
    }

    solve_gauss(n, H, b, x_comp);
    solve_tikhonov(n, H, b, 1e-4, x_reg);

    printf("H_4 norm_1 = %.4f\n", norm_1(n, H));
    printf("Розв'язок Гаусса: [%.6f, %.6f, %.6f, %.6f]\n", x_comp[0], x_comp[1], x_comp[2], x_comp[3]);
    printf("Регуляризований:  [%.6f, %.6f, %.6f, %.6f]\n", x_reg[0], x_reg[1], x_reg[2], x_reg[3]);

    free(H);
    free(x_exact);
    free(b);
    free(x_comp);
    free(x_reg);
    return 0;
}
