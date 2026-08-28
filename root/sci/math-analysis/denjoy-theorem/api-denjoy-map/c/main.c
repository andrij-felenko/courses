#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "denjoy_map.h"

/* Контекст користувацьких параметрів відображення */
typedef struct {
    double omega;
    double k;
} arnold_params_t;

/* Функція підйому F(x) */
static double arnold_lift(double x, void *user_data) {
    arnold_params_t *p = (arnold_params_t *)user_data;
    return x + p->omega - (p->k / (2.0 * M_PI)) * sin(2.0 * M_PI * x);
}

/* Функція похідної F'(x) */
static double arnold_prime(double x, void *user_data) {
    arnold_params_t *p = (arnold_params_t *)user_data;
    return 1.0 - p->k * cos(2.0 * M_PI * x);
}

int main(void) {
    arnold_params_t params = {
        .omega = (sqrt(5.0) - 1.0) / 2.0,  /* Золотий перетин */
        .k = 0.4                            /* Субкритичний режим K < 1 */
    };

    denjoy_map_config_t config;
    if (denjoy_map_init(&config, arnold_lift, arnold_prime, &params) != DENJOY_OK) {
        fprintf(stderr, "Помилка ініціалізації конфігурації\n");
        return 1;
    }

    /* Перевірка гладкості диффеоморфізму */
    double min_deriv = 0.0;
    if (denjoy_verify_diffeomorphism(&config, 1000, &min_deriv) != DENJOY_OK) {
        printf("Увага: відображення втратило монотонність! Мін. похідна = %.6f\n", min_deriv);
        return 1;
    }
    printf("Відображення є строго монотонним. Мін. похідна = %.6f\n", min_deriv);

    /* Обчислення числа обертання */
    denjoy_rotation_info_t rot_info;
    if (denjoy_compute_rotation_number(&config, 0.0, 500000L, &rot_info) == DENJOY_OK) {
        printf("Обчислене число обертання rho(f) = %.8f\n", rot_info.rotation_number);
    }

    /* Перевірка нерівності Данжуа для q = 610 */
    denjoy_distortion_stats_t dist_stats;
    if (denjoy_check_distortion(&config, 610, 2000, &dist_stats) == DENJOY_OK) {
        printf("--- Спотворення для q = 610 ---\n");
        printf("Мін. похідна q-ї ітерації: %.6f\n", dist_stats.min_derivative);
        printf("Макс. похідна q-ї ітерації: %.6f\n", dist_stats.max_derivative);
        printf("Логарифмічне спотворення:  %.6f (<= Var(log f'))\n", dist_stats.log_distortion);
    }

    return 0;
}
