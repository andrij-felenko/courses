#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    CUT_AT,
    CUT_BT,
    CUT_SC,
    CUT_TUNING_FORK_32K
} QuartzCutType;

typedef struct {
    QuartzCutType cut;
    double nominal_freq_hz; /* Номінальна частота в Гц */
    double angle_offset_min; /* Відхилення кута в кутових мінутах (для AT) */
    double t0_deg_c;         /* Температура перегину або вершини */
} QuartzSpec;

typedef struct {
    double fs_hz;    /* Послідовний резонанс */
    double fp_hz;    /* Паралельний резонанс */
    double c0_pf;    /* Статична ємність */
    double r1_ohm;   /* Динамічний опір (ESR) */
    double l1_h;     /* Динамічна індуктивність */
    double c1_ff;    /* Динамічна ємність (фемтофаради) */
    double q_factor; /* Добротність */
    double r_ratio;  /* Відношення ємностей C0 / C1 */
} BvdParameters;

typedef struct {
    double drive_level_uw;     /* Потужність збудження кристала (мкВт) */
    double neg_resistance_ohm; /* Необхідний від'ємний опір інвертора */
    double safety_factor;      /* Коефіцієнт запасу (|R_neg| / R1) */
    bool is_safe_startup;      /* Чи гарантовано безпечний старт */
} OscillatorAnalysis;

/* Розрахунок відхилення частоти (ppm) від температури */
double quartz_calculate_ppm(const QuartzSpec* spec, double temp_deg_c) {
    double dt = temp_deg_c - spec->t0_deg_c;
    
    switch (spec->cut) {
        case CUT_AT: {
            /* Чутливість лінійного коефіцієнта: -0.0847 ppm/(°C · arcmin) */
            double a1 = -0.0847 * spec->angle_offset_min;
            double a2 = -0.0004;
            double a3 = 0.000095;
            return (a1 * dt) + (a2 * dt * dt) + (a3 * dt * dt * dt);
        }
        case CUT_BT: {
            double b2 = -0.040;
            return b2 * dt * dt;
        }
        case CUT_SC: {
            /* SC-зріз: кубічна крива з точкою перегину близько 92 °C */
            double c1 = 0.0;
            double c2 = -0.0003;
            double c3 = 0.000075;
            return (c1 * dt) + (c2 * dt * dt) + (c3 * dt * dt * dt);
        }
        case CUT_TUNING_FORK_32K: {
            double k2 = -0.035;
            return k2 * dt * dt;
        }
        default:
            return 0.0;
    }
}

/* Обчислення параметрів еквівалентної схеми Баттерворта-Ван Дайка */
bool quartz_extract_bvd(double fs_hz, double fp_hz, double c0_pf, double r1_ohm, BvdParameters* out_bvd) {
    if (fs_hz <= 0.0 || fp_hz <= fs_hz || c0_pf <= 0.0 || r1_ohm <= 0.0) {
        return false;
    }
    
    double c0_farads = c0_pf * 1e-12;
    double delta_f = fp_hz - fs_hz;
    
    /* C1 = 2 * C0 * (fp - fs) / fs */
    double c1_farads = 2.0 * c0_farads * (delta_f / fs_hz);
    
    /* L1 = 1 / (4 * pi^2 * fs^2 * C1) */
    double omega_s = 2.0 * M_PI * fs_hz;
    double l1_henry = 1.0 / (omega_s * omega_s * c1_farads);
    
    /* Q = omega_s * L1 / R1 */
    double q = (omega_s * l1_henry) / r1_ohm;
    
    out_bvd->fs_hz = fs_hz;
    out_bvd->fp_hz = fp_hz;
    out_bvd->c0_pf = c0_pf;
    out_bvd->r1_ohm = r1_ohm;
    out_bvd->l1_h = l1_henry;
    out_bvd->c1_ff = c1_farads * 1e15; /* фФ */
    out_bvd->q_factor = q;
    out_bvd->r_ratio = c0_farads / c1_farads;
    
    return true;
}

/* Оцінка стабільності генератора П'єрса */
bool quartz_analyze_oscillator(double freq_hz, double c0_pf, double cl_pf, double r1_ohm, 
                               double vpp_volts, OscillatorAnalysis* out_analysis) {
    if (freq_hz <= 0.0 || cl_pf <= 0.0 || r1_ohm <= 0.0 || vpp_volts <= 0.0) {
        return false;
    }

    double c_total = (c0_pf + cl_pf) * 1e-12;
    double omega = 2.0 * M_PI * freq_hz;
    
    /* Струм через кристал: I_rms = (V_pp / (2 * sqrt(2))) * omega * (C0 + CL) */
    double v_rms = vpp_volts / (2.0 * sqrt(2.0));
    double i_rms = v_rms * omega * c_total;
    
    /* Потужність розсіювання: P = I_rms^2 * R1 */
    double power_watts = i_rms * i_rms * r1_ohm;
    out_analysis->drive_level_uw = power_watts * 1e6;
    
    /* Рекомендований запас за від'ємним опором: |-R| >= 5 * R1 */
    out_analysis->neg_resistance_ohm = 5.0 * r1_ohm;
    out_analysis->safety_factor = 5.0;
    
    /* Критерій безпеки: потужність для ВЧ резонатора < 100 мкВт, для 32 кГц < 1 мкВт */
    double max_allowed_uw = (freq_hz < 100000.0) ? 1.0 : 100.0;
    out_analysis->is_safe_startup = (out_analysis->drive_level_uw <= max_allowed_uw);
    
    return true;
}

/* Розрахунок похибки ходу RTC за добу (секунди) */
double rtc_daily_drift_seconds(double temp_deg_c) {
    QuartzSpec spec = {
        .cut = CUT_TUNING_FORK_32K,
        .nominal_freq_hz = 32768.0,
        .angle_offset_min = 0.0,
        .t0_deg_c = 25.0
    };
    double ppm = quartz_calculate_ppm(&spec, temp_deg_c);
    return (ppm * 1e-6) * 86400.0;
}

/* Інтегрування добового дрейфу за добовим синусоїдальним температурним профілем */
double rtc_diurnal_drift_seconds(double t_mean, double t_amplitude) {
    double total_drift_sec = 0.0;
    int steps = 24; /* 24 погодинні точки */
    for (int h = 0; h < steps; ++h) {
        double hour_angle = (2.0 * M_PI * (double)h) / 24.0;
        double current_temp = t_mean + t_amplitude * sin(hour_angle);
        total_drift_sec += rtc_daily_drift_seconds(current_temp) / 24.0;
    }
    return total_drift_sec;
}
