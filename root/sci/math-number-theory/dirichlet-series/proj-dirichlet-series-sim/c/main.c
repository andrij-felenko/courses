#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура для представлення зрізаного ряду Діріхле */
typedef struct {
    double* coeff; /* Масив коефіцієнтів a[1..N] (1-indexed) */
    size_t size;   /* Верхня межа N */
} DirichletSeries;

/* Створення та ініціалізація ряду */
DirichletSeries* dirichlet_create(size_t size) {
    DirichletSeries* ds = (DirichletSeries*)malloc(sizeof(DirichletSeries));
    if (!ds) return NULL;
    ds->size = size;
    ds->coeff = (double*)calloc(size + 1, sizeof(double));
    if (!ds->coeff) {
        free(ds);
        return NULL;
    }
    return ds;
}

/* Звільнення пам'яті */
void dirichlet_free(DirichletSeries* ds) {
    if (ds) {
        free(ds->coeff);
        free(ds);
    }
}

/* Чисельне обчислення значення F(s) для s = sigma + i*t */
void dirichlet_eval(const DirichletSeries* ds, double sigma, double t, double* real_out, double* imag_out) {
    double res_re = 0.0;
    double res_im = 0.0;
    
    for (size_t n = 1; n <= ds->size; ++n) {
        if (ds->coeff[n] == 0.0) continue;
        
        double norm = pow((double)n, -sigma);
        double angle = -t * log((double)n);
        
        res_re += ds->coeff[n] * norm * cos(angle);
        res_im += ds->coeff[n] * norm * sin(angle);
    }
    
    *real_out = res_re;
    *imag_out = res_im;
}

/* Алгоритм швидкої згортки за O(N log N) */
DirichletSeries* dirichlet_convolve(const DirichletSeries* a, const DirichletSeries* b) {
    size_t min_n = (a->size < b->size) ? a->size : b->size;
    DirichletSeries* res = dirichlet_create(min_n);
    if (!res) return NULL;

    for (size_t i = 1; i <= min_n; ++i) {
        if (a->coeff[i] == 0.0) continue;
        for (size_t j = 1; i * j <= min_n; ++j) {
            res->coeff[i * j] += a->coeff[i] * b->coeff[j];
        }
    }
    return res;
}

/* Обчислення оберненого ряду b = a⁻¹ відносно згортки */
DirichletSeries* dirichlet_invert(const DirichletSeries* a) {
    if (a->size == 0 || a->coeff[1] == 0.0) return NULL;

    DirichletSeries* inv = dirichlet_create(a->size);
    if (!inv) return NULL;

    inv->coeff[1] = 1.0 / a->coeff[1];

    for (size_t n = 2; n <= a->size; ++n) {
        double sum = 0.0;
        for (size_t d = 2; d <= n; ++d) {
            if (n % d == 0) {
                sum += a->coeff[d] * inv->coeff[n / d];
            }
        }
        inv->coeff[n] = -sum / a->coeff[1];
    }
    return inv;
}

int main(void) {
    size_t N = 10;
    DirichletSeries* zeta = dirichlet_create(N);
    for (size_t i = 1; i <= N; ++i) {
        zeta->coeff[i] = 1.0; /* ζ(s) має коефіцієнти a[n] = 1 */
    }

    DirichletSeries* d_func = dirichlet_convolve(zeta, zeta);
    printf("Коефіцієнти ζ(s)² (число дільників d(n)):\n");
    for (size_t i = 1; i <= N; ++i) {
        printf("d(%zu) = %.0f\n", i, d_func->coeff[i]);
    }

    double re, im;
    dirichlet_eval(zeta, 2.0, 3.5, &re, &im);
    printf("\nζ(2.0 + 3.5i) (зрізана до N=10): %.5f + %.5fi\n", re, im);

    dirichlet_free(zeta);
    dirichlet_free(d_func);
    return 0;
}
