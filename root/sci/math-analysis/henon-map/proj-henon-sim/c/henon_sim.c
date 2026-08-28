/* henon_sim.c — Моделювання відображення Ено та обчислення показників Ляпунова мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double a;
    double b;
} HenonParams;

typedef struct {
    double x;
    double y;
} Point2D;

/* Один крок відображення Ено */
static inline Point2D henon_step(Point2D pt, HenonParams p) {
    Point2D next;
    next.x = 1.0 - p.a * pt.x * pt.x + pt.y;
    next.y = p.b * pt.x;
    return next;
}

/* Обчислення найбільшого показника Ляпунова */
double compute_lyapunov_c(HenonParams p, Point2D start, size_t transient, size_t steps) {
    Point2D pt = start;

    /* 1. Пропускаємо перехідний процес */
    for (size_t i = 0; i < transient; ++i) {
        pt = henon_step(pt, p);
        if (fabs(pt.x) > 1e6) return -1.0; /* Атрактор розрушився */
    }

    /* 2. Ініціалізуємо дотичний вектор розходження */
    double dx = 1.0;
    double dy = 0.0;
    double log_sum = 0.0;

    for (size_t i = 0; i < steps; ++i) {
        /* Множення на матрицю Якобі J(x,y) */
        double next_dx = -2.0 * p.a * pt.x * dx + dy;
        double next_dy = p.b * dx;

        /* Обчислюємо довжину збурення */
        double norm = sqrt(next_dx * next_dx + next_dy * next_dy);
        if (norm < 1e-12) break;

        log_sum += log(norm);

        /* Нормалізуємо дотичний вектор */
        dx = next_dx / norm;
        dy = next_dy / norm;

        /* Крок базової траєкторії */
        pt = henon_step(pt, p);
    }

    return log_sum / (double)steps;
}

int main(void) {
    HenonParams params = { .a = 1.4, .b = 0.3 };
    Point2D init_state = { .x = 0.1, .y = 0.1 };

    double lyap = compute_lyapunov_c(params, init_state, 1000, 100000);
    printf("Показник Ляпунова (C): lambda_1 = %.5f\n", lyap);

    return 0;
}
