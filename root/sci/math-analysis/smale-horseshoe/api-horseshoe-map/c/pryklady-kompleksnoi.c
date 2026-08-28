#include <stdio.h>
#include <stdlib.h>
#include "horseshoe_c.h"

int main(void) {
    HorseshoeConfig cfg;
    if (horseshoe_init_config(0.35, 2.4, &cfg) != HORSESHOE_SUCCESS) {
        fprintf(stderr, "Помилка: неприпустимі параметри підкови!\n");
        return EXIT_FAILURE;
    }

    HorseshoePoint2D points[3] = {
        { .x = 0.2, .y = 0.1 },
        { .x = 0.5, .y = 0.5 },
        { .x = 0.8, .y = 0.9 }
    };

    printf("--- Драйвер симуляції відображення підкови (C) ---\n");
    for (size_t i = 0; i < 3; ++i) {
        HorseshoePoint2D out_pt;
        HorseshoeStatus status = horseshoe_map_forward(&points[i], &out_pt, &cfg);

        if (status == HORSESHOE_SUCCESS) {
            printf("Точка #%zu: (%.3f, %.3f) -> (%.4f, %.4f)\n", i, points[i].x, points[i].y, out_pt.x, out_pt.y);
        } else if (status == HORSESHOE_ERROR_ESCAPED_DOMAIN) {
            printf("Точка #%zu: (%.3f, %.3f) -> Вилетіла з квадрата S\n", i, points[i].x, points[i].y);
        } else {
            printf("Точка #%zu: Помилка відображення (%d)\n", i, status);
        }
    }

    double dim;
    horseshoe_compute_capacity_dim(&cfg, &dim);
    printf("Фрактальна вимірність інваріантної множини: D_box = %.4f\n", dim);

    return EXIT_SUCCESS;
}
