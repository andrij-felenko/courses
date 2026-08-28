/* frenkel_poole_sim.c — Симулятор струмів витоку Френкеля-Пуля на C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи (SI) */
#define Q_ELEM    1.602176634e-19 /* Заряд електрона, Кл */
#define KB_BOLTZ  1.380649e-23    /* Стала Больцмана, Дж/К */
#define EPS_0     8.854187817e-12 /* Діелектрична проникність вакууму, Ф/м */

/* Фізичні параметри плівки Si3N4 у 3D NAND */
typedef struct {
    double eps_r;   /* Оптична відносна діелектрична проникність (~5.5) */
    double phi_b_ev;/* Глибина пастки в еВ (~1.05 еВ) */
    double c_const; /* Константа витоку (А / (В · м)) */
} NitrideParams;

/* Результат обчислення для однієї точки */
typedef struct {
    double field_mv_cm; /* Поле, МВ/см */
    double barrier_drop_ev; /* Зниження бар'єра dPhi, еВ */
    double j_pf_a_cm2;  /* Густина струму, А/см² */
    double retention_sec;/* Оціночний час утримання, с */
} SimPoint;

/* Обчислення струму Френкеля-Пуля для заданого поля E (В/м) та T (К) */
SimPoint compute_fp_point(double e_field_v_m, double temp_k, const NitrideParams *params) {
    SimPoint pt;
    pt.field_mv_cm = e_field_v_m / 1e8; /* Конвертація у МВ/см */

    double eps_i = params->eps_r * EPS_0;
    
    /* Зниження бар'єра dPhi = sqrt(q * E / (pi * eps_i)) у Дж */
    double dphi_joules = sqrt((Q_ELEM * Q_ELEM * Q_ELEM * e_field_v_m) / (M_PI * eps_i));
    pt.barrier_drop_ev = dphi_joules / Q_ELEM;

    double phi_eff_joules = (params->phi_b_ev * Q_ELEM) - dphi_joules;
    if (phi_eff_joules < 0.0) {
        phi_eff_joules = 0.0; /* Повний пробій бар'єра */
    }

    /* Густина струму J_PF = C * E * exp(-phi_eff / (kB * T)) у А/м² */
    double exponent = -phi_eff_joules / (KB_BOLTZ * temp_k);
    double j_pf_m2 = params->c_const * e_field_v_m * exp(exponent);
    
    pt.j_pf_a_cm2 = j_pf_m2 / 1e4; /* Конвертація в А/см² */

    /* Оцінка часу втрати 50% заряду (заряд комірки ~10^-15 Кл, площа ~10^-10 см²) */
    double q_cell_cm2 = 1.0e-5; /* Кл/см² */
    pt.retention_sec = (j_pf_a_cm2 > 1e-30) ? (q_cell_cm2 / pt.j_pf_a_cm2) : 1e15;

    return pt;
}

int main(void) {
    NitrideParams si3n4 = {
        .eps_r = 5.5,
        .phi_b_ev = 1.05,
        .c_const = 1.5e-6
    };

    double temp_celsius = 85.0; /* Робоча температура SSD */
    double temp_k = temp_celsius + 273.15;

    printf("=== Симуляція струмів витоку Френкеля-Пуля (T = %.1f C) ===\n", temp_celsius);
    printf("%-12s | %-14s | %-16s | %-16s\n", 
           "E (МВ/см)", "dPhi (еВ)", "J_PF (А/см²)", "Retention (роки)");
    printf("-------------------------------------------------------------------\n");

    for (double field_mv = 0.5; field_mv <= 4.01; field_mv += 0.5) {
        double e_v_m = field_mv * 1e8;
        SimPoint pt = compute_fp_point(e_v_m, temp_k, &si3n4);
        double retention_years = pt.retention_sec / (365.25 * 86400.0);

        printf("%-12.2f | %-14.4f | %-16.4e | %-16.4e\n",
               pt.field_mv_cm, pt.barrier_drop_ev, pt.j_pf_a_cm2, retention_years);
    }

    return 0;
}
