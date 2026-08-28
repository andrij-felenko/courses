#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_DIM 16

/* Результат розв'язання цілочислової неоднозначності */
typedef struct {
    double fix1[MAX_DIM];  /* Найкращий цілий вектор ǎ₁ */
    double fix2[MAX_DIM];  /* Другий за якістю цілий вектор ǎ₂ */
    double f1;             /* Квадратична нев'язка F(ǎ₁) */
    double f2;             /* Квадратична нев'язка F(ǎ₂) */
    double ratio;          /* Відношення якості F(ǎ₂) / F(ǎ₁) */
    bool fixed;            /* Ознака успішної валідації */
} lambda_result_t;

/* Факторизація Q = L * D * L^T */
static void factorize_ldl(int n, const double *Q, double *L, double *D) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            L[i * n + j] = (i == j) ? 1.0 : 0.0;
        }
        D[i] = 0.0;
    }

    for (int i = n - 1; i >= 0; i--) {
        D[i] = Q[i * n + i];
        for (int j = i + 1; j < n; j++) {
            double lij = L[j * n + i];
            D[i] -= lij * lij * D[j];
        }
        if (D[i] <= 0.0) D[i] = 1e-12; /* Захист від втрати додатної визначеності */

        for (int j = 0; j < i; j++) {
            double sum = Q[i * n + j];
            for (int k = i + 1; k < n; k++) {
                sum -= L[k * n + i] * L[k * n + j] * D[k];
            }
            L[i * n + j] = sum / D[i];
        }
    }
}

/* Цілочисловий зсув Гаусса для пари індексів (i, j) */
static void gauss_transform(int n, double *L, double *Z, int i, int j) {
    int mu = (int)round(L[i * n + j]);
    if (mu == 0) return;

    for (int k = i; k < n; k++) {
        L[k * n + j] -= (double)mu * L[k * n + i];
    }
    for (int k = 0; k < n; k++) {
        Z[k * n + j] -= (double)mu * Z[k * n + i];
    }
}

/* Перестановка сусідніх координат (i, i+1) та перерахунок LDL^T */
static void swap_coordinates(int n, double *L, double *D, double *Z, int i) {
    int j = i + 1;
    double d1 = D[i], d2 = D[j];
    double lambda = L[j * n + i];
    double delta = d1 + lambda * lambda * d2;

    /* Нові умовні дисперсії */
    D[i] = delta;
    D[j] = (d1 * d2) / delta;
    L[j * n + i] = (lambda * d2) / delta;

    /* Оновлення недіагональних коефіцієнтів у трикутнику */
    for (int k = 0; k < i; k++) {
        double lik = L[i * n + k];
        double ljk = L[j * n + k];
        L[i * n + k] = ljk;
        L[j * n + k] = lik;
    }
    for (int k = j + 1; k < n; k++) {
        double lki = L[k * n + i];
        double lkj = L[k * n + j];
        L[k * n + i] = lki * L[j * n + i] + lkj * (d2 / delta);
        L[k * n + j] = lki - lkj * lambda;
    }

    /* Оновлення унімодулярної матриці Z */
    for (int k = 0; k < n; k++) {
        double zki = Z[k * n + i];
        double zkj = Z[k * n + j];
        Z[k * n + i] = zkj;
        Z[k * n + j] = zki;
    }
}

/* Повна редукція ґратки: Гауссові зсуви + впорядкування за Тойніссеном */
static void reduce_lattice(int n, double *L, double *D, double *Z) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            Z[i * n + j] = (i == j) ? 1.0 : 0.0;
        }
    }

    int i = n - 2;
    while (i >= 0) {
        /* Зсув Гаусса для сусідньої позиції */
        gauss_transform(n, L, Z, i + 1, i);

        double delta = D[i] + L[(i + 1) * n + i] * L[(i + 1) * n + i] * D[i + 1];
        if (delta + 1e-9 < D[i + 1]) {
            swap_coordinates(n, L, D, Z, i);
            /* Повне оновлення вищих елементів стовпця */
            for (int k = i + 1; k < n; k++) {
                for (int m = i; m >= 0; m--) {
                    gauss_transform(n, L, Z, k, m);
                }
            }
            i = n - 2; /* Перезапуск перевірки вниз */
        } else {
            i--;
        }
    }
}

/* Пошук у глибину (DFS) всередині еліпсоїда */
static void search_hyper_ellipsoid(int n, const double *L, const double *D,
                                  const double *z_hat, double *z_fix1, double *z_fix2,
                                  double *f1, double *f2) {
    int i = n - 1;
    double max_dist = 1e9;
    *f1 = max_dist;
    *f2 = max_dist;

    double z[MAX_DIM] = {0};
    double step[MAX_DIM] = {0};
    double dist[MAX_DIM] = {0};
    double z_cond[MAX_DIM] = {0};

    z_cond[i] = z_hat[i];
    z[i] = round(z_cond[i]);
    step[i] = (z_cond[i] >= z[i]) ? 1.0 : -1.0;

    int candidates_found = 0;

    while (true) {
        double diff = z[i] - z_cond[i];
        double new_dist = dist[i] + diff * diff * D[i];

        if (new_dist < max_dist) {
            if (i > 0) {
                /* Спуск на рівень нижче */
                i--;
                dist[i] = new_dist;
                double cond = z_hat[i];
                for (int j = i + 1; j < n; j++) {
                    cond -= L[j * n + i] * (z[j] - z_hat[j]);
                }
                z_cond[i] = cond;
                z[i] = round(z_cond[i]);
                step[i] = (z_cond[i] >= z[i]) ? 1.0 : -1.0;
            } else {
                /* Знайдено цілий вектор-листок */
                if (new_dist < *f1) {
                    *f2 = *f1;
                    memcpy(z_fix2, z_fix1, n * sizeof(double));
                    *f1 = new_dist;
                    memcpy(z_fix1, z, n * sizeof(double));
                } else if (new_dist < *f2) {
                    *f2 = new_dist;
                    memcpy(z_fix2, z, n * sizeof(double));
                }
                candidates_found++;
                if (candidates_found >= 2) {
                    max_dist = *f2; /* Динамічне звуження радіуса гіперсфери */
                }

                /* Альтернативний крок на поточному рівні */
                z[i] += step[i];
                step[i] = -step[i] - ((step[i] > 0) ? 1.0 : -1.0);
            }
        } else {
            /* Підйом назад по дереву */
            if (i == n - 1) break;
            i++;
            z[i] += step[i];
            step[i] = -step[i] - ((step[i] > 0) ? 1.0 : -1.0);
        }
    }
}

/* Загальний виклик методу LAMBDA */
lambda_result_t lambda_resolve(int n, const double *a_hat, const double *Q_a, double ratio_thresh) {
    lambda_result_t res;
    memset(&res, 0, sizeof(res));

    double L[MAX_DIM * MAX_DIM];
    double D[MAX_DIM];
    double Z[MAX_DIM * MAX_DIM];

    factorize_ldl(n, Q_a, L, D);
    reduce_lattice(n, L, D, Z);

    /* ẑ = Zᵀ · â */
    double z_hat[MAX_DIM] = {0};
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            z_hat[i] += Z[j * n + i] * a_hat[j];
        }
    }

    double z_fix1[MAX_DIM] = {0};
    double z_fix2[MAX_DIM] = {0};
    search_hyper_ellipsoid(n, L, D, z_hat, z_fix1, z_fix2, &res.f1, &res.f2);

    /* Зворотне перетворення: ǎ = Z · ž */
    for (int i = 0; i < n; i++) {
        res.fix1[i] = 0.0;
        res.fix2[i] = 0.0;
        for (int j = 0; j < n; j++) {
            res.fix1[i] += Z[i * n + j] * z_fix1[j];
            res.fix2[i] += Z[i * n + j] * z_fix2[j];
        }
    }

    res.ratio = (res.f1 > 1e-12) ? (res.f2 / res.f1) : 999.0;
    res.fixed = (res.ratio >= ratio_thresh);
    return res;
}

int main(void) {
    int n = 3;
    /* Плаваючі неоднозначності з високою кореляцією */
    double a_hat[3] = { 5.45, 12.35, 8.85 };
    double Q_a[9] = {
        6.25,  6.15,  6.05,
        6.15,  6.30,  6.10,
        6.05,  6.10,  6.20
    };

    lambda_result_t res = lambda_resolve(n, a_hat, Q_a, 2.5);

    printf("Float оцінки:   [ %.2f, %.2f, %.2f ]\n", a_hat[0], a_hat[1], a_hat[2]);
    printf("Fixed вектор 1: [ %.0f, %.0f, %.0f ]  (F1 = %.5f)\n",
           res.fix1[0], res.fix1[1], res.fix1[2], res.f1);
    printf("Fixed вектор 2: [ %.0f, %.0f, %.0f ]  (F2 = %.5f)\n",
           res.fix2[0], res.fix2[1], res.fix2[2], res.f2);
    printf("Ratio-Test:     %.2f  (поріг 2.5) -> %s\n",
           res.ratio, res.fixed ? "FIXED" : "FLOAT");

    return 0;
}
