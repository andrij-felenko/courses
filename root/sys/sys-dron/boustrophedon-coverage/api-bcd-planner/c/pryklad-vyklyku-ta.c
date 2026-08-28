#include "bcd_planner.h"
#include <stdio.h>

int main(void) {
    bcd_config_t cfg = {
        .swath_width = 12.0,
        .lateral_overlap = 0.6,
        .safety_margin = 2.0,
        .min_turn_radius = 5.0,
        .angle_mode = BCD_ANGLE_AUTO_MIN_TURNS,
        .custom_sweep_angle_rad = 0.0
    };

    bcd_context_t *ctx = bcd_create(&cfg);
    if (!ctx) {
        fprintf(stderr, "Помилка виділення пам'яті під планувальник BCD\n");
        return -1;
    }

    /* Зовнішня межа поля (прямокутник 200x120 метрів) */
    bcd_point_t boundary[] = {
        { 0.0, 0.0 }, { 200.0, 0.0 }, { 200.0, 120.0 }, { 0.0, 120.0 }
    };
    bcd_set_boundary(ctx, boundary, 4);

    /* Заборонена зона (будівля посередині поля) */
    bcd_point_t obstacle[] = {
        { 80.0, 40.0 }, { 120.0, 40.0 }, { 120.0, 80.0 }, { 80.0, 80.0 }
    };
    bcd_add_obstacle(ctx, obstacle, 4);

    /* Розрахунок покриття */
    bcd_status_t status = bcd_compute(ctx);
    if (status == BCD_STATUS_OK) {
        size_t wp_count = 0;
        bcd_get_waypoint_count(ctx, &wp_count);

        bcd_metrics_t metrics;
        bcd_get_metrics(ctx, &metrics);

        printf("Успішно сплановано місію:\n");
        printf("  Кількість комірок розкладу: %zu\n", metrics.cell_count);
        printf("  Кількість точок маршруту: %zu\n", wp_count);
        printf("  Робоча довжина галсів: %.1f м\n", metrics.total_work_distance_m);
        printf("  Транзитна довжина: %.1f м\n", metrics.total_transit_distance_m);
    } else {
        fprintf(stderr, "Помилка обчислення розкладу: код %d\n", status);
    }

    bcd_destroy(ctx);
    return 0;
}
