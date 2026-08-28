/*
 * proj_mounting_stress_calc.c — Інженерний калькулятор кріплення друкованих плат (C99).
 * Розрахунок осьових сил, тиску під шайбами, деформацій за IPC-9704, CTE та зон заборони.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Константи матеріалів та стандартів */
#define FR4_DEFAULT_E_GPA         20.0     /* Модуль пружності FR-4, ГПа */
#define FR4_DEFAULT_CTE_PPM       15.0     /* CTE FR-4 в площині XY, ppm/K */
#define FR4_MAX_COMPRESS_MPA     250.0     /* Граничний тиск стиску FR-4, МПа */

/* Типи матеріалів корпусу */
typedef enum {
    CHASSIS_ALUMINUM_6061 = 0,
    CHASSIS_STEEL_SPCC,
    CHASSIS_STAINLESS_304,
    CHASSIS_BRASS,
    CHASSIS_POLYCARBONATE_ABS,
    CHASSIS_CUSTOM
} ChassisMaterialType;

/* Вхідна конфігурація кріпильного вузла */
typedef struct {
    double screw_dia_nominal_mm;   /* Номінальний діаметр гвинта (2.0, 2.5, 3.0, 4.0) */
    double drill_hole_dia_mm;      /* Фактичний діаметр отвору на платі */
    double washer_outer_dia_mm;    /* Зовнішній діаметр шайби або головки гвинта */
    double nut_factor_k;           /* Коефіцієнт тертя різьби K (0.12..0.30) */
    double torque_nm;              /* Крутний момент затягування, Н·м */
    double pcb_thickness_mm;       /* Товщина текстоліту плати, мм */
    double standoff_span_mm;       /* Відстань між центрами опорних стійок, мм */
    double standoff_mismatch_mm;   /* Висотне биття стійок (Δh), мм */
    ChassisMaterialType chassis_mat; /* Матеріал шасі */
    double chassis_cte_ppm;        /* CTE шасі (якщо обрано CUSTOM), ppm/K */
    double temp_min_c;             /* Мінімальна робоча температура, °C */
    double temp_max_c;             /* Максимальна робоча температура, °C */
} PcbMountingInput;

/* Результати інженерного розрахунку */
typedef struct {
    /* 1. Силові параметри */
    double clamp_force_n;          /* Осьова сила стискання, Н */
    double washer_contact_area_mm2;/* Площа контакту під шайбою, мм^2 */
    double washer_pressure_mpa;    /* Контактний тиск під шайбою, МПа */
    bool   pressure_safe;          /* Чи не перевищено 250 МПа для FR-4 */

    /* 2. Деформаційні параметри */
    double bending_curvature_m_inv;/* Кривина прогину плати, 1/м */
    double surface_microstrain;    /* Деформація на поверхні текстоліту, με */
    double bending_stress_mpa;     /* Згинальне напруження в текстоліті, МПа */

    /* 3. Оцінка за IPC/JEDEC-9704 */
    double mlcc_0402_margin;       /* Запас міцності для 0402 (ліміт 750 με) */
    double mlcc_0805_margin;       /* Запас міцності для 0805 (ліміт 500 με) */
    double mlcc_1206_margin;       /* Запас міцності для 1206 (ліміт 400 με) */
    bool   overall_ipc9704_safe;   /* Чи безпечно для стандартних компонентів 0805 */

    /* 4. Теплове розширення та геометрія паза */
    double delta_cte_ppm;          /* Різниця CTE між платою та корпусом, ppm/K */
    double thermal_expansion_mm;   /* Абсолютне теплове зміщення на базі, мм */
    double recommended_slot_len_mm;/* Рекомендована повна довжина овального паза, мм */

    /* 5. Радіуси зон заборони (Keepout) від центру отвору */
    double keepout_trace_radius_mm;/* Зона заборони доріжок */
    double keepout_0603_radius_mm; /* Зона заборони пасивів 0603 */
    double keepout_0805_radius_mm; /* Зона заборони MLCC 0805 */
    double keepout_1206_radius_mm; /* Зона заборони MLCC 1206 */
    double keepout_tooling_radius_mm; /* Зона доступу монтажного інструмента */
} PcbMountingOutput;

/* Отримання назви та CTE матеріалу шасі */
static void get_chassis_props(ChassisMaterialType type, double custom_cte,
                              const char **name_out, double *cte_out) {
    switch (type) {
        case CHASSIS_ALUMINUM_6061:
            *name_out = "Алюмінієвий сплав AL6061-T6";
            *cte_out = 23.2;
            break;
        case CHASSIS_STEEL_SPCC:
            *name_out = "Листова сталь SPCC";
            *cte_out = 11.8;
            break;
        case CHASSIS_STAINLESS_304:
            *name_out = "Нержавіюча сталь AISI 304";
            *cte_out = 16.5;
            break;
        case CHASSIS_BRASS:
            *name_out = "Латунь ЛС59-1 (CW614N)";
            *cte_out = 18.5;
            break;
        case CHASSIS_POLYCARBONATE_ABS:
            *name_out = "Пластик PC / ABS";
            *cte_out = 72.0;
            break;
        case CHASSIS_CUSTOM:
        default:
            *name_out = "Користувацький матеріал";
            *cte_out = custom_cte;
            break;
    }
}

/*
 * Головна розрахункова функція
 */
bool calculate_pcb_mounting_node(const PcbMountingInput *in, PcbMountingOutput *out) {
    if (!in || !out) return false;
    if (in->screw_dia_nominal_mm <= 0.0 || in->washer_outer_dia_mm <= in->drill_hole_dia_mm) return false;
    if (in->nut_factor_k <= 0.0 || in->pcb_thickness_mm <= 0.0 || in->standoff_span_mm <= 0.0) return false;

    memset(out, 0, sizeof(PcbMountingOutput));

    /* 1. Розрахунок осьової сили затягування */
    double d_screw_m = in->screw_dia_nominal_mm * 1e-3;
    out->clamp_force_n = in->torque_nm / (in->nut_factor_k * d_screw_m);

    /* 2. Контактний тиск під шайбою */
    double d_wash_mm = in->washer_outer_dia_mm;
    double d_hole_mm = in->drill_hole_dia_mm;
    out->washer_contact_area_mm2 = (M_PI / 4.0) * (pow(d_wash_mm, 2) - pow(d_hole_mm, 2));
    out->washer_pressure_mpa = out->clamp_force_n / out->washer_contact_area_mm2;
    out->pressure_safe = (out->washer_pressure_mpa <= FR4_MAX_COMPRESS_MPA);

    /* 3. Згинальна деформація затисненої плати: ε = (6 * t * Δh) / L^2 */
    double t_m = in->pcb_thickness_mm * 1e-3;
    double dh_m = in->standoff_mismatch_mm * 1e-3;
    double l_m = in->standoff_span_mm * 1e-3;

    out->bending_curvature_m_inv = (8.0 * dh_m) / pow(l_m, 2);
    double strain_abs = (6.0 * t_m * dh_m) / pow(l_m, 2);
    out->surface_microstrain = strain_abs * 1e6; /* у мікрострейнах */
    out->bending_stress_mpa = strain_abs * (FR4_DEFAULT_E_GPA * 1e3);

    /* 4. Оцінка запасу міцності за IPC/JEDEC-9704 */
    out->mlcc_0402_margin = 750.0 / (out->surface_microstrain > 1e-3 ? out->surface_microstrain : 1e-3);
    out->mlcc_0805_margin = 500.0 / (out->surface_microstrain > 1e-3 ? out->surface_microstrain : 1e-3);
    out->mlcc_1206_margin = 400.0 / (out->surface_microstrain > 1e-3 ? out->surface_microstrain : 1e-3);
    out->overall_ipc9704_safe = (out->surface_microstrain <= 500.0);

    /* 5. Теплове розширення */
    const char *mat_name = NULL;
    double chassis_cte = 0.0;
    get_chassis_props(in->chassis_mat, in->chassis_cte_ppm, &mat_name, &chassis_cte);

    out->delta_cte_ppm = fabs(chassis_cte - FR4_DEFAULT_CTE_PPM);
    double delta_t = fabs(in->temp_max_c - in->temp_min_c);
    out->thermal_expansion_mm = in->standoff_span_mm * (out->delta_cte_ppm * 1e-6) * delta_t;
    
    /* Рекомендована довжина паза: D_hole + ΔL + 2 * зазор 0.15 мм */
    out->recommended_slot_len_mm = in->drill_hole_dia_mm + out->thermal_expansion_mm + 0.30;

    /* 6. Розрахунок радіусів зон відчуження */
    double r_wash = in->washer_outer_dia_mm / 2.0;
    out->keepout_trace_radius_mm   = r_wash + 0.80;
    out->keepout_0603_radius_mm    = r_wash + 1.50;
    out->keepout_0805_radius_mm    = r_wash + 2.50;
    out->keepout_1206_radius_mm    = r_wash + 4.00;
    out->keepout_tooling_radius_mm = r_wash + 4.50;

    return true;
}

/* Друк детального інженерного звіту */
void print_mounting_report(const PcbMountingInput *in, const PcbMountingOutput *out) {
    const char *mat_name = NULL;
    double chassis_cte = 0.0;
    get_chassis_props(in->chassis_mat, in->chassis_cte_ppm, &mat_name, &chassis_cte);

    printf("===================================================================\n");
    printf("   ЗВЕДЕНИЙ ЗВІТ РОЗРАХУНКУ КРІПИЛЬНОГО ВУЗЛА ПЛАТИ (C99 ENGINE)   \n");
    printf("===================================================================\n\n");

    printf("[1] ВХІДНІ ДАНІ КОНСТРУКЦІЇ:\n");
    printf("  • Номінал гвинта:              M%.1f (Свердління: Ø%.2f мм)\n", in->screw_dia_nominal_mm, in->drill_hole_dia_mm);
    printf("  • Шайба / Головка гвинта:      Ø%.2f мм\n", in->washer_outer_dia_mm);
    printf("  • Крутний момент затяжки:      %.2f Н·м (Коефіцієнт тертя K = %.2f)\n", in->torque_nm, in->nut_factor_k);
    printf("  • Друкована плата:             Товщина t = %.2f мм, Проліт L = %.1f мм\n", in->pcb_thickness_mm, in->standoff_span_mm);
    printf("  • Висотне биття стійок (Δh):   %.3f мм (%.0f мкм)\n", in->standoff_mismatch_mm, in->standoff_mismatch_mm * 1000.0);
    printf("  • Матеріал шасі:               %s (CTE = %.1f ppm/K)\n", mat_name, chassis_cte);
    printf("  • Робочий діапазон температур: %.1f °C .. +%.1f °C (ΔT = %.1f °C)\n\n", in->temp_min_c, in->temp_max_c, fabs(in->temp_max_c - in->temp_min_c));

    printf("[2] СИЛОВІ НАВАНТАЖЕННЯ:\n");
    printf("  • Осьова сила притиску F_clamp:   %.1f Н (%.1f кгс)\n", out->clamp_force_n, out->clamp_force_n / 9.80665);
    printf("  • Площа контакту шайби:           %.2f мм²\n", out->washer_contact_area_mm2);
    printf("  • Контактний тиск на ламінат:     %.2f МПа (Ліміт: 250 МПа) -> %s\n\n",
           out->washer_pressure_mpa, out->pressure_safe ? "[НОРМА]" : "[ПЕРЕВИЩЕННЯ ТИСКУ]");

    printf("[3] ЗГИНАЛЬНІ ДЕФОРМАЦІЇ ТА ОЦІНКА IPC/JEDEC-9704:\n");
    printf("  • Пікова поверхнева деформація:   %.1f με\n", out->surface_microstrain);
    printf("  • Згинальне напруження в FR-4:    %.2f МПа\n", out->bending_stress_mpa);
    printf("  • Запас міцності MLCC 0402:       %.2f x (Ліміт 750 με) -> %s\n",
           out->mlcc_0402_margin, out->mlcc_0402_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
    printf("  • Запас міцності MLCC 0805:       %.2f x (Ліміт 500 με) -> %s\n",
           out->mlcc_0805_margin, out->mlcc_0805_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
    printf("  • Запас міцності MLCC 1206:       %.2f x (Ліміт 400 με) -> %s\n",
           out->mlcc_1206_margin, out->mlcc_1206_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
    printf("  • Загальний статус за IPC-9704:   %s\n\n",
           out->overall_ipc9704_safe ? "✓ БЕЗПЕЧНО (Деформація <= 500 με)" : "✖ КРИТИЧНО: ВИСОКИЙ РИЗИК ТРІЩИН MLCC");

    printf("[4] ТЕПЛОВА КОМПЕНСАЦІЯ ТА ОВАЛЬНІ ПАЗИ:\n");
    printf("  • Різниця коефіцієнтів |ΔCTE|:    %.1f ppm/K\n", out->delta_cte_ppm);
    printf("  • Теплове зміщення осей на базі:  %.3f мм (%.1f мкм)\n", out->thermal_expansion_mm, out->thermal_expansion_mm * 1000.0);
    printf("  • Рекомендований розмір паза:     Ø%.2f × %.2f мм\n\n", in->drill_hole_dia_mm, out->recommended_slot_len_mm);

    printf("[5] ГЕОМЕТРИЧНІ ЗОНИ ЗАБОРОНИ (KEEPOUT RADIUS):\n");
    printf("  • Зона заборони мідних доріжок:   R >= %.2f мм (Ø >= %.2f мм)\n", out->keepout_trace_radius_mm, out->keepout_trace_radius_mm * 2.0);
    printf("  • Зона заборони пасивів 0603:     R >= %.2f мм (Ø >= %.2f мм)\n", out->keepout_0603_radius_mm, out->keepout_0603_radius_mm * 2.0);
    printf("  • Зона заборони MLCC 0805:        R >= %.2f мм (Ø >= %.2f мм)\n", out->keepout_0805_radius_mm, out->keepout_0805_radius_mm * 2.0);
    printf("  • Зона заборони MLCC 1206+:       R >= %.2f мм (Ø >= %.2f мм)\n", out->keepout_1206_radius_mm, out->keepout_1206_radius_mm * 2.0);
    printf("  • Зона доступу біти інструмента:  R >= %.2f мм (Ø >= %.2f мм, Z > 25 мм)\n", out->keepout_tooling_radius_mm, out->keepout_tooling_radius_mm * 2.0);
    printf("===================================================================\n");
}

int main(void) {
    /* Приклад: розрахунок плати контролера на стійках M3 в алюмінієвому корпусі */
    PcbMountingInput config = {
        .screw_dia_nominal_mm   = 3.0,
        .drill_hole_dia_mm      = 3.2,
        .washer_outer_dia_mm    = 7.0,
        .nut_factor_k           = 0.20,
        .torque_nm              = 0.60,
        .pcb_thickness_mm       = 1.60,
        .standoff_span_mm       = 75.0,
        .standoff_mismatch_mm   = 0.20,
        .chassis_mat            = CHASSIS_ALUMINUM_6061,
        .chassis_cte_ppm        = 23.2,
        .temp_min_c             = -40.0,
        .temp_max_c             = 85.0
    };

    PcbMountingOutput results;
    if (calculate_pcb_mounting_node(&config, &results)) {
        print_mounting_report(&config, &results);
    } else {
        fprintf(stderr, "Помилка: некоректні вхідні геометричні параметри.\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
