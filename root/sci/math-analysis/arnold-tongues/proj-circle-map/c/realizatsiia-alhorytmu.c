#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double omega;
    double k;
    size_t transient_steps;
    size_t measure_steps;
    double initial_x;
} circle_map_config_t;

typedef struct {
    double rotation_number;
    int numerator;
    int denominator;
    bool is_mode_locked;
} circle_map_result_t;

/* Обчислення підйому синус-кругового відображення */
static inline double circle_map_step(double x, double omega, double k) {
    const double two_pi = 2.0 * M_PI;
    return x + omega - (k / two_pi) * sin(two_pi * x);
}

/* Пошук найближчого раціонального дробу p/q з обмеженням знаменника max_q */
static void find_closest_rational(double w, int max_q, double tol, int *out_p, int *out_q, bool *out_locked) {
    w = w - floor(w); // нормалізація до [0, 1)
    int best_p = 0;
    int best_q = 1;
    double min_diff = fabs(w);

    for (int q = 1; q <= max_q; ++q) {
        int p = (int)round(w * q);
        double diff = fabs(w - (double)p / (double)q);
        if (diff < min_diff) {
            min_diff = diff;
            best_p = p;
            best_q = q;
        }
    }

    *out_p = best_p;
    *out_q = best_q;
    *out_locked = (min_diff <= tol);
}

/* Основна функція моделювання траєкторії та обчислення W */
circle_map_result_t compute_circle_map(const circle_map_config_t *cfg, int max_q, double tol) {
    double x = cfg->initial_x;
    const double omega = cfg->omega;
    const double k = cfg->k;

    /* 1. Фаза перехідного процесу */
    for (size_t i = 0; i < cfg->transient_steps; ++i) {
        x = circle_map_step(x, omega, k);
    }

    /* 2. Вимірювальна фаза */
    const double start_x = x;
    for (size_t i = 0; i < cfg->measure_steps; ++i) {
        x = circle_map_step(x, omega, k);
    }

    const double delta_x = x - start_x;
    const double rot_num = delta_x / (double)cfg->measure_steps;

    /* 3. Ідентифікація резонансного режиму */
    circle_map_result_t res;
    res.rotation_number = rot_num;
    find_closest_rational(rot_num, max_q, tol, &res.numerator, &res.denominator, &res.is_mode_locked);

    return res;
}

int main(void) {
    circle_map_config_t cfg = {
        .omega = 0.33333333,
        .k = 0.8,
        .transient_steps = 10000,
        .measure_steps = 50000,
        .initial_x = 0.1
    };

    circle_map_result_t res = compute_circle_map(&cfg, 16, 1e-4);

    printf("Параметри: Omega = %.4f, K = %.4f\n", cfg.omega, cfg.k);
    printf("Число обертання W = %.6f\n", res.rotation_number);
    if (res.is_mode_locked) {
        printf("Стан: Фазове захоплення на резонансі %d/%d\n", res.numerator, res.denominator);
    } else {
        printf("Стан: Квазіперіодичний рух (поза язиками)\n");
    }

    return 0;
}
