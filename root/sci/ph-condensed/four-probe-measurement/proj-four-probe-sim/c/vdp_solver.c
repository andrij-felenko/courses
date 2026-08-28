/* vdp_solver.c — Чиста реалізація мовою C99 для мікроконтролерів (STM32/ESP32) */
#include <stdio.h>
#include <math.h>

#define VDP_PI 3.14159265358979323846
#define VDP_LN2 0.69314718055994530942

typedef enum {
    VDP_OK = 0,
    VDP_ERR_INVALID_CURRENT = -1,
    VDP_ERR_INVALID_THICKNESS = -2,
    VDP_ERR_NON_POSITIVE_R = -3,
    VDP_ERR_DIVERGED = -4
} vdp_error_t;

typedef struct {
    double sheet_resistance_ohm_sq;
    double resistivity_ohm_cm;
    double asymmetry_ratio;
    int iterations;
} vdp_result_t;

vdp_error_t vdp_solve_sheet_resistance(double r_a, double r_b, double tol, int max_iter, double *out_r_s, int *out_iters) {
    if (r_a <= 0.0 || r_b <= 0.0) {
        return VDP_ERR_NON_POSITIVE_R;
    }

    double r_s = (VDP_PI / (2.0 * VDP_LN2)) * (r_a + r_b);
    int i;

    for (i = 1; i <= max_iter; ++i) {
        double e_a = exp(-VDP_PI * r_a / r_s);
        double e_b = exp(-VDP_PI * r_b / r_s);

        double f_val = e_a + e_b - 1.0;
        double f_der = (VDP_PI * r_a / (r_s * r_s)) * e_a + (VDP_PI * r_b / (r_s * r_s)) * e_b;

        if (fabs(f_der) < 1e-15) {
            break;
        }

        double delta = f_val / f_der;
        r_s -= delta;

        if (fabs(delta / r_s) < tol) {
            if (out_r_s) *out_r_s = r_s;
            if (out_iters) *out_iters = i;
            return VDP_OK;
        }
    }

    return VDP_ERR_DIVERGED;
}

vdp_error_t vdp_process_measurements(
    const double v_a[4],
    const double v_b[4],
    double current_amps,
    double thickness_cm,
    vdp_result_t *result
) {
    if (!result) return VDP_ERR_INVALID_CURRENT;
    if (current_amps <= 0.0) return VDP_ERR_INVALID_CURRENT;
    if (thickness_cm <= 0.0) return VDP_ERR_INVALID_THICKNESS;

    double r_a1 = (v_a[0] - v_a[1]) / (2.0 * current_amps);
    double r_a2 = (v_a[2] - v_a[3]) / (2.0 * current_amps);
    double r_a = (r_a1 + r_a2) / 2.0;

    double r_b1 = (v_b[0] - v_b[1]) / (2.0 * current_amps);
    double r_b2 = (v_b[2] - v_b[3]) / (2.0 * current_amps);
    double r_b = (r_b1 + r_b2) / 2.0;

    double r_s = 0.0;
    int iters = 0;
    vdp_error_t err = vdp_solve_sheet_resistance(r_a, r_b, 1e-9, 50, &r_s, &iters);
    if (err != VDP_OK) {
        return err;
    }

    result->sheet_resistance_ohm_sq = r_s;
    result->resistivity_ohm_cm = r_s * thickness_cm;
    result->asymmetry_ratio = (r_a > r_b) ? (r_a / r_b) : (r_b / r_a);
    result->iterations = iters;

    return VDP_OK;
}

int main(void) {
    double v_a[4] = {0.0123, -0.0121, 0.0124, -0.0122};
    double v_b[4] = {0.0185, -0.0183, 0.0186, -0.0184};
    vdp_result_t res;

    vdp_error_t status = vdp_process_measurements(v_a, v_b, 0.010, 0.05, &res);
    if (status == VDP_OK) {
        printf("R_s (C99): %.4f Ohm/sq\n", res.sheet_resistance_ohm_sq);
        printf("rho (C99): %.4f mOhm*cm\n", res.resistivity_ohm_cm * 1000.0);
    }
    return 0;
}
