#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define STEFAN_BOLTZMANN 5.670374419e-8
#define AIR_CONDUCTIVITY 0.0262
#define GRAVITY 9.80665

typedef enum {
    MAT_PLASTIC_ABS,
    MAT_ALUMINUM_ANODIZED,
    MAT_ALUMINUM_RAW
} EnclosureMaterial;

typedef struct {
    double length_m;        // Довжина корпусу (м)
    double width_m;         // Ширина корпусу (м)
    double height_m;        // Висота корпусу (м)
    double wall_thick_m;    // Товщина стінки (м)
    EnclosureMaterial mat;
    double t_ambient_c;     // Температура довкілля (°C)
    double solar_flux_w_m2; // Сонячне випромінювання (Вт/м²)
} EnclosureConfig;

typedef struct {
    double p_watts;            // Потужність компонента (Вт)
    double r_th_jc;            // Опір кристал-корпус (°C/Вт)
    double area_m2;            // Площа контакту компонента (м²)
    bool   has_thermal_bridge; // Чи встановлено Gap Pad
    double gap_thick_m;        // Товщина термопрокладки (м)
    double gap_k;              // Теплопровідність прокладки (Вт/(м·К))
    double t_j_max_limit_c;    // Гранична температура кристала (°C)
} ComponentConfig;

typedef struct {
    double t_junction_c;
    double t_case_c;
    double t_air_inner_c;
    double t_wall_inner_c;
    double t_wall_outer_c;
    double h_conv_ext;
    double h_rad_ext;
    double r_th_ext;
    bool   is_safe;
    double thermal_margin_c;
} ThermalReport;

static double get_material_k(EnclosureMaterial mat) {
    switch (mat) {
        case MAT_ALUMINUM_ANODIZED:
        case MAT_ALUMINUM_RAW:
            return 160.0;
        case MAT_PLASTIC_ABS:
        default:
            return 0.20;
    }
}

static double get_material_emissivity(EnclosureMaterial mat) {
    switch (mat) {
        case MAT_ALUMINUM_ANODIZED: return 0.88;
        case MAT_ALUMINUM_RAW:      return 0.08;
        case MAT_PLASTIC_ABS:
        default:                    return 0.92;
    }
}

bool solve_thermal_budget(const EnclosureConfig *enc,
                          const ComponentConfig *comp,
                          ThermalReport *out_rep) {
    if (!enc || !comp || !out_rep) return false;

    double a_top_bot = enc->length_m * enc->width_m;
    double a_vert    = 2.0 * (enc->length_m + enc->width_m) * enc->height_m;
    double a_total   = 2.0 * a_top_bot + a_vert;

    double k_wall   = get_material_k(enc->mat);
    double eps_wall = get_material_emissivity(enc->mat);
    double r_th_wall = enc->wall_thick_m / (k_wall * a_total);

    // Розрахунок термічного опору термомосту
    double r_th_bridge = 0.0;
    if (comp->has_thermal_bridge && comp->area_m2 > 0.0 && comp->gap_k > 0.0) {
        r_th_bridge = comp->gap_thick_m / (comp->gap_k * comp->area_m2) + 0.35; // + контактний опір
    } else {
        // Тепловіддача через внутрішній застійний шар з урахуванням площі розтікання плати (~0.016 м²)
        const double effective_pcb_area = 0.016;
        r_th_bridge = 0.010 / (AIR_CONDUCTIVITY * effective_pcb_area);
    }

    // Сонячне поглинання верхньою та боковими стінками
    double p_solar = enc->solar_flux_w_m2 * (a_top_bot + 0.5 * a_vert) * 0.7; // коефіцієнт поглинання 0.7
    double p_total_ext = comp->p_watts + p_solar;

    // Ітераційний розрахунок температури зовнішньої стінки
    double t_wall_out = enc->t_ambient_c + 5.0;
    double t_amb_k = enc->t_ambient_c + 273.15;
    double h_c = 5.0;
    double h_r = 5.0;

    for (int iter = 0; iter < 100; ++iter) {
        double delta_t = fabs(t_wall_out - enc->t_ambient_c);
        if (delta_t < 0.1) delta_t = 0.1;

        // Конвекція для вертикальної пластини (апроксимація Черчилля-Чу)
        h_c = 1.42 * pow(delta_t / enc->height_m, 0.25);
        if (h_c < 2.0) h_c = 2.0;

        // Радіація за Стефаном-Больцманом
        double t_wall_k = t_wall_out + 273.15;
        double t_mean_k = 0.5 * (t_wall_k + t_amb_k);
        h_r = 4.0 * eps_wall * STEFAN_BOLTZMANN * pow(t_mean_k, 3.0);

        double h_ext = h_c + h_r;
        double r_ext = 1.0 / (h_ext * a_total);

        double next_t_wall_out = enc->t_ambient_c + p_total_ext * r_ext;
        if (fabs(next_t_wall_out - t_wall_out) < 0.005) {
            t_wall_out = next_t_wall_out;
            break;
        }
        t_wall_out = 0.7 * t_wall_out + 0.3 * next_t_wall_out; // релаксація
    }

    double delta_t_wall = comp->p_watts * r_th_wall;
    double t_wall_in    = t_wall_out + delta_t_wall;
    double t_case       = t_wall_in + comp->p_watts * r_th_bridge;
    double t_junction   = t_case + comp->p_watts * comp->r_th_jc;
    double t_air_in     = 0.5 * (t_case + t_wall_in);

    out_rep->t_wall_outer_c   = t_wall_out;
    out_rep->t_wall_inner_c   = t_wall_in;
    out_rep->t_air_inner_c    = t_air_in;
    out_rep->t_case_c         = t_case;
    out_rep->t_junction_c     = t_junction;
    out_rep->h_conv_ext       = h_c;
    out_rep->h_rad_ext        = h_r;
    out_rep->r_th_ext         = 1.0 / ((h_c + h_r) * a_total);
    out_rep->thermal_margin_c = comp->t_j_max_limit_c - t_junction;
    out_rep->is_safe          = (out_rep->thermal_margin_c >= 0.0);

    return true;
}

void print_report(const char *scenario, const ThermalReport *rep) {
    printf("========================================================\n");
    printf("СЦЕНАРІЙ: %s\n", scenario);
    printf("========================================================\n");
    printf("Зовнішня стінка корпусу: %6.2f °C\n", rep->t_wall_outer_c);
    printf("Внутрішня стінка корпусу: %6.2f °C\n", rep->t_wall_inner_c);
    printf("Повітря всередині боксу: %6.2f °C\n", rep->t_air_inner_c);
    printf("Корпус чіпа (T_case):    %6.2f °C\n", rep->t_case_c);
    printf("Кристал чіпа (T_junction):%6.2f °C\n", rep->t_junction_c);
    printf("--------------------------------------------------------\n");
    printf("Коефіцієнт конвекції:    %6.2f Вт/(м²·К)\n", rep->h_conv_ext);
    printf("Коефіцієнт радіації:     %6.2f Вт/(м²·К)\n", rep->h_rad_ext);
    printf("Зовнішній опір корпусу:  %6.2f °C/Вт\n", rep->r_th_ext);
    printf("Запас до перегріву:      %6.2f °C -> %s\n",
           rep->thermal_margin_c, rep->is_safe ? "[OK - БЕЗПЕЧНО]" : "[ПЕРЕГРІВ!]");
    printf("========================================================\n\n");
}

int main(void) {
    EnclosureConfig enc = {
        .length_m = 0.120,
        .width_m = 0.080,
        .height_m = 0.050,
        .wall_thick_m = 0.003,
        .mat = MAT_PLASTIC_ABS,
        .t_ambient_c = 35.0,
        .solar_flux_w_m2 = 0.0
    };

    ComponentConfig comp = {
        .p_watts = 3.5,
        .r_th_jc = 4.0,
        .area_m2 = 0.020 * 0.020, // 20x20 мм
        .has_thermal_bridge = false,
        .gap_thick_m = 0.0015,
        .gap_k = 3.0,
        .t_j_max_limit_c = 105.0
    };

    ThermalReport rep;

    // Сценарій 1: Пластиковий корпус без термомосту
    solve_thermal_budget(&enc, &comp, &rep);
    print_report("Пластиковий герметичний бокс IP67 (без термомосту)", &rep);

    // Сценарій 2: Алюмінієвий анодований корпус з термомостом Gap Pad
    enc.mat = MAT_ALUMINUM_ANODIZED;
    comp.has_thermal_bridge = true;
    solve_thermal_budget(&enc, &comp, &rep);
    print_report("Алюмінієвий корпус з анодуванням + Gap Pad (3 Вт/м·К)", &rep);

    return 0;
}
