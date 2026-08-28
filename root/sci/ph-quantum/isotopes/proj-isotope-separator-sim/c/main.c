/* c — Симуляція мас-спектрометричного розділення та центрифужного каскаду */
#include <stdio.h>
#include <math.h>

#define ELEM_CHARGE 1.602176634e-19
#define AMU_TO_KG   1.660539066e-27
#define GAS_CONST   8.314462618

typedef struct {
    double mass_amu_1;    /* Маса легкого ізотопу (а.о.м.) */
    double mass_amu_2;    /* Маса важкого ізотопу (а.о.м.) */
    double voltage_v;     /* Прискорювальна напруга U (В) */
    double magnetic_b_t;  /* Магнітна індукція B (Тл) */
} em_separator_params_t;

typedef struct {
    double radius_m1;     /* Радіус траєкторії першого ізотопу (м) */
    double radius_m2;     /* Радіус траєкторії другого ізотопу (м) */
    double separation_mm; /* Відстань між плямами на колекторі (мм) */
    double resolution;    /* Роздільна здатність m / delta_m */
} em_separator_result_t;

typedef struct {
    double delta_m_kg;    /* Молярна різниця мас (кг/моль) */
    double rotor_radius_m;/* Радіус ротора центрифуги (м) */
    double rpm;           /* Оберти за хвилину (об/хв) */
    double temp_kelvin;   /* Температура газу (К) */
    double feed_fraction; /* Частка 235U у сировині (z_f) */
    double prod_fraction; /* Бажана частка 235U у продукті (y_p) */
    double tail_fraction; /* Частка 235U у відвалі (x_w) */
} cascade_params_t;

typedef struct {
    double alpha_factor;  /* Коефіцієнт розділення одного ступеня */
    double v_peripheral;  /* Периферійна швидкість ротора (м/с) */
    double min_stages;    /* Мінімальна кількість ступенів N_min */
    double product_flow;  /* Відносний вихід продукту P/F */
} cascade_result_t;

int simulate_em_separator(const em_separator_params_t* p, em_separator_result_t* res) {
    if (!p || !res || p->magnetic_b_t <= 0.0 || p->voltage_v <= 0.0) {
        return -1;
    }

    double m1_kg = p->mass_amu_1 * AMU_TO_KG;
    double m2_kg = p->mass_amu_2 * AMU_TO_KG;

    res->radius_m1 = (1.0 / p->magnetic_b_t) * sqrt((2.0 * m1_kg * p->voltage_v) / ELEM_CHARGE);
    res->radius_m2 = (1.0 / p->magnetic_b_t) * sqrt((2.0 * m2_kg * p->voltage_v) / ELEM_CHARGE);

    res->separation_mm = 2.0 * (res->radius_m2 - res->radius_m1) * 1000.0;
    res->resolution = (p->mass_amu_1 + p->mass_amu_2) / (2.0 * fabs(p->mass_amu_2 - p->mass_amu_1));

    return 0;
}

int simulate_cascade(const cascade_params_t* p, cascade_result_t* res) {
    if (!p || !res || p->rpm <= 0.0 || p->rotor_radius_m <= 0.0) {
        return -1;
    }

    double omega = (p->rpm * 2.0 * M_PI) / 60.0;
    res->v_peripheral = omega * p->rotor_radius_m;

    /* alpha = exp( (delta_m * v_periph^2) / (2 * R * T) ) */
    double exponent = (p->delta_m_kg * res->v_peripheral * res->v_peripheral) / (2.0 * GAS_CONST * p->temp_kelvin);
    res->alpha_factor = exp(exponent);

    /* Рівняння Фенске: N_min */
    double num = (p->prod_fraction / (1.0 - p->prod_fraction)) / (p->tail_fraction / (1.0 - p->tail_fraction));
    res->min_stages = log(num) / log(res->alpha_factor);

    /* Відносний вихід продукту P/F = (z_f - x_w) / (y_p - x_w) */
    res->product_flow = (p->feed_fraction - p->tail_fraction) / (p->prod_fraction - p->tail_fraction);

    return 0;
}

int main(void) {
    printf("=== СИМУЛЯЦІЯ РОЗДІЛЕННЯ ІЗОТОПІВ (C) ===\n\n");

    /* 1. Мас-спектрометр для ізотопів Урану 235U та 238U */
    em_separator_params_t em_p = {
        .mass_amu_1 = 235.0439,
        .mass_amu_2 = 238.0507,
        .voltage_v = 10000.0,    /* 10 кВ */
        .magnetic_b_t = 0.5      /* 0.5 Тл */
    };
    em_separator_result_t em_res;

    if (simulate_em_separator(&em_p, &em_res) == 0) {
        printf("--- Електромагнітний розділювач (180 deg) ---\n");
        printf("Радіус 235U: %.4f м\n", em_res.radius_m1);
        printf("Радіус 238U: %.4f м\n", em_res.radius_m2);
        printf("Просторове розділення на фокусі (2*Delta_r): %.2f мм\n", em_res.separation_mm);
        printf("Роздільна здатність m / Delta_m: %.1f\n\n", em_res.resolution);
    }

    /* 2. Газова центрифуга для збагачення Урану */
    cascade_params_t cas_p = {
        .delta_m_kg = 0.003,       /* 3 г/моль між 238UF6 та 235UF6 */
        .rotor_radius_m = 0.15,    /* 15 см */
        .rpm = 90000.0,            /* 90,000 об/хв */
        .temp_kelvin = 320.0,      /* 47 °C */
        .feed_fraction = 0.0072,   /* Природний уран 0.72% 235U */
        .prod_fraction = 0.045,    /* Енергетичний уран 4.5% 235U */
        .tail_fraction = 0.002     /* Відвал 0.2% 235U */
    };
    cascade_result_t cas_res;

    if (simulate_cascade(&cas_p, &cas_res) == 0) {
        printf("--- Каскад газових центрифуг (UF6) ---\n");
        printf("Периферійна швидкість ротора: %.1f м/с\n", cas_res.v_peripheral);
        printf("Фактор розділення 1 ступеня (alpha): %.5f\n", cas_res.alpha_factor);
        printf("Мінімальна кількість ступенів N_min: %.1f\n", cas_res.min_stages);
        printf("Вихід продукту P/F: %.4f (%.2f%% від входу)\n", cas_res.product_flow, cas_res.product_flow * 100.0);
    }

    return 0;
}
