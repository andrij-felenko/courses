#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура для представлення зрізаного ряду Діріхле */
typedef struct {
    double* coeff; /* Масив коефіцієнтів a[1..N] (1-indexed) */
    size_t size;   /* Верхня межа N */
} DirichletSeries;

/* Створення та ініціалізація ряду нулями */
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

/* Звільнення динамічної пам'яті */
void dirichlet_free(DirichletSeries* ds) {
    if (ds) {
        free(ds->coeff);
        free(ds);
    }
}

/* Друк коефіцієнтів ряду */
void dirichlet_print(const DirichletSeries* ds, const char* name) {
    if (!ds) return;
    printf("Ряд %s (розмір N = %zu):\n", name, ds->size);
    for (size_t i = 1; i <= ds->size; ++i) {
        printf("  %s(%zu) = %6.2f\n", name, i, ds->coeff[i]);
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

/* Лінійна комбінація: додавання двох рядів */
DirichletSeries* dirichlet_add(const DirichletSeries* a, const DirichletSeries* b) {
    size_t min_n = (a->size < b->size) ? a->size : b->size;
    DirichletSeries* res = dirichlet_create(min_n);
    if (!res) return NULL;

    for (size_t i = 1; i <= min_n; ++i) {
        res->coeff[i] = a->coeff[i] + b->coeff[i];
    }
    return res;
}

/* Масштабування коефіцієнтів на константу */
DirichletSeries* dirichlet_scale(const DirichletSeries* a, double scalar) {
    DirichletSeries* res = dirichlet_create(a->size);
    if (!res) return NULL;

    for (size_t i = 1; i <= a->size; ++i) {
        res->coeff[i] = a->coeff[i] * scalar;
    }
    return res;
}

int main(void) {
    const size_t N = 10;

    /* 1. Створення Дзета-ряду ζ(s): коефіцієнти 1(n) = 1 */
    DirichletSeries* zeta = dirichlet_create(N);
    for (size_t i = 1; i <= N; ++i) {
        zeta->coeff[i] = 1.0;
    }

    /* 2. Обчислення згортки ζ * ζ = d(n) (кількість дільників) */
    DirichletSeries* d_func = dirichlet_convolve(zeta, zeta);
    dirichlet_print(d_func, "d (число дільників ζ²)");

    /* 3. Обчислення оберненого ряду ζ⁻¹ = μ(n) (функція Мебіуса) */
    DirichletSeries* mobius = dirichlet_invert(zeta);
    dirichlet_print(mobius, "μ (функція Мебіуса ζ⁻¹)");

    /* 4. Створення степеневого ряду N(n) = n */
    DirichletSeries* id_func = dirichlet_create(N);
    for (size_t i = 1; i <= N; ++i) {
        id_func->coeff[i] = (double)i;
    }

    /* 5. Обчислення функції Ейлера φ = μ * N */
    DirichletSeries* phi = dirichlet_convolve(mobius, id_func);
    dirichlet_print(phi, "φ (функція Ейлера μ * N)");

    /* 6. Чисельне обчислення значення ζ(2.0 + 3.5i) */
    double re, im;
    dirichlet_eval(zeta, 2.0, 3.5, &re, &im);
    printf("\nЧисельне значення ζ(2.0 + 3.5i) (N = %zu): %.5f + %.5fi\n", N, re, im);

    /* 7. Очищення виділених ресурсів */
    dirichlet_free(zeta);
    dirichlet_free(d_func);
    dirichlet_free(mobius);
    dirichlet_free(id_func);
    dirichlet_free(phi);

    return 0;
}
