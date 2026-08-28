#include <stdio.h>
#include "wireforce.h"

int main(void) {
    /* 1. Задання геометрії шинопроводу 0.4 кВ */
    wf_wire_geometry_t geo = {
        .distance_m = 0.20,       /* 200 мм між фазами */
        .length_m = 1.00,         /* 1.0 м проліт між ізоляторами */
        .bus_width_m = 0.010,     /* 10 мм товщина */
        .bus_height_m = 0.100,    /* 100 мм висота */
        .inclination_rad = 0.0    /* Паралельне розташування */
    };

    /* 2. Параметри короткого замикання (I''k = 50 кА) */
    wf_sc_params_t sc = {
        .initial_ik_ka = 50.0,
        .shock_factor = 1.85,
        .frequency_hz = 50.0,
        .is_three_phase = true
    };

    /* 3. Характеристики матеріалу (Мідь M1t та ізолятор ІОР-10-7.5) */
    wf_material_limits_t mat = {
        .type = WF_MAT_COPPER_HARD,
        .yield_stress_mpa = 200.0,
        .max_insulator_kn = 7.5,
        .safety_factor_req = 1.25
    };

    wf_calc_result_t res;
    wf_status_t status = wf_calculate_busbar_system(&geo, &sc, &mat, &res);

    if (status == WF_SUCCESS) {
        printf("--- АНАЛІЗ УСПІШНИЙ ---\n");
        printf("Ударний струм КЗ: %.2f кА\n", res.peak_current_ka);
        printf("Сила на метр: %.2f кН/м\n", res.force_per_meter_kn_m);
        printf("Напруження в шині: %.2f МПа\n", res.bending_stress_mpa);
        printf("Навантаження на ізолятор: %.2f кН\n", res.insulator_load_kn);
        printf("Запас міцності: %.2f\n", res.actual_safety_factor);
    } else {
        printf("ПОМИЛКА РОЗРАХУНКУ: %s (код %d)\n", 
               wf_status_to_string(status), status);
    }

    return 0;
}
