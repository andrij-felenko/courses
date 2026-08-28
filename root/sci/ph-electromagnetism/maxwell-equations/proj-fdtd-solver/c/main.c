/* 1D FDTD Simulation of Maxwell's Equations in Free Space (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 400            /* Кількість осередків просторової сітки */
#define NT 600            /* Кількість кроків за часом */
#define S_COURANT 0.99    /* Число Куранта S = c * dt / dx */

/* Фізичні константи вакууму */
static const double EPS0 = 8.854187817e-12;
static const double MU0  = 1.256637061e-6;

int main(void) {
    const double c0 = 1.0 / sqrt(EPS0 * MU0);
    const double dx = 1e-3;                   /* Крок простору: 1 мм */
    const double dt = S_COURANT * dx / c0;    /* Крок часу за умовою CFL */

    /* Виділення пам'яті під вектори полів */
    double *Ez = (double *)calloc(NX, sizeof(double));
    double *Hy = (double *)calloc(NX - 1, sizeof(double));

    if (!Ez || !Hy) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    /* Коефіцієнти оновлення в різницевих рівняннях */
    const double ch = dt / (MU0 * dx);
    const double ce = dt / (EPS0 * dx);

    /* Змінні для поглинальних межевих умов Мура (Mur ABC) */
    const double abc_coef = (c0 * dt - dx) / (c0 * dt + dx);
    double ez_left_prev = 0.0;
    double ez_right_prev = 0.0;

    /* Параметри Гаусового джерела у центрі сітки */
    const int src_pos = NX / 2;
    const double t0 = 40.0 * dt;
    const double tau = 12.0 * dt;

    /* Головний часловий цикл FDTD */
    for (int n = 0; n < NT; n++) {
        /* 1. Оновлення магнітного поля Hy (крок n + 1/2) */
        for (int i = 0; i < NX - 1; i++) {
            Hy[i] += ch * (Ez[i + 1] - Ez[i]);
        }

        /* Збереження граничних значень для поглинальних умов */
        ez_left_prev = Ez[1];
        ez_right_prev = Ez[NX - 2];

        /* 2. Оновлення електричного поля Ez (крок n + 1) */
        for (int i = 1; i < NX - 1; i++) {
            Ez[i] += ce * (Hy[i] - Hy[i - 1]);
        }

        /* 3. Інжекція Гаусового імпульсу джерела */
        const double time_curr = n * dt;
        const double src_val = exp(-pow((time_curr - t0) / tau, 2.0));
        Ez[src_pos] += src_val;

        /* 4. Застосування поглинальних межевих умов (Mur ABC) */
        Ez[0] = ez_left_prev + abc_coef * (Ez[1] - Ez[0]);
        Ez[NX - 1] = ez_right_prev + abc_coef * (Ez[NX - 2] - Ez[NX - 1]);

        /* Консольний моніторинг кожні 100 кроків */
        if (n % 100 == 0) {
            printf("Крок %3d / %d | Ez[src] = %+.4f | Ez[center+50] = %+.4f\n",
                   n, NT, Ez[src_pos], Ez[src_pos + 50]);
        }
    }

    free(Ez);
    free(Hy);
    return 0;
}
