#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define EPSILON_0 8.8541878128e-12 /* Електрична стала, Ф/м */

typedef enum {
    INSULATION_OK = 0,
    INSULATION_ERR_INVALID_GEOMETRY = -1,
    INSULATION_ERR_INVALID_MATERIAL = -2,
    INSULATION_ERR_BREAKDOWN_RISK  = -3
} insulation_error_t;

typedef struct {
    double r1_m;        /* Радіус внутрішнього провідника, м */
    double r2_m;        /* Зовнішній радіус ізоляції, м */
    double length_m;    /* Довжина кабелю, м */
    double voltage_v;   /* Робоча напруга, В */
    double freq_hz;     /* Частота напруги, Гц */
    double eps_r;       /* Відносна діелектрична проникність */
    double tan_delta;   /* Тангенс кута діелектричних втрат */
    double e_breakdown; /* Пробійна напруженість діелектрика, В/м */
    double rho_v;       /* Об'ємний питомий опір, Ом·м */
} cable_params_t;

typedef struct {
    double e_max;          /* Максимальна напруженість поля (на r1), В/м */
    double e_min;          /* Мінімальна напруженість поля (на r2), В/м */
    double r_ratio;        /* Співвідношення радіусів r2 / r1 */
    double opt_r1_m;       /* Оптимальний радіус r1 для даного r2, м */
    double insulation_r;   /* Загальний опір ізоляції кабелю, Ом */
    double dielectric_loss;/* Потужність діелектричних втрат, Вт */
    double safety_factor;  /* Коефіцієнт запасу міцності e_breakdown / e_max */
    bool is_optimum;       /* Прапор близькості r2/r1 до e (~2.718) */
} cable_result_t;

insulation_error_t calculate_cable_insulation(const cable_params_t* params, cable_result_t* result) {
    if (!params || !result) {
        return INSULATION_ERR_INVALID_GEOMETRY;
    }
    if (params->r1_m <= 0.0 || params->r2_m <= params->r1_m || params->length_m <= 0.0) {
        return INSULATION_ERR_INVALID_GEOMETRY;
    }
    if (params->eps_r < 1.0 || params->e_breakdown <= 0.0 || params->rho_v <= 0.0) {
        return INSULATION_ERR_INVALID_MATERIAL;
    }

    double ln_ratio = log(params->r2_m / params->r1_m);
    result->r_ratio = params->r2_m / params->r1_m;
    result->opt_r1_m = params->r2_m / M_E;

    /* Перевірка близькості відношення r2/r1 до е з допуском 15% */
    result->is_optimum = fabs(result->r_ratio - M_E) < 0.4;

    /* Напруженість поля E(r) */
    result->e_max = params->voltage_v / (params->r1_m * ln_ratio);
    result->e_min = params->voltage_v / (params->r2_m * ln_ratio);

    /* Коефіцієнт запасу електричної міцності */
    result->safety_factor = params->e_breakdown / result->e_max;

    /* Опір ізоляції R_ins = (rho_v / (2 * pi * L)) * ln(r2 / r1) */
    result->insulation_r = (params->rho_v / (2.0 * M_PI * params->length_m)) * ln_ratio;

    /* Погонова та загальна ємність C = (2 * pi * eps_0 * eps_r * L) / ln(r2 / r1) */
    double capacitance = (2.0 * M_PI * EPSILON_0 * params->eps_r * params->length_m) / ln_ratio;

    /* Потужність діелектричних втрат P = U^2 * omega * C * tan(delta) */
    double omega = 2.0 * M_PI * params->freq_hz;
    result->dielectric_loss = params->voltage_v * params->voltage_v * omega * capacitance * params->tan_delta;

    if (result->safety_factor < 1.0) {
        return INSULATION_ERR_BREAKDOWN_RISK;
    }

    return INSULATION_OK;
}

int main(void) {
    cable_params_t xlpe_cable = {
        .r1_m = 0.010,         /* Жилa радіусом 10 мм */
        .r2_m = 0.027,         /* Ізоляція зовнішнім радіусом 27 мм */
        .length_m = 1000.0,    /* Кабель довжиною 1 км */
        .voltage_v = 110000.0, /* Напруга 110 кВ */
        .freq_hz = 50.0,       /* 50 Гц */
        .eps_r = 2.3,          /* XLPE діелектрик */
        .tan_delta = 0.0005,   /* tan δ = 0.0005 */
        .e_breakdown = 30e6,   /* 30 кВ/мм = 30 МВ/м */
        .rho_v = 1e14          /* 10^14 Ом·м */
    };

    cable_result_t res;
    insulation_error_t err = calculate_cable_insulation(&xlpe_cable, &res);

    if (err == INSULATION_ERR_BREAKDOWN_RISK) {
        printf("[ПОМИЛКА] Загроза пробою! E_max (%.2f МВ/м) перевищує межу (%.2f МВ/м)\n",
               res.e_max / 1e6, xlpe_cable.e_breakdown / 1e6);
        return 1;
    } else if (err != INSULATION_OK) {
        printf("[ПОМИЛКА] Некоректні вхідні параметри геометрії чи матеріалу.\n");
        return 1;
    }

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ІЗОЛЯЦІЇ КАБЕЛЮ (C) ===\n");
    printf("Відношення радіусів r2/r1 : %.3f (Оптимум e ~ 2.718: %s)\n",
           res.r_ratio, res.is_optimum ? "ТАК" : "НІ");
    printf("Оптимальний радіус r1     : %.2f мм\n", res.opt_r1_m * 1000.0);
    printf("Максимальне поле E_max    : %.2f кВ/мм\n", res.e_max / 1e6);
    printf("Мінімальне поле E_min     : %.2f кВ/мм\n", res.e_min / 1e6);
    printf("Запас електричної міцності: %.2f\n", res.safety_factor);
    printf("Опір ізоляції (1 км)      : %.2f МОм\n", res.insulation_r / 1e6);
    printf("Діелектричні втрати       : %.2f Вт\n", res.dielectric_loss);

    return 0;
}
