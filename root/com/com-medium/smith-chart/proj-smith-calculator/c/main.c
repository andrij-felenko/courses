/* ============================================================================
 * C99 Implementation: Full RF Smith Chart & L-Match Calculator Module
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    L_TOPOLOGY_PARALLEL_C_SERIES_L = 0,
    L_TOPOLOGY_PARALLEL_L_SERIES_C = 1,
    L_TOPOLOGY_SERIES_L_PARALLEL_C = 2,
    L_TOPOLOGY_SERIES_C_PARALLEL_L = 3,
    L_TOPOLOGY_UNSUPPORTED = -1
} l_topology_t;

typedef struct {
    double complex z_raw;
    double complex z_norm;
    double complex gamma;
    double gamma_mag;
    double gamma_phase_deg;
    double vswr;
    double return_loss_db;
    double mismatch_loss_db;
} rf_smith_point_t;

typedef struct {
    l_topology_t topology;
    double c_farads;
    double l_henries;
    bool valid;
} l_match_solution_t;

/* Комплексний аналіз точки на діаграмі Сміта */
rf_smith_point_t rf_smith_analyze(double complex z_load, double z0) {
    rf_smith_point_t pt;
    pt.z_raw = z_load;
    
    if (z0 <= 0.0) {
        z0 = 50.0;
    }
    
    pt.z_norm = z_load / z0;
    pt.gamma = (pt.z_norm - 1.0) / (pt.z_norm + 1.0);
    pt.gamma_mag = cabs(pt.gamma);
    pt.gamma_phase_deg = carg(pt.gamma) * 180.0 / M_PI;

    if (pt.gamma_mag >= 0.9999) {
        pt.vswr = 999.0;
        pt.return_loss_db = 0.0;
        pt.mismatch_loss_db = 99.0;
    } else {
        pt.vswr = (1.0 + pt.gamma_mag) / (1.0 - pt.gamma_mag);
        pt.return_loss_db = -20.0 * log10(pt.gamma_mag);
        pt.mismatch_loss_db = -10.0 * log10(1.0 - pt.gamma_mag * pt.gamma_mag);
    }
    
    return pt;
}

/* Синтез ФНЧ L-мережі для навантаження R_L < Z₀ */
l_match_solution_t rf_smith_solve_lowpass_r_less(double complex z_load, double z0, double freq_hz) {
    l_match_solution_t sol;
    sol.valid = false;
    sol.topology = L_TOPOLOGY_PARALLEL_C_SERIES_L;
    sol.c_farads = 0.0;
    sol.l_henries = 0.0;

    double r_l = creal(z_load);
    double x_l = cimag(z_load);
    double omega = 2.0 * M_PI * freq_hz;

    if (r_l <= 0.0 || r_l >= z0 || omega <= 0.0) {
        return sol;
    }

    double rad = r_l * (r_l * r_l + x_l * x_l - r_l * z0);
    if (rad < 0.0) {
        return sol;
    }

    double b_p = (x_l + sqrt(r_l / z0) * sqrt(rad)) / (r_l * r_l + x_l * x_l);
    double x_s = (1.0 / b_p) + (x_l * z0) / r_l - z0 / (b_p * r_l);

    if (b_p > 0.0 && x_s > 0.0) {
        sol.c_farads = b_p / omega;
        sol.l_henries = x_s / omega;
        sol.valid = true;
    }

    return sol;
}

/* Друкований вивід звіту розрахунку */
void rf_smith_print_report(double complex z_load, double z0, double freq_hz) {
    rf_smith_point_t pt = rf_smith_analyze(z_load, z0);
    
    printf("=====================================================\n");
    printf("     ЗВІТ АНАЛІЗУ ДІАГРАМИ СМІТА ТА УЗГОДЖЕННЯ\n");
    printf("=====================================================\n");
    printf("Робоча частота:     %.2f МГц\n", freq_hz / 1e6);
    printf("Опорний опір Z₀:    %.1f Ом\n", z0);
    printf("Опір навантаження:  %.2f + j(%.2f) Ом\n", creal(z_load), cimag(z_load));
    printf("Нормований опір z:  %.3f + j(%.3f)\n", creal(pt.z_norm), cimag(pt.z_norm));
    printf("-----------------------------------------------------\n");
    printf("Комплексний Γ:       %.4f + j(%.4f)\n", creal(pt.gamma), cimag(pt.gamma));
    printf("Модуль |Γ|:          %.4f\n", pt.gamma_mag);
    printf("Фаза ∠Γ:             %.2f°\n", pt.gamma_phase_deg);
    printf("КСХ (VSWR):          %.2f : 1\n", pt.vswr);
    printf("Return Loss (RL):    %.2f дБ\n", pt.return_loss_db);
    printf("Mismatch Loss (ML):  %.2f дБ\n", pt.mismatch_loss_db);
    printf("-----------------------------------------------------\n");

    l_match_solution_t sol = rf_smith_solve_lowpass_r_less(z_load, z0, freq_hz);
    if (sol.valid) {
        printf("СИНТЕЗОВАНО L-МЕРЕЖУ (ФНЧ, R_L < Z₀):\n");
        printf("  - Паралельний конденсатор (C): %.2f пФ\n", sol.c_farads * 1e12);
        printf("  - Послідовна індуктивність (L): %.2f нГн\n", sol.l_henries * 1e9);
    } else {
        printf("УВАГА: Потрібна інша топологія (R_L >= Z₀ або висока реактивність).\n");
    }
    printf("=====================================================\n\n");
}

int main(void) {
    /* Приклад 1: Wi-Fi антена 2.45 ГГц */
    rf_smith_print_report(25.0 + 50.0 * I, 50.0, 2.45e9);

    /* Приклад 2: Низькоомний транзистор 915 МГц */
    rf_smith_print_report(10.0 - 15.0 * I, 50.0, 915.0e6);

    return 0;
}
