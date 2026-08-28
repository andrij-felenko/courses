#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Припускаємо наявність заголовочного файла C-API */
#include "circle_map.h"

int main(void) {
    circle_map_config_t cfg = {
        .omega = 0.5,
        .k = 0.7,
        .transient_steps = 10000,
        .measure_steps = 50000,
        .initial_x = 0.2
    };

    circle_map_result_t result;
    circle_map_status_t status = circle_map_solve(&cfg, 16, 1e-4, &result);

    if (status != CIRCLE_MAP_SUCCESS) {
        fprintf(stderr, "Помилка обчислення: код %d\n", status);
        return EXIT_FAILURE;
    }

    printf("=== Результати обчислення через C-API ===\n");
    printf("Число обертання W: %.6f\n", result.rotation_number);
    printf("Показник Ляпунова lambda: %.6f\n", result.lyapunov_exponent);

    if (result.is_locked) {
        printf("Статус: Захоплення фази на резонансі %d/%d\n", result.numerator, result.denominator);
    } else {
        printf("Статус: Квазіперіодичний режим\n");
    }

    /* Пошук меж язика 1/2 при K = 0.7 */
    double w_left = 0.0, w_right = 0.0;
    status = circle_map_find_tongue_boundaries(0.7, 1, 2, 1e-6, &w_left, &w_right);
    if (status == CIRCLE_MAP_SUCCESS) {
        printf("Межі язика 1/2 при K=0.7: Omega in [%.6f, %.6f], ширина = %.6f\n",
               w_left, w_right, w_right - w_left);
    }

    return EXIT_SUCCESS;
}
