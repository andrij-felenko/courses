#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define Q_ELEM 1.602176634e-19
#define K_BOLTZ 1.380649e-23
#define EPS_0 8.8541878128e-14

typedef struct {
    double area_cm2;
    double rel_perm;
    double richardson_a;
} schottky_config_t;

typedef struct {
    double nd_cm3;
    double v_bi_v;
    double slope;
} cv_results_t;

/* Обчислення струму насичення Is */
double calc_saturation_current(const schottky_config_t* cfg, double phi_bn_ev, double temp_k) {
    double vt = (K_BOLTZ * temp_k) / Q_ELEM;
    return cfg->area_cm2 * cfg->richardson_a * (temp_k * temp_k) * exp(-phi_bn_ev / vt);
}

/* Симуляція ВАХ методом Ньютона-Рафсона */
int simulate_iv_curve(const schottky_config_t* cfg, double phi_bn_ev, double eta, 
                      double rs_ohm, double temp_k, double* v_out, double* i_out, int count) {
    if (!cfg || !v_out || !i_out || count <= 0) return -1;

    double vt = (K_BOLTZ * temp_k) / Q_ELEM;
    double is_sat = calc_saturation_current(cfg, phi_bn_ev, temp_k);
    double v_step = 0.6 / (count - 1);

    for (int idx = 0; idx < count; ++idx) {
        double v_ext = idx * v_step;
        double curr = 1.0e-9;

        for (int iter = 0; iter < 30; ++iter) {
            double v_diode = v_ext - curr * rs_ohm;
            double exp_term = exp(v_diode / (eta * vt));
            double f_val = curr - is_sat * (exp_term - 1.0);
            double df_val = 1.0 + is_sat * (rs_ohm / (eta * vt)) * exp_term;
            double step = f_val / df_val;
            curr -= step;
            if (fabs(step) < 1.0e-12) break;
        }

        v_out[idx] = v_ext;
        i_out[idx] = (curr > 0.0) ? curr : 0.0;
    }
    return 0;
}

/* Обчислення C-V параметрів */
int extract_cv_parameters(const schottky_config_t* cfg, const double* vr, 
                          const double* c_pf, int count, double temp_k, cv_results_t* res) {
    if (!cfg || !vr || !c_pf || !res || count < 2) return -1;

    double sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_xx = 0.0;
    double eps_s = cfg->rel_perm * EPS_0;
    double vt = (K_BOLTZ * temp_k) / Q_ELEM;

    for (int i = 0; i < count; ++i) {
        double c_f = c_pf[i] * 1.0e-12;
        double y_val = 1.0 / (c_f * c_f);
        double x_val = vr[i];

        sum_x += x_val;
        sum_y += y_val;
        sum_xy += x_val * y_val;
        sum_xx += x_val * x_val;
    }

    double slope = (count * sum_xy - sum_x * sum_y) / (count * sum_xx - sum_x * sum_x);
    double intercept = (sum_y - slope * sum_x) / count;

    res->slope = slope;
    res->nd_cm3 = 2.0 / (Q_ELEM * eps_s * (cfg->area_cm2 * cfg->area_cm2) * slope);
    res->v_bi_v = (intercept / slope) + vt;

    return 0;
}

int main(void) {
    schottky_config_t cfg = { .area_cm2 = 1.0e-3, .rel_perm = 11.7, .richardson_a = 112.0 };
    double v[50], i[50];

    if (simulate_iv_curve(&cfg, 0.70, 1.05, 12.0, 300.0, v, i, 50) == 0) {
        printf("C симуляцію ВАХ успішно виконано. Точок: 50, I(max) = %.4f мА\n", i[49] * 1000.0);
    }
    return 0;
}
