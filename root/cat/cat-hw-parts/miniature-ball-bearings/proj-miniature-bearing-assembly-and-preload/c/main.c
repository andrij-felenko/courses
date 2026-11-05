#include "bearing_calc.h"
#include <stdio.h>

int main(void) {
    BearingParams bearing_608 = {
        .model_name = "608 (DIN 625)",
        .d_inner_mm = 8.0,
        .d_outer_mm = 22.0,
        .width_mm = 7.0,
        .c_dyn_n = 3300.0,
        .c0_stat_n = 1350.0
    };

    PressFitParams fit = {
        .shaft_interference_um = 6.0,
        .friction_coeff = 0.15
    };

    WaveSpringParams spring = {
        .free_height_mm = 2.5,
        .work_height_mm = 1.7,
        .spring_rate_n_mm = 20.0
    };

    AssemblyReport report;
    if (!calculate_assembly(&bearing_608, &fit, &spring, &report)) {
        fprintf(stderr, "Помилка розрахунку монтажних параметрів.\n");
        return 1;
    }

    printf("====================================================\n");
    printf(" Розрахунок монтажу підшипника: %s\n", bearing_608.model_name);
    printf("====================================================\n");
    printf("1. Запресування на вал (d = %.1f мм, натяг = %.1f мкм):\n", bearing_608.d_inner_mm, fit.shaft_interference_um);
    printf("   - Контактний тиск у посадці: %.2f МПа\n", report.contact_pressure_mpa);
    printf("   - Розрахункове осьове зусилля запресування: %.1f Н\n", report.press_force_n);
    printf("\n2. Осьовий попередній натяг хвилястою пружиною:\n");
    printf("   - Фактичне зусилля пружини: %.1f Н\n", report.preload_force_n);
    printf("   - Рекомендований діапазон (0.5%%..2%% C0): %.1f .. %.1f Н\n", report.preload_min_rec_n, report.preload_max_rec_n);
    printf("   - Стан попереднього натягу: %s\n", report.preload_is_safe ? "ОПТИМАЛЬНИЙ" : "НЕВІДПОВІДНИЙ");
    printf("====================================================\n");

    return 0;
}
