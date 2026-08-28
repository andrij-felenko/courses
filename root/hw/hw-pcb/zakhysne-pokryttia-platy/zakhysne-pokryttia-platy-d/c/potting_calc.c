/* potting_calc.c — Інженерний калькулятор теплових та механічних напружень заливки плати */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    const char* name;
    double thermal_conductivity; /* Вт/(м·К) */
    double young_modulus_mpa;    /* Модуль Юнга, МПа */
    double cte_ppm;              /* КТР, ppm/K (10^-6 1/K) */
    double density_g_cm3;        /* Густина, г/см³ */
    double poisson_ratio;        /* Коефіцієнт Пуассона (зазвичай 0.35-0.40) */
} MaterialProps;

typedef struct {
    double box_length_mm;
    double box_width_mm;
    double box_height_mm;
    double pcb_length_mm;
    double pcb_width_mm;
    double pcb_thickness_mm;
    double components_vol_cm3;
    double coating_thickness_mm; /* Товщина шару над гарячим чіпом */
    double chip_area_mm2;        /* Площа контакту чіпа */
    double temp_delta_c;         /* Перепад температур ΔT (°C) */
    double component_cte_ppm;    /* КТР матеріалу компонента (Si = 3, MLCC = 9) */
} PottingInput;

typedef struct {
    double net_volume_cm3;
    double compound_mass_g;
    double thermal_resistance_k_w;
    double cte_stress_mpa;
    bool stress_warning;
} PottingResult;

bool calculate_potting(const MaterialProps* mat, const PottingInput* in, PottingResult* out) {
    if (!mat || !in || !out) return false;
    if (mat->thermal_conductivity <= 0.0 || mat->density_g_cm3 <= 0.0) return false;
    if (in->box_length_mm <= 0.0 || in->box_width_mm <= 0.0 || in->box_height_mm <= 0.0) return false;

    /* 1. Об'ємний та масовий розрахунок */
    double box_vol_cm3 = (in->box_length_mm * in->box_width_mm * in->box_height_mm) / 1000.0;
    double pcb_vol_cm3 = (in->pcb_length_mm * in->pcb_width_mm * in->pcb_thickness_mm) / 1000.0;
    out->net_volume_cm3 = box_vol_cm3 - pcb_vol_cm3 - in->components_vol_cm3;
    if (out->net_volume_cm3 < 0.0) out->net_volume_cm3 = 0.0;
    out->compound_mass_g = out->net_volume_cm3 * mat->density_g_cm3;

    /* 2. Тепловий опір шару заливки над чіпом: R_th = t / (k * A) */
    double t_m = in->coating_thickness_mm / 1000.0;
    double a_m2 = in->chip_area_mm2 / 1000000.0;
    if (a_m2 > 0.0) {
        out->thermal_resistance_k_w = t_m / (mat->thermal_conductivity * a_m2);
    } else {
        out->thermal_resistance_k_w = 0.0;
    }

    /* 3. Механічне напруження від невідповідності КТР: σ = E * |Δα| * ΔT / (1 - ν) */
    double delta_cte = fabs(mat->cte_ppm - in->component_cte_ppm) * 1e-6;
    double denom = 1.0 - mat->poisson_ratio;
    if (denom <= 0.01) denom = 0.65;
    out->cte_stress_mpa = (mat->young_modulus_mpa * delta_cte * in->temp_delta_c) / denom;

    /* Поріг небезпеки: механічне напруження > 40 МПа небезпечне для крихких MLCC */
    out->stress_warning = (out->cte_stress_mpa > 40.0);
    return true;
}

int main(void) {
    MaterialProps materials[] = {
        {"PU-T1 (Теплопровідний поліуретан)", 0.95, 80.0, 70.0, 1.75, 0.38},
        {"EP-R1 (Жорсткий епоксидний компаунд)", 0.75, 3200.0, 35.0, 1.85, 0.35},
        {"SI-T1 (Теплопровідний силікон)", 1.50, 15.0, 180.0, 2.35, 0.45}
    };

    PottingInput input = {
        .box_length_mm = 80.0,
        .box_width_mm = 60.0,
        .box_height_mm = 20.0,
        .pcb_length_mm = 75.0,
        .pcb_width_mm = 55.0,
        .pcb_thickness_mm = 1.6,
        .components_vol_cm3 = 8.5,
        .coating_thickness_mm = 3.0,
        .chip_area_mm2 = 144.0,       /* QFN чіп 12x12 мм */
        .temp_delta_c = 85.0,         /* Робочий перепад від +25 до -60 °C або до +110 °C */
        .component_cte_ppm = 9.0      /* Керамічний конденсатор MLCC */
    };

    printf("=== РОЗРАХУНОК ОБСЯГУ, ТЕПЛА ТА СТРЕСУ ЗАЛИВКИ ПЛАТИ ===\n");
    printf("Розміри корпусу: %.1f x %.1f x %.1f мм\n", input.box_length_mm, input.box_width_mm, input.box_height_mm);
    printf("Чіп: площа %.1f мм², шар заливки %.1f мм, ΔT = %.1f °C\n\n",
           input.chip_area_mm2, input.coating_thickness_mm, input.temp_delta_c);

    for (size_t i = 0; i < sizeof(materials)/sizeof(materials[0]); ++i) {
        PottingResult res;
        if (calculate_potting(&materials[i], &input, &res)) {
            printf("Матеріал: %s\n", materials[i].name);
            printf("  - Чистий об'єм компаунда : %.2f см³\n", res.net_volume_cm3);
            printf("  - Необхідна маса заливки : %.2f г\n", res.compound_mass_g);
            printf("  - Тепловий опір шару R_th: %.2f K/Вт\n", res.thermal_resistance_k_w);
            printf("  - Термонапруження σ (CTE): %.2f МПа %s\n",
                   res.cte_stress_mpa, res.stress_warning ? "[УВАГА: РИЗИК СКОЛУ MLCC!]" : "[БЕЗПЕЧНО]");
            printf("------------------------------------------------------------\n");
        }
    }
    return 0;
}
