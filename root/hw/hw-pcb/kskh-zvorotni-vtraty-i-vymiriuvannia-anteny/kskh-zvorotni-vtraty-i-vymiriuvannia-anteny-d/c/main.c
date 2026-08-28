#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846

typedef struct {
    double real;
    double imag;
} ComplexZ;

typedef struct {
    double vswr;
    double gamma_mag;
    double gamma_phase_deg;
    double return_loss_db;
    double mismatch_loss_db;
    double radiated_power_percent;
} RfMetrics;

typedef struct {
    bool valid;
    bool series_first; // true: L_s -> C_p, false: C_p -> L_s
    double l_val_nh;
    double c_val_pf;
    double q_factor;
} LMatchResult;

RfMetrics rf_calc_metrics(ComplexZ z_load, double z0) {
    RfMetrics m;
    double num_r = z_load.real - z0;
    double num_i = z_load.imag;
    double den_r = z_load.real + z0;
    double den_i = z_load.imag;
    
    double den_mag_sq = den_r * den_r + den_i * den_i;
    double gamma_r = (num_r * den_r + num_i * den_i) / den_mag_sq;
    double gamma_i = (num_i * den_r - num_r * den_i) / den_mag_sq;
    
    m.gamma_mag = sqrt(gamma_r * gamma_r + gamma_i * gamma_i);
    m.gamma_phase_deg = atan2(gamma_i, gamma_r) * (180.0 / PI);
    
    if (m.gamma_mag >= 1.0) {
        m.vswr = 999.99;
        m.return_loss_db = 0.0;
        m.mismatch_loss_db = 999.99;
        m.radiated_power_percent = 0.0;
    } else {
        m.vswr = (1.0 + m.gamma_mag) / (1.0 - m.gamma_mag);
        m.return_loss_db = -20.0 * log10(m.gamma_mag > 1e-6 ? m.gamma_mag : 1e-6);
        double p_ratio = 1.0 - m.gamma_mag * m.gamma_mag;
        m.mismatch_loss_db = -10.0 * log10(p_ratio > 1e-6 ? p_ratio : 1e-6);
        m.radiated_power_percent = p_ratio * 100.0;
    }
    return m;
}

LMatchResult rf_calc_l_match(ComplexZ z_load, double z0, double freq_hz) {
    LMatchResult res = {0};
    double r_a = z_load.real;
    double x_a = z_load.imag;
    double omega = 2.0 * PI * freq_hz;
    
    if (r_a <= 0.0 || freq_hz <= 0.0 || z0 <= 0.0) return res;
    
    if (r_a < z0) {
        // Топологія: Low-Pass (Послідовна L, шунтова C на стороні генератора)
        double q = sqrt((z0 / r_a) - 1.0);
        double x_s = q * r_a - x_a;
        double b_p = q / z0;
        
        res.valid = true;
        res.series_first = true;
        res.q_factor = q;
        res.l_val_nh = (x_s / omega) * 1e9;
        res.c_val_pf = (b_p / omega) * 1e12;
    } else {
        // Топологія: Low-Pass (Шунтова C на стороні антени, послідовна L)
        double q = sqrt((r_a / z0) - 1.0);
        double b_p = q / r_a;
        double x_s = q * z0 - x_a;
        
        res.valid = true;
        res.series_first = false;
        res.q_factor = q;
        res.l_val_nh = (x_s / omega) * 1e9;
        res.c_val_pf = (b_p / omega) * 1e12;
    }
    return res;
}
