#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double r_raw_ohm;
    double r_sheet_ohm_sq;
    double resistivity_ohm_m;
    double c_factor;
} FourProbeResult;

int calc_4probe_sheet_resistance(
    double voltage_v,
    double current_a,
    double probe_spacing_m,
    double thickness_m,
    FourProbeResult *out_res
) {
    if (!out_res || current_a <= 0.0 || voltage_v <= 0.0 || probe_spacing_m <= 0.0) {
        return -1;
    }

    double r_raw = voltage_v / current_a;
    double c_base = M_PI / log(2.0);
    double c_thick = 1.0;

    if (thickness_m > 0.0 && (thickness_m / probe_spacing_m) > 0.05) {
        double d_s = thickness_m / probe_spacing_m;
        c_thick = (M_PI * d_s) / log(sinh(d_s) / sinh(d_s / 2.0));
        c_thick = c_thick / c_base;
    }

    double r_sheet = r_raw * c_base * c_thick;
    out_res->r_raw_ohm = r_raw;
    out_res->r_sheet_ohm_sq = r_sheet;
    out_res->resistivity_ohm_m = (thickness_m > 0.0) ? (r_sheet * thickness_m) : 0.0;
    out_res->c_factor = c_base * c_thick;

    return 0;
}

int solve_van_der_pauw(double r_a, double r_b, double tol, int max_iter, double *out_rs) {
    if (!out_rs || r_a <= 0.0 || r_b <= 0.0) return -1;

    double r_s = (M_PI / log(2.0)) * ((r_a + r_b) / 2.0);

    for (int i = 0; i < max_iter; i++) {
        double exp_a = exp(-M_PI * r_a / r_s);
        double exp_b = exp(-M_PI * r_b / r_s);
        double f_val = exp_a + exp_b - 1.0;
        double df_drs = (M_PI * r_a / (r_s * r_s)) * exp_a + (M_PI * r_b / (r_s * r_s)) * exp_b;

        double dr_s = f_val / df_drs;
        r_s -= dr_s;

        if (fabs(dr_s) < tol) {
            *out_rs = r_s;
            return 0;
        }
    }
    return -2;
}

int main(void) {
    FourProbeResult res;
    if (calc_4probe_sheet_resistance(0.04532, 0.001, 0.001, 1e-7, &res) == 0) {
        printf("C [4-Probe] R_s: %.4f Ohm/sq, rho: %.6e Ohm*m\n", res.r_sheet_ohm_sq, res.resistivity_ohm_m);
    }
    double vdp_rs = 0.0;
    if (solve_van_der_pauw(10.2, 11.5, 1e-7, 100, &vdp_rs) == 0) {
        printf("C [VdP] R_s: %.4f Ohm/sq\n", vdp_rs);
    }
    return 0;
}
