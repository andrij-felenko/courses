/* heat_pipe_calc.c — Ідіоматична реалізація мовою C (C99/C11) */
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Теплофізичні властивості робочої рідини */
typedef struct {
    const char* name;
    double temp_c;          /* Робоча температура, °C */
    double density_l;       /* Густина рідини, кг/м³ */
    double density_v;       /* Густина пари, кг/м³ */
    double h_fg;            /* Прихована теплота випаровування, Дж/кг */
    double surface_tension; /* Поверхневий натяг, Н/м */
    double viscosity_l;     /* Динамічна в'язкість рідини, Па·с */
    double k_fluid;         /* Теплопровідність рідини, Вт/(м·К) */
} FluidProps;

/* Конструктивні параметри теплової трубки */
typedef struct {
    double length_total;    /* Повна довжина, м */
    double length_evap;     /* Довжина випаровувача, м */
    double length_cond;     /* Довжина конденсатора, м */
    double r_outer;         /* Зовнішній радіус трубки, м */
    double r_inner;         /* Внутрішній радіус стінки (зовнішній радіус фітиля), м */
    double r_vapor;         /* Радіус парового ядра, м */
    double r_eff_pore;      /* Ефективний радіус пор фітиля, м */
    double permeability;    /* Проникність фітиля K, м² */
    double porosity;        /* Порозність фітиля (0.0-1.0) */
    double k_metal;         /* Теплопровідність металу стінки, Вт/(м·К) */
} HeatPipeParams;

/* Результати обчислення */
typedef struct {
    double merit_number;    /* Число Мерита рідини, Вт/м² */
    double p_cap_max;       /* Максимальний капілярний тиск, Па */
    double q_cap_limit;     /* Капілярний ліміт потужності, Вт */
    double q_boil_limit;    /* Кипійний ліміт потужності, Вт */
    double r_thermal_total; /* Еквівалентний тепловий опір, °C/Вт */
    bool is_valid;
} HeatPipeResult;

/* Обчислення числа Мерита: N_M = (ρ_l * γ * h_fg) / μ_l */
double calc_merit_number(const FluidProps* f) {
    if (!f || f->viscosity_l <= 0.0) return 0.0;
    return (f->density_l * f->surface_tension * f->h_fg) / f->viscosity_l;
}

/* Розрахунок термічних меж та опору */
HeatPipeResult calc_heat_pipe(const HeatPipeParams* hp, const FluidProps* fluid, double tilt_deg) {
    HeatPipeResult res = {0};
    if (!hp || !fluid) return res;
    if (hp->r_outer <= hp->r_inner || hp->r_inner <= hp->r_vapor) return res;

    /* 1. Ефективна довжина переносу маси */
    double l_eff = 0.5 * hp->length_evap + (hp->length_total - hp->length_evap - hp->length_cond) + 0.5 * hp->length_cond;

    /* 2. Площа перерізу фітиля */
    double a_wick = M_PI * (hp->r_inner * hp->r_inner - hp->r_vapor * hp->r_vapor);

    /* 3. Максимальний капілярний тиск (припущення: кут змочування θ = 0, cos θ = 1) */
    res.p_cap_max = (2.0 * fluid->surface_tension) / hp->r_eff_pore;

    /* 4. Гравітаційний протитиск */
    double tilt_rad = tilt_deg * (M_PI / 180.0);
    double p_grav = fluid->density_l * 9.81 * hp->length_total * sin(tilt_rad);

    /* 5. Число Мерита */
    res.merit_number = calc_merit_number(fluid);

    /* 6. Капілярний ліміт Q_cap_max */
    double available_dp = res.p_cap_max - p_grav;
    if (available_dp > 0.0) {
        res.q_cap_limit = available_dp * (fluid->density_l * hp->permeability * a_wick * fluid->h_fg) / (fluid->viscosity_l * l_eff);
    } else {
        res.q_cap_limit = 0.0; /* Капілярний помп не може подолати гравітацію */
    }

    /* 7. Ефективна теплопровідність просоченого фітиля (формула Максвелла) */
    double km = hp->k_metal;
    double kf = fluid->k_fluid;
    double eps = hp->porosity;
    double k_wick_eff = km * ((km + kf) - (1.0 - eps) * (km - kf)) / ((km + kf) + (1.0 - eps) * (km - kf));

    /* 8. Кипійний ліміт Q_boil_max */
    double t_sat_k = fluid->temp_c + 273.15;
    double r_b = 2.5e-6; /* Типовий радіус зародка бульбашки, 2.5 мкм */
    double numerator = 4.0 * M_PI * hp->length_evap * k_wick_eff * fluid->surface_tension * t_sat_k;
    double denominator = fluid->density_v * fluid->h_fg * r_b * log(hp->r_inner / hp->r_vapor);
    res.q_boil_limit = numerator / denominator;

    /* 9. Еквівалентний тепловий опір */
    double r_wall_evap = log(hp->r_outer / hp->r_inner) / (2.0 * M_PI * hp->length_evap * hp->k_metal);
    double r_wick_evap = log(hp->r_inner / hp->r_vapor) / (2.0 * M_PI * hp->length_evap * k_wick_eff);
    double r_wick_cond = log(hp->r_inner / hp->r_vapor) / (2.0 * M_PI * hp->length_cond * k_wick_eff);
    double r_wall_cond = log(hp->r_outer / hp->r_inner) / (2.0 * M_PI * hp->length_cond * hp->k_metal);

    res.r_thermal_total = r_wall_evap + r_wick_evap + r_wick_cond + r_wall_cond;
    res.is_valid = true;

    return res;
}

int main(void) {
    /* Параметри води за 100 °C */
    FluidProps water = {
        .name = "Water (100 C)",
        .temp_c = 100.0,
        .density_l = 958.4,
        .density_v = 0.598,
        .h_fg = 2257000.0,
        .surface_tension = 0.0589,
        .viscosity_l = 0.000282,
        .k_fluid = 0.679
    };

    /* Типова мідна трубка D=8мм зі спеченим фітилем */
    HeatPipeParams hp = {
        .length_total = 0.200,   /* 200 мм */
        .length_evap = 0.050,    /* 50 мм */
        .length_cond = 0.050,    /* 50 мм */
        .r_outer = 0.0040,       /* Зовнішній радіус 4 мм */
        .r_inner = 0.0033,       /* Стінка 0.7 мм */
        .r_vapor = 0.0025,       /* Товщина фітиля 0.8 мм */
        .r_eff_pore = 15e-6,     /* Пор 15 мкм */
        .permeability = 1.5e-11, /* K = 1.5e-11 м² */
        .porosity = 0.55,        /* Порозність 55% */
        .k_metal = 390.0         /* Мідь */
    };

    HeatPipeResult res = calc_heat_pipe(&hp, &water, 0.0 /* Горизонтально */);

    if (res.is_valid) {
        printf("--- Розрахунок теплової трубки (%s) ---\n", water.name);
        printf("Число Мерита N_M:        %.2e Вт/м²\n", res.merit_number);
        printf("Макс. капілярний тиск:  %.1f Па\n", res.p_cap_max);
        printf("Капілярний ліміт Q_max: %.2f Вт\n", res.q_cap_limit);
        printf("Кипійний ліміт Q_max:   %.2f Вт\n", res.q_boil_limit);
        printf("Тепловий опір R_th:     %.4f °C/Вт\n", res.r_thermal_total);
    }
    return 0;
}
