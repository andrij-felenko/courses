/* Implementation in C (C99 standard) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

/* Структура стану 2D осцилятора */
typedef struct {
    double x;   /* координата зміщення */
    double v;   /* швидкість dx/dt */
} State;

/* Параметри осцилятора Дуффінга */
typedef struct {
    double gamma; /* коефіцієнт згасання */
    double f0;    /* амплітуда зовнішнього збудження */
    double omega; /* частота збудження */
} DuffingParams;

/* Правими частини диференціальних рівнянь: dx/dt = v, dv/dt = ... */
static void duffing_rhs(const State* s, double t, const DuffingParams* p, double* dx, double* dv) {
    *dx = s->v;
    *dv = -p->gamma * s->v + s->x - s->x * s->x * s->x + p->f0 * cos(p->omega * t);
}

/* Один крок інтегрування методом Рунґе-Кутти 4-го порядку (RK4) */
static State rk4_step(State s, double t, double dt, const DuffingParams* p) {
    double k1_x, k1_v;
    double k2_x, k2_v;
    double k3_x, k3_v;
    double k4_x, k4_v;

    duffing_rhs(&s, t, p, &k1_x, &k1_v);

    State s2 = { s.x + 0.5 * dt * k1_x, s.v + 0.5 * dt * k1_v };
    duffing_rhs(&s2, t + 0.5 * dt, p, &k2_x, &k2_v);

    State s3 = { s.x + 0.5 * dt * k2_x, s.v + 0.5 * dt * k2_v };
    duffing_rhs(&s3, t + 0.5 * dt, p, &k3_x, &k3_v);

    State s4 = { s.x + dt * k3_x, s.v + dt * k3_v };
    duffing_rhs(&s4, t + dt, p, &k4_x, &k4_v);

    State result;
    result.x = s.x + (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x);
    result.v = s.v + (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v);
    return result;
}

/* Інтерполяція Ерміта для знаходження стану у точний момент часу t_target */
static State hermite_interpolate(State s1, State s2, double t1, double dt, double t_target, const DuffingParams* p) {
    double s = (t_target - t1) / dt;
    double v1_x, v1_v, v2_x, v2_v;

    duffing_rhs(&s1, t1, p, &v1_x, &v1_v);
    duffing_rhs(&s2, t1 + dt, p, &v2_x, &v2_v);

    double h00 = (1.0 - 3.0 * s * s + 2.0 * s * s * s);
    double h10 = s * (1.0 - s) * (1.0 - s);
    double h01 = s * s * (3.0 - 2.0 * s);
    double h11 = s * s * (s - 1.0);

    State res;
    res.x = h00 * s1.x + h10 * dt * v1_x + h01 * s2.x + h11 * dt * v2_x;
    res.v = h00 * s1.v + h10 * dt * v1_v + h01 * s2.v + h11 * dt * v2_v;
    return res;
}

int main(void) {
    DuffingParams params = { .gamma = 0.2, .f0 = 0.3, .omega = 1.0 };

    double T_period = 2.0 * PI / params.omega;
    double dt = T_period / 500.0; /* 500 кроків на один період збудження */

    State current_state = { .x = 0.1, .v = 0.0 };
    double current_time = 0.0;

    /* Пропускаємо перехідний процес (1000 періодів) */
    size_t transient_periods = 1000;
    size_t steps_per_period = 500;

    for (size_t i = 0; i < transient_periods * steps_per_period; ++i) {
        current_state = rk4_step(current_state, current_time, dt, &params);
        current_time += dt;
    }

    /* Збираємо 5000 точок стробоскопічного перерізу Пуанкаре */
    size_t target_points = 5000;
    double next_cross_time = current_time + T_period;

    FILE* out_file = fopen("poincare_section.dat", "w");
    if (!out_file) {
        perror("Не вдалося відкрити файл для запису");
        return EXIT_FAILURE;
    }

    size_t collected = 0;
    while (collected < target_points) {
        State next_state = rk4_step(current_state, current_time, dt, &params);
        double next_time = current_time + dt;

        /* Перевіряємо, чи перенули ми момент стробоскопічного спалаху */
        if (current_time <= next_cross_time && next_time > next_cross_time) {
            State exact = hermite_interpolate(current_state, next_state, current_time, dt, next_cross_time, &params);
            fprintf(out_file, "%.8f\t%.8f\n", exact.x, exact.v);

            collected++;
            next_cross_time += T_period;
        }

        current_state = next_state;
        current_time = next_time;
    }

    fclose(out_file);
    printf("Обчислення завершено. Записано точок у poincare_section.dat\n");
    return EXIT_SUCCESS;
}
