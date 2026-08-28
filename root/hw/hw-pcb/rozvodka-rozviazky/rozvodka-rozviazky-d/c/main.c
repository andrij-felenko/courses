#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define VACUUM_PERM_H_M (4.0 * M_PI * 1e-7)
#define C_SPEED_M_S 299792458.0

typedef struct {
    double v_nominal_v;
    double allowed_ripple_ratio;
    double transient_current_a;
    double target_impedance_ohms;
} PdnTargetSpec;

typedef struct {
    const char *name;
    double c_farads;
    double esr_ohms;
    double esl_henries;
    double l_mount_henries;
    double srf_hz;
} DecouplingCap;

PdnTargetSpec pdn_calc_target(double v_nom, double ripple_pct, double delta_i) {
    PdnTargetSpec spec;
    spec.v_nominal_v = v_nom;
    spec.allowed_ripple_ratio = ripple_pct / 100.0;
    spec.transient_current_a = delta_i;
    spec.target_impedance_ohms = (v_nom * spec.allowed_ripple_ratio) / delta_i;
    return spec;
}

double pdn_calc_srf(double c_f, double l_total_h) {
    if (c_f <= 0.0 || l_total_h <= 0.0) return 0.0;
    return 1.0 / (2.0 * M_PI * sqrt(c_f * l_total_h));
}

double pdn_calc_antiresonance_freq(double c_small_f, double l_large_h) {
    if (c_small_f <= 0.0 || l_large_h <= 0.0) return 0.0;
    return 1.0 / (2.0 * M_PI * sqrt(c_small_f * l_large_h));
}

int main(void) {
    PdnTargetSpec target = pdn_calc_target(0.90, 3.0, 20.0);

    printf("====================================================================\n");
    printf("  РОЗРАХУНОК ЦІЛЬОВОГО ІМПЕДАНСУ ТА ПАРАМЕТРІВ РОЗВ'ЯЗКИ (C99)\n");
    printf("====================================================================\n");
    printf("  Номінальна напруга:     %.2f В (допуск ±%.1f%%, dV = %.1f мВ)\n",
           target.v_nominal_v, target.allowed_ripple_ratio * 100.0,
           target.v_nominal_v * target.allowed_ripple_ratio * 1000.0);
    printf("  Стрибок струму:         %.1f А\n", target.transient_current_a);
    printf("  Цільовий опір PDN:      %.3f мОм (Z_target)\n\n", target.target_impedance_ohms * 1000.0);

    DecouplingCap cap_far = {
        .name = "0402 100nF (Far Traces)",
        .c_farads = 100e-9, .esr_ohms = 0.018,
        .esl_henries = 0.38e-9, .l_mount_henries = 3.08e-9
    };
    cap_far.srf_hz = pdn_calc_srf(cap_far.c_farads, cap_far.l_mount_henries);

    DecouplingCap cap_side = {
        .name = "0402 100nF (Side Vias)",
        .c_farads = 100e-9, .esr_ohms = 0.018,
        .esl_henries = 0.38e-9, .l_mount_henries = 0.78e-9
    };
    cap_side.srf_hz = pdn_calc_srf(cap_side.c_farads, cap_side.l_mount_henries);

    DecouplingCap cap_vippo = {
        .name = "0201 100nF (VIPPO Bottom)",
        .c_farads = 100e-9, .esr_ohms = 0.022,
        .esl_henries = 0.20e-9, .l_mount_henries = 0.42e-9
    };
    cap_vippo.srf_hz = pdn_calc_srf(cap_vippo.c_farads, cap_vippo.l_mount_henries);

    printf("%-28s | %-10s | %-12s\n", "Топологія монтажу", "L_mount", "SRF (Резонанс)");
    printf("-----------------------------+------------+-------------\n");
    printf("%-28s | %6.2f нГн  | %6.1f МГц\n", cap_far.name, cap_far.l_mount_henries * 1e9, cap_far.srf_hz / 1e6);
    printf("%-28s | %6.2f нГн  | %6.1f МГц\n", cap_side.name, cap_side.l_mount_henries * 1e9, cap_side.srf_hz / 1e6);
    printf("%-28s | %6.2f нГн  | %6.1f МГц\n", cap_vippo.name, cap_vippo.l_mount_henries * 1e9, cap_vippo.srf_hz / 1e6);

    double f_anti = pdn_calc_antiresonance_freq(10e-9, cap_side.l_mount_henries);
    printf("\n  Паразитний антирезонанс (100нФ Side-Via паралельно з 10нФ): %.1f МГц\n", f_anti / 1e6);
    printf("====================================================================\n");

    return 0;
}
