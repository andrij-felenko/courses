#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MU_0 1.2566370614359173e-6 /* Гн/м */
#define SQRT3_HALF 0.8660254037844386

typedef enum {
    BUSBAR_OK = 0,
    BUSBAR_ERR_INVALID_PARAM = -1,
    BUSBAR_ERR_STRESS_EXCEEDED = -2,
    BUSBAR_ERR_INSULATOR_FAIL = -3
} busbar_status_t;

typedef struct {
    double ik_initial_ka;   /* Початковий діючий струм КЗ I''k, кА */
    double k_shock;          /* Ударний коефіцієнт k_th (1.0 - 2.0) */
    double distance_m;       /* Відстань між осями фаз a, м */
    double span_length_m;    /* Довжина прольоту між ізоляторами L, м */
    double bus_width_m;      /* Ширина шини b (товщина), м */
    double bus_height_m;     /* Висота шини h (у площині вигину), м */
    double yield_stress_mpa; /* Межа плинності матеріалу sigma_0.2, МПа */
    double max_insulator_force_kn; /* Допустиме згинне навантаження ізолятора, кН */
} busbar_config_t;

typedef struct {
    double i_peak_ka;          /* Ударний струм КЗ i_th, кА */
    double force_per_meter_kn; /* Динамічна сила на метр F_din, кН/м */
    double total_span_force_kn;/* Повна сила на проліт, кН */
    double bending_stress_mpa; /* Виникаюче напруження вигину, МПа */
    double insulator_load_kn;  /* Навантаження на опорний ізолятор, кН */
    double safety_factor_stress;/* Коефіцієнт запасу міцності шини */
    bool is_safe;              /* Загальний прапорець безпеки */
} busbar_result_t;

busbar_status_t busbar_calculate_forces(const busbar_config_t* cfg, busbar_result_t* res) {
    if (!cfg || !res) return BUSBAR_ERR_INVALID_PARAM;
    if (cfg->distance_m <= 0.0 || cfg->span_length_m <= 0.0 || 
        cfg->bus_width_m <= 0.0 || cfg->bus_height_m <= 0.0) {
        return BUSBAR_ERR_INVALID_PARAM;
    }

    /* 1. Обчислення ударного струму i_th (в амперах) */
    double ik_amp = cfg->ik_initial_ka * 1000.0 * sqrt(2.0);
    double i_peak_amp = ik_amp * cfg->k_shock;
    res->i_peak_ka = i_peak_amp / 1000.0;

    /* 2. Максимальна електродинамічна сила на метр F_din (Н/м) */
    double f_din_n_m = (MU_0 / (2.0 * M_PI)) * SQRT3_HALF * 
                       (i_peak_amp * i_peak_amp / cfg->distance_m);
    res->force_per_meter_kn = f_din_n_m / 1000.0;
    res->total_span_force_kn = res->force_per_meter_kn * cfg->span_length_m;

    /* 3. Момент опору прямокутної шини W_z = b * h^2 / 6 (м^3) */
    double w_z = (cfg->bus_width_m * cfg->bus_height_m * cfg->bus_height_m) / 6.0;

    /* 4. Згинний момент M_max = (F_din * L^2) / 10 (Н*м) для 2+ прольотів */
    double m_max = (f_din_n_m * cfg->span_length_m * cfg->span_length_m) / 10.0;

    /* 5. Механічне напруження sigma = M / W (Па -> МПа) */
    double stress_pa = m_max / w_z;
    res->bending_stress_mpa = stress_pa / 1e6;

    /* 6. Реакція на опорному ізоляторі F_R = 1.1 * F_din * L (кН) */
    res->insulator_load_kn = 1.1 * res->force_per_meter_kn * cfg->span_length_m;

    /* 7. Перевірка запасу міцності */
    res->safety_factor_stress = cfg->yield_stress_mpa / res->bending_stress_mpa;
    res->is_safe = (res->bending_stress_mpa <= 0.8 * cfg->yield_stress_mpa) &&
                   (res->insulator_load_kn <= cfg->max_insulator_force_kn);

    if (res->bending_stress_mpa > cfg->yield_stress_mpa) {
        return BUSBAR_ERR_STRESS_EXCEEDED;
    }
    if (res->insulator_load_kn > cfg->max_insulator_force_kn) {
        return BUSBAR_ERR_INSULATOR_FAIL;
    }

    return BUSBAR_OK;
}

int main(void) {
    busbar_config_t cfg = {
        .ik_initial_ka = 40.0,       /* I''k = 40 кА */
        .k_shock = 1.8,              /* k_th = 1.8 */
        .distance_m = 0.25,          /* a = 250 мм */
        .span_length_m = 1.2,        /* L = 1.2 м */
        .bus_width_m = 0.010,        /* b = 10 мм */
        .bus_height_m = 0.080,       /* h = 80 мм */
        .yield_stress_mpa = 200.0,   /* Мідь M1t, 200 МПа */
        .max_insulator_force_kn = 12.5 /* Ізолятор ІОР-10, 12.5 кН */
    };
    busbar_result_t res;

    busbar_status_t status = busbar_calculate_forces(&cfg, &res);
    printf("--- РЕЗУЛЬТАТ РОЗРАХУНКУ ШИНОПРОВОДУ (C) ---\n");
    printf("Ударний струм КЗ i_th:        %.2f кА\n", res.i_peak_ka);
    printf("Сила на метр F_din:            %.2f кН/м\n", res.force_per_meter_kn);
    printf("Напруження вигину sigma:       %.2f МПа (допустиме %.2f МПа)\n", 
           res.bending_stress_mpa, cfg.yield_stress_mpa * 0.8);
    printf("Навантаження на ізолятор:     %.2f кН (допустиме %.2f кН)\n", 
           res.insulator_load_kn, cfg.max_insulator_force_kn);
    printf("Коефіцієнт запасу:             %.2f\n", res.safety_factor_stress);
    printf("Стан конструкції:              %s\n", res.is_safe ? " БЕЗПЕЧНО" : " РИЗИК РУЙНУВАННЯ");

    return (status == BUSBAR_OK) ? 0 : 1;
}
