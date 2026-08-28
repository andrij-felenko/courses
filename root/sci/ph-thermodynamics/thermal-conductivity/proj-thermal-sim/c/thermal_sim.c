/* thermal_sim.c — Симуляція 1D теплопровідності методом FTCS мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double lambda; /* Вт/(м·К) */
    double rho;    /* кг/м³ */
    double cp;     /* Дж/(кг·К) */
    double alpha;  /* м²/с */
} Material;

int main(void) {
    const double length = 0.10;    /* 10 см */
    const int N = 100;             /* 100 вузлів сітки */
    const double dx = length / (N - 1);
    const double total_time = 5.0; /* 5 секунд симуляції */

    /* Властивості матеріалів */
    Material copper = {390.0, 8960.0, 385.0, 390.0 / (8960.0 * 385.0)};
    Material steel  = {15.0,  7900.0, 500.0, 15.0  / (7900.0 * 500.0)};

    /* Максимальна температуропровідність визначає крок часу */
    double max_alpha = (copper.alpha > steel.alpha) ? copper.alpha : steel.alpha;
    double dt = 0.45 * (dx * dx) / max_alpha; /* Запасовий коефіцієнт 0.45 < 0.5 */

    int steps = (int)(total_time / dt);

    double *T = (double *)malloc(N * sizeof(double));
    double *T_new = (double *)malloc(N * sizeof(double));
    double *alpha_grid = (double *)malloc(N * sizeof(double));

    if (!T || !T_new || !alpha_grid) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(T); free(T_new); free(alpha_grid);
        return 1;
    }

    /* Ліва половина (0..N/2) — мідь, права (N/2..N) — сталь */
    int mid = N / 2;
    for (int i = 0; i < N; i++) {
        alpha_grid[i] = (i < mid) ? copper.alpha : steel.alpha;
        T[i] = 20.0; /* Початкова температура 20 °C */
    }

    /* Граничні умови */
    T[0] = 100.0;     /* Лівий кінець 100 °C */
    T[N - 1] = 20.0;  /* Правий кінець 20 °C */

    /* Часовий цикл */
    for (int step = 0; step < steps; step++) {
        T_new[0] = 100.0;
        T_new[N - 1] = 20.0;

        for (int i = 1; i < N - 1; i++) {
            double fo = alpha_grid[i] * dt / (dx * dx);
            T_new[i] = T[i] + fo * (T[i + 1] - 2.0 * T[i] + T[i - 1]);
        }

        /* Оновлення масиву */
        for (int i = 0; i < N; i++) {
            T[i] = T_new[i];
        }
    }

    printf("=== Профіль температури через %.1f с ===\n", total_time);
    printf("x = 0.00 м (Вхід Cu):   %.2f °C\n", T[0]);
    printf("x = 0.025 м (Середина Cu): %.2f °C\n", T[N / 4]);
    printf("x = 0.050 м (Стик Cu-Steel): %.2f °C\n", T[N / 2]);
    printf("x = 0.075 м (Середина Steel): %.2f °C\n", T[3 * N / 4]);
    printf("x = 0.100 м (Вихід Steel): %.2f °C\n", T[N - 1]);

    free(T);
    free(T_new);
    free(alpha_grid);
    return 0;
}
