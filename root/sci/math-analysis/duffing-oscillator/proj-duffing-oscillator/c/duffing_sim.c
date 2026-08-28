/* duffing_sim.c — Чисельне інтегрування осцилятора Дуффінга на C99 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double alpha; /* лінійна жорсткість */
    double beta;  /* кубічна жорсткість */
    double delta; /* коефіцієнт згасання */
    double gamma; /* амплітуда зовнішньої сили */
    double omega; /* частота зовнішньої сили */
} duffing_params_t;

typedef struct {
    double x;
    double v;
} state_t;

/* Обчислення правих частин системи диференціальних рівнянь */
static inline state_t duffing_derivatives(state_t s, double t, const duffing_params_t *p) {
    state_t d;
    d.x = s.v;
    d.v = - p->delta * s.v - p->alpha * s.x - p->beta * s.x * s.x * s.x + p->gamma * cos(p->omega * t);
    return d;
}

/* Одиничний крок методом Рунге-Кутти 4-го порядку (RK4) */
state_t rk4_step(state_t s, double t, double h, const duffing_params_t *p) {
    state_t k1 = duffing_derivatives(s, t, p);
    
    state_t s2 = { s.x + 0.5 * h * k1.x, s.v + 0.5 * h * k1.v };
    state_t k2 = duffing_derivatives(s2, t + 0.5 * h, p);
    
    state_t s3 = { s.x + 0.5 * h * k2.x, s.v + 0.5 * h * k2.v };
    state_t k3 = duffing_derivatives(s3, t + 0.5 * h, p);
    
    state_t s4 = { s.x + h * k3.x, s.v + h * k3.v };
    state_t k4 = duffing_derivatives(s4, t + h, p);
    
    state_t next_s;
    next_s.x = s.x + (h / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
    next_s.v = s.v + (h / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v);
    return next_s;
}

int main(void) {
    /* Параметри двоямного хаотичного осцилятора (Атрактор Уеди / Муна) */
    duffing_params_t params = {
        .alpha = -1.0,
        .beta  =  1.0,
        .delta =  0.2,
        .gamma =  0.3,
        .omega =  1.2
    };

    state_t current_state = { .x = 0.1, .v = 0.0 };
    double t = 0.0;
    
    /* Період зовнішньої сили T_period та крок інтегрування */
    double period = 2.0 * M_PI / params.omega;
    int steps_per_period = 500;
    double h = period / steps_per_period;
    
    int transient_periods = 200;  /* Пропускаємо перехідні процеси */
    int total_poincare_pts = 2000; /* Кількість точок у перерізі Пуанкаре */
    
    FILE *fp_poincare = fopen("poincare_c.dat", "w");
    if (!fp_poincare) {
        perror("Не вдалося відкрити файл poincare_c.dat");
        return EXIT_FAILURE;
    }
    
    /* 1. Пропускаємо перехідний режим */
    long transient_steps = (long)transient_periods * steps_per_period;
    for (long step = 0; step < transient_steps; ++step) {
        current_state = rk4_step(current_state, t, h, params);
        t += h;
    }
    
    /* 2. Запис стробоскопічних точок перерізу Пуанкаре (кожен період T) */
    for (int pt = 0; pt < total_poincare_pts; ++pt) {
        fprintf(fp_poincare, "%.8f\t%.8f\n", current_state.x, current_state.v);
        for (int step = 0; step < steps_per_period; ++step) {
            current_state = rk4_step(current_state, t, h, params);
            t += h;
        }
    }
    
    fclose(fp_poincare);
    printf("Обчислення завершено успішно. Записано %d точок у poincare_c.dat\n", total_poincare_pts);
    return EXIT_SUCCESS;
}
