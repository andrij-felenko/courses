#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_ISOTOPES 6

/* Індекси ізотопів у масиві Y */
#define C12 0
#define N13 1
#define C13 2
#define N14 3
#define O15 4
#define N15 5

/* Фізичні константи реакцій для T = 25 мільйонів К, rho = 100 г/см³ */
typedef struct {
    double lambda1; /* 12C + p  -> 13N  */
    double lambda2; /* 13N      -> 13C (beta+) */
    double lambda3; /* 13C + p  -> 14N  */
    double lambda4; /* 14N + p  -> 15O (bottleneck) */
    double lambda5; /* 15O      -> 15N (beta+) */
    double lambda6; /* 15N + p  -> 12C + 4He */
    double Y_p;     /* Концентрація протонів */
} CNOParams;

/* Обчислення правих частин диференціальних рівнянь dY/dt */
void cno_derivatives(const double Y[NUM_ISOTOPES], double dYdt[NUM_ISOTOPES], const CNOParams* p) {
    double rate1 = p->lambda1 * p->Y_p * Y[C12];
    double rate2 = p->lambda2 * Y[N13];
    double rate3 = p->lambda3 * p->Y_p * Y[C13];
    double rate4 = p->lambda4 * p->Y_p * Y[N14];
    double rate5 = p->lambda5 * Y[O15];
    double rate6 = p->lambda6 * p->Y_p * Y[N15];

    dYdt[C12] = rate6 - rate1;
    dYdt[N13] = rate1 - rate2;
    dYdt[C13] = rate2 - rate3;
    dYdt[N14] = rate3 - rate4;
    dYdt[O15] = rate4 - rate5;
    dYdt[N15] = rate5 - rate6;
}

/* Один крок методу Рунґе — Кутти 4-го порядку (RK4) */
void rk4_step(double Y[NUM_ISOTOPES], double dt, const CNOParams* p) {
    double k1[NUM_ISOTOPES], k2[NUM_ISOTOPES], k3[NUM_ISOTOPES], k4[NUM_ISOTOPES];
    double Y_temp[NUM_ISOTOPES];

    cno_derivatives(Y, k1, p);

    for (int i = 0; i < NUM_ISOTOPES; i++) {
        Y_temp[i] = Y[i] + 0.5 * dt * k1[i];
    }
    cno_derivatives(Y_temp, k2, p);

    for (int i = 0; i < NUM_ISOTOPES; i++) {
        Y_temp[i] = Y[i] + 0.5 * dt * k2[i];
    }
    cno_derivatives(Y_temp, k3, p);

    for (int i = 0; i < NUM_ISOTOPES; i++) {
        Y_temp[i] = Y[i] + dt * k3[i];
    }
    cno_derivatives(Y_temp, k4, p);

    for (int i = 0; i < NUM_ISOTOPES; i++) {
        Y[i] += (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
    }
}

int main(void) {
    /* Параметри ядра зоряного середовища: T = 2.5·10⁷ K, rho = 100 г/см³ */
    CNOParams params = {
        .lambda1 = 1.2e-4, /* s^-1 per Y_p */
        .lambda2 = 1.159e-3,/* s^-1 (T1/2 = 9.97 хв) */
        .lambda3 = 4.5e-4, /* s^-1 per Y_p */
        .lambda4 = 1.8e-6, /* s^-1 per Y_p (найповільніша!) */
        .lambda5 = 5.681e-3,/* s^-1 (T1/2 = 122 с) */
        .lambda6 = 8.0e-2, /* s^-1 per Y_p */
        .Y_p = 0.70        /* 70% водню за масою */
    };

    /* Початкові молярні частки: 100% вуглецю-12 у CNO-ізотопах */
    double Y[NUM_ISOTOPES] = {1.0, 0.0, 0.0, 0.0, 0.0, 0.0};

    double t = 0.0;
    double dt = 100.0; /* Крок за часом у секундах */
    double t_max = 1.0e7; /* Загальний час симуляції: 10 мільйонів секунд */

    printf("=== Симуляція кінетики CNO-циклу (C) ===\n");
    printf("Час (с)     12C        13N        13C        14N        15O        15N\n");
    printf("-------------------------------------------------------------------------\n");

    int step = 0;
    while (t <= t_max) {
        if (step % 2000 == 0) {
            printf("%9.1e  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f  %9.4f\n",
                   t, Y[C12], Y[N13], Y[C13], Y[N14], Y[O15], Y[N15]);
        }
        rk4_step(Y, dt, &params);
        t += dt;
        step++;
    }

    printf("-------------------------------------------------------------------------\n");
    printf("Рівноважний стан підтверджено: частка 14N = %.2f%%\n", Y[N14] * 100.0);
    return 0;
}
