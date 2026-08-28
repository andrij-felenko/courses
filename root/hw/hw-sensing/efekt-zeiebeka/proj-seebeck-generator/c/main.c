#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Параметри конструкції модуля термоелектрогенератора TEG */
typedef struct {
    double seebeck_p;    /* коефіцієнт Зеєбека p-типу, В/К (наприклад +210e-6) */
    double seebeck_n;    /* коефіцієнт Зеєбека n-типу, В/К (наприклад -210e-6) */
    double rho_p;        /* питомий електричний опір p-типу, Ом·м */
    double rho_n;        /* питомий електричний опір n-типу, Ом·м */
    double kappa_p;      /* питома теплопровідність p-типу, Вт/(м·К) */
    double kappa_n;      /* питома теплопровідність n-типу, Вт/(м·К) */
    double leg_length_m; /* висота напівпровідникового стовпчика, м */
    double leg_area_m2;   /* площа поперечного перерізу стовпчика, м² */
    int num_couples;     /* кількість послідовно з'єднаних пар p-n */
} TegModuleParams;

/* Результати розрахунку робочої точки генератора під навантаженням */
typedef struct {
    double v_open_circuit_v;     /* ЕРС холостого ходу, В */
    double r_internal_ohm;       /* внутрішній опір модуля, Ом */
    double k_thermal_w_per_k;    /* теплова провідність модуля, Вт/К */
    double current_a;            /* робочий струм у колі, А */
    double voltage_load_v;       /* падіння напруги на навантаженні, В */
    double power_electrical_w;   /* корисна вихідна потужність, Вт */
    double heat_absorbed_hot_w;  /* тепловий потік з гарячого боку, Вт */
    double heat_rejected_cold_w; /* тепловий потік, скинутий на радіатор, Вт */
    double efficiency_percent;   /* ККД генерації, % */
} TegOperatingPoint;

/* Чисельний розрахунок термоелектричної робочої точки */
TegOperatingPoint teg_calculate_point(const TegModuleParams *mod,
                                      double t_hot_k,
                                      double t_cold_k,
                                      double r_load_ohm) {
    TegOperatingPoint pt;
    double delta_t = t_hot_k - t_cold_k;
    double total_seebeck = (mod->seebeck_p - mod->seebeck_n) * (double)mod->num_couples;
    double geom_factor = mod->leg_length_m / mod->leg_area_m2;

    pt.v_open_circuit_v = total_seebeck * delta_t;
    pt.r_internal_ohm = (mod->rho_p + mod->rho_n) * geom_factor * (double)mod->num_couples;
    pt.k_thermal_w_per_k = (mod->kappa_p + mod->kappa_n) * (1.0 / geom_factor) * (double)mod->num_couples;

    double r_total = pt.r_internal_ohm + r_load_ohm;
    pt.current_a = (r_total > 1e-12) ? (pt.v_open_circuit_v / r_total) : 0.0;
    pt.voltage_load_v = pt.current_a * r_load_ohm;
    pt.power_electrical_w = pt.current_a * pt.current_a * r_load_ohm;

    /* Енергетичний баланс граней з урахуванням ефектів Пельтьє, теплопровідності та Джоуля */
    double q_peltier_hot = total_seebeck * t_hot_k * pt.current_a;
    double q_conduction = pt.k_thermal_w_per_k * delta_t;
    double q_joule_half = 0.5 * pt.current_a * pt.current_a * pt.r_internal_ohm;

    pt.heat_absorbed_hot_w = q_peltier_hot + q_conduction - q_joule_half;
    pt.heat_rejected_cold_w = (total_seebeck * t_cold_k * pt.current_a) + q_conduction + q_joule_half;

    if (pt.heat_absorbed_hot_w > 1e-9) {
        pt.efficiency_percent = (pt.power_electrical_w / pt.heat_absorbed_hot_w) * 100.0;
    } else {
        pt.efficiency_percent = 0.0;
    }

    return pt;
}

/* ──────────────── NIST ITS-90 Поліноми для Термопари Типу K ─────────────── */

static const double K_COEFFS_T_TO_V[] = {
    -1.76004136860E-01,
     3.89212049750E+01,
     1.85587700320E-02,
    -9.94575928740E-05,
     3.18409457190E-07,
    -5.60728448890E-10,
     5.60750590590E-13,
    -3.20207200030E-16,
     9.71511471520E-20,
    -1.21047212750E-23
};

static const double K_COEFFS_V_TO_T[] = {
     0.0000000E+00,
     2.5083550E+01,
     7.8601060E-02,
    -2.5031310E-01,
     8.3152700E-02,
    -1.2280340E-02,
     9.8040360E-04,
    -4.4130300E-05,
     1.0577340E-06,
    -1.0527550E-08
};

/* Пряме перетворення: T (°C) -> ЕРС (мкВ) за схемою Горнера */
double thermocouple_k_temp_to_uv(double temp_c) {
    double uv = K_COEFFS_T_TO_V[9];
    for (int i = 8; i >= 0; --i) {
        uv = uv * temp_c + K_COEFFS_T_TO_V[i];
    }
    double a0 = 1.185976e+02;
    double a1 = -1.183432e-04;
    double a2 = 1.269686e+02;
    uv += a0 * exp(a1 * (temp_c - a2) * (temp_c - a2));
    return uv;
}

/* Обернене перетворення: ЕРС (мВ) -> T (°C) за схемою Горнера */
double thermocouple_k_voltage_to_temp(double emf_mv) {
    double temp = K_COEFFS_V_TO_T[9];
    for (int i = 8; i >= 0; --i) {
        temp = temp * emf_mv + K_COEFFS_V_TO_T[i];
    }
    return temp;
}

/* Повний контур вимірювання з компенсацією холодного спаю */
double thermocouple_k_measure(double measured_raw_uv, double cjc_ambient_temp_c) {
    double v_cjc_uv = thermocouple_k_temp_to_uv(cjc_ambient_temp_c);
    double v_total_uv = measured_raw_uv + v_cjc_uv;
    return thermocouple_k_voltage_to_temp(v_total_uv * 1e-3);
}

int main(void) {
    /* Параметри серійного модуля TEG (127 пар, Bi2Te3) */
    TegModuleParams mod = {
        .seebeck_p = 210e-6,
        .seebeck_n = -210e-6,
        .rho_p = 1.2e-5,
        .rho_n = 1.2e-5,
        .kappa_p = 1.5,
        .kappa_n = 1.5,
        .leg_length_m = 1.5e-3,
        .leg_area_m2 = 1.4e-3 * 1.4e-3,
        .num_couples = 127
    };

    double t_hot = 473.15;  /* 200 °C */
    double t_cold = 303.15; /* 30 °C */

    TegOperatingPoint probe = teg_calculate_point(&mod, t_hot, t_cold, 1.0);
    TegOperatingPoint match = teg_calculate_point(&mod, t_hot, t_cold, probe.r_internal_ohm);

    printf("=== Симуляція Термоелектричного Генератора (TEG) ===\n");
    printf("Перепад температур ΔT: %.1f K (Hot=%.1f K, Cold=%.1f K)\n", t_hot - t_cold, t_hot, t_cold);
    printf("Напруга холостого ходу V_oc: %.3f В\n", match.v_open_circuit_v);
    printf("Внутрішній опір модуля R_int: %.3f Ом\n", match.r_internal_ohm);
    printf("Струм при узгодженні I: %.3f А\n", match.current_a);
    printf("Максимальна вихідна потужність P_el: %.3f Вт\n", match.power_electrical_w);
    printf("Тепловий ККД генератора: %.2f %%\n\n", match.efficiency_percent);

    printf("=== Лінеаризація Термопари Типу K (ITS-90 + CJC) ===\n");
    double ambient_cjc = 24.5;
    double measured_uv = 12150.0;
    double hot_temp = thermocouple_k_measure(measured_uv, ambient_cjc);

    printf("Температура клем холодного спаю (CJC): %.2f °C\n", ambient_cjc);
    printf("Виміряна різниця потенціалів: %.1f мкВ\n", measured_uv);
    printf("Обчислена дійсна температура об'єкта: %.2f °C\n", hot_temp);

    return 0;
}
