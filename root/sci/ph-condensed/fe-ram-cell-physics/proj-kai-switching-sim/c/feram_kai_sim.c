/* feram_kai_sim.c - Чисельний симулятор зчитування FeRAM комірки (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double area_cap_um2;   /* Площа конденсатора, мкм² */
    double p_remnant_uc;   /* Залишкова поляризація Pᵣ, мкКл/см² */
    double c_lin_ff;       /* Лінійна ємність конденсатора, фФ */
    double c_bitline_ff;   /* Паразитна ємність розрядної шини Bitline, фФ */
    double tau_0_ns;       /* Часова константа KAI τ₀, нс */
    double avrami_n;       /* Показник Аврамі n */
    double v_dd_volts;     /* Напруга живлення V_DD, В */
    double t_rise_ns;      /* Час наростання фронту PL імпульсу, нс */
} FeRamCellParams;

typedef struct {
    double time_ns;
    double v_pl_volts;
    double i_sw_ma;
    double i_lin_ma;
    double v_bl_state1_volts;
    double v_bl_state0_volts;
} SimPoint;

/* Обчислення похідної переключеної фази dμ/dt за моделлю KAI */
static double kai_dmu_dt(double t_ns, double tau_0_ns, double avrami_n) {
    if (t_ns <= 0.0 || tau_0_ns <= 0.0) {
        return 0.0;
    }
    double norm_t = t_ns / tau_0_ns;
    double term1 = (avrami_n / tau_0_ns) * pow(norm_t, avrami_n - 1.0);
    double term2 = exp(-pow(norm_t, avrami_n));
    return term1 * term2;
}

/* Симуляція динаміки зчитування комірки */
static bool run_feram_simulation(const FeRamCellParams *params, 
                                double t_total_ns, 
                                double dt_ns, 
                                SimPoint **out_results, 
                                size_t *out_count) {
    if (!params || !out_results || !out_count || dt_ns <= 0.0) {
        return false;
    }

    size_t steps = (size_t)(t_total_ns / dt_ns) + 1;
    SimPoint *results = (SimPoint *)malloc(steps * sizeof(SimPoint));
    if (!results) {
        return false;
    }

    /* Перетворення одиниць SI */
    double area_cm2 = params->area_cap_um2 * 1.0e-8;
    double pr_c_cm2 = params->p_remnant_uc * 1.0e-6;
    double q_sw_total_c = 2.0 * pr_c_cm2 * area_cm2; /* Q_sw = 2 * Pᵣ * A */
    
    double c_lin_farads = params->c_lin_ff * 1.0e-15;
    double c_bl_farads = params->c_bitline_ff * 1.0e-15;
    double c_total_farads = c_lin_farads + c_bl_farads;

    double v_bl_1 = 0.0;
    double v_bl_0 = 0.0;

    for (size_t i = 0; i < steps; i++) {
        double t = i * dt_ns;
        
        /* Профіль імпульсу пластинної шини PL */
        double v_pl = 0.0;
        double dv_pl_dt = 0.0;
        if (t < params->t_rise_ns) {
            v_pl = params->v_dd_volts * (t / params->t_rise_ns);
            dv_pl_dt = params->v_dd_volts / params->t_rise_ns;
        } else {
            v_pl = params->v_dd_volts;
            dv_pl_dt = 0.0;
        }

        /* Струм перемикання KAI (для стану '1') */
        double dmu_dt = kai_dmu_dt(t, params->tau_0_ns, params->avrami_n);
        double i_sw_amp = q_sw_total_c * (dmu_dt * 1.0e9); /* dμ/dt переведено в с⁻¹ */

        /* Лінійний струм зміщення */
        double i_lin_amp = c_lin_farads * (dv_pl_dt * 1.0e9);

        /* Оновлення напруг розрядної шини */
        double dv_bl_1 = ((i_sw_amp + i_lin_amp) / c_total_farads) * (dt_ns * 1.0e-9);
        double dv_bl_0 = (i_lin_amp / c_total_farads) * (dt_ns * 1.0e-9);

        v_bl_1 += dv_bl_1;
        v_bl_0 += dv_bl_0;

        results[i].time_ns = t;
        results[i].v_pl_volts = v_pl;
        results[i].i_sw_ma = i_sw_amp * 1.0e3;
        results[i].i_lin_ma = i_lin_amp * 1.0e3;
        results[i].v_bl_state1_volts = v_bl_1;
        results[i].v_bl_state0_volts = v_bl_0;
    }

    *out_results = results;
    *out_count = steps;
    return true;
}

int main(void) {
    FeRamCellParams cell = {
        .area_cap_um2 = 0.25,     /* 0.25 мкм² */
        .p_remnant_uc = 22.0,     /* 22 мкКл/см² */
        .c_lin_ff = 5.0,          /* 5 фФ */
        .c_bitline_ff = 60.0,     /* 60 фФ */
        .tau_0_ns = 2.5,          /* 2.5 нс */
        .avrami_n = 2.2,          /* n = 2.2 */
        .v_dd_volts = 1.8,        /* 1.8 В */
        .t_rise_ns = 1.0          /* 1.0 нс */
    };

    SimPoint *results = NULL;
    size_t count = 0;

    if (run_feram_simulation(&cell, 10.0, 0.05, &results, &count)) {
        printf("Time(ns) | V_PL(V) | I_sw(mA) | V_BL[1](V) | V_BL[0](V) | Sense_Margin(mV)\n");
        printf("-------------------------------------------------------------------------\n");
        
        for (size_t i = 0; i < count; i += 20) { /* Друк кожного 20-го кроку */
            double margin_mv = (results[i].v_bl_state1_volts - results[i].v_bl_state0_volts) * 1000.0;
            printf("%8.2f | %7.2f | %8.4f | %10.3f | %10.3f | %17.1f\n",
                   results[i].time_ns,
                   results[i].v_pl_volts,
                   results[i].i_sw_ma,
                   results[i].v_bl_state1_volts,
                   results[i].v_bl_state0_volts,
                   margin_mv);
        }
        free(results);
    }
    return 0;
}
