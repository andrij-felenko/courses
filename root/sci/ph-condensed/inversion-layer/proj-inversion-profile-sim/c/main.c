/* c99 — Моделювання електростатики МДН-інверсійного шару на C99 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define Q_ELEM   1.602176634e-19
#define KB       1.380649e-23
#define EPS0     8.8541878128e-14
#define EPS_SI   (11.7 * EPS0)
#define EPS_OX   (3.9 * EPS0)
#define N_I      1.5e10

typedef struct {
    double v_g;
    double n_a;
    double d_ox_nm;
    double temp_k;
    double v_fb;
    double x_max_nm;
    double dx_nm;
} mos_params_t;

typedef struct {
    double psi_s;
    double psi_b;
    double q_n;
    size_t count;
    double* x_nm;
    double* psi;
    double* n_conc;
    double* p_conc;
} mos_result_t;

static double calc_field(double psi_s, double vt, double l_d, double n_a) {
    if (psi_s <= 0.0) return 0.0;
    double u_s = psi_s / vt;
    double ratio = N_I / n_a;
    double term1 = exp(-u_s) + u_s - 1.0;
    double term2 = (ratio * ratio) * (exp(u_s) - u_s - 1.0);
    double f_val = sqrt(fmax(0.0, term1 + term2));
    return (sqrt(2.0) * vt / l_d) * f_val;
}

static double gate_residual(double psi_s, const mos_params_t* p, double vt, double l_d, double c_ox) {
    double f_s = calc_field(psi_s, vt, l_d, p->n_a);
    double q_sc = -EPS_SI * f_s;
    double v_g_calc = p->v_fb + psi_s + (fabs(q_sc) / c_ox);
    return v_g_calc - p->v_g;
}

static double rhs_psi(double f) {
    return -f;
}

static double rhs_f(double psi, double vt, double n_a) {
    if (psi <= 0.0) return 0.0;
    double u = psi / vt;
    double p_c = n_a * exp(-u);
    double n_c = (N_I * N_I / n_a) * exp(u);
    double rho = Q_ELEM * (p_c - n_c - n_a);
    return -rho / EPS_SI;
}

bool mos_simulate(const mos_params_t* p, mos_result_t* res) {
    if (!p || !res) return false;

    double vt = (KB * p->temp_k) / Q_ELEM;
    double psi_b = vt * log(p->n_a / N_I);
    double d_ox_cm = p->d_ox_nm * 1e-7;
    double c_ox = EPS_OX / d_ox_cm;
    double l_d = sqrt((EPS_SI * vt) / (2.0 * Q_ELEM * p->n_a));

    // 1. Пошук кореня методом бісекції
    double low = 0.0001;
    double high = (p->v_g > 0.1) ? p->v_g : 0.1;
    for (int iter = 0; iter < 80; ++iter) {
        double mid = 0.5 * (low + high);
        if (gate_residual(mid, p, vt, l_d, c_ox) > 0.0) {
            high = mid;
        } else {
            low = mid;
        }
    }
    double psi_s_sol = 0.5 * (low + high);
    double f_s_init = calc_field(psi_s_sol, vt, l_d, p->n_a);

    // 2. Виділення пам'яті для профілю
    size_t n_steps = (size_t)(p->x_max_nm / p->dx_nm);
    size_t total_points = n_steps + 1;

    res->x_nm = (double*)malloc(total_points * sizeof(double));
    res->psi = (double*)malloc(total_points * sizeof(double));
    res->n_conc = (double*)malloc(total_points * sizeof(double));
    res->p_conc = (double*)malloc(total_points * sizeof(double));

    if (!res->x_nm || !res->psi || !res->n_conc || !res->p_conc) {
        free(res->x_nm); free(res->psi); free(res->n_conc); free(res->p_conc);
        return false;
    }

    res->psi_s = psi_s_sol;
    res->psi_b = psi_b;
    res->count = total_points;

    double curr_psi = psi_s_sol;
    double curr_f = f_s_init;
    double dx_cm = p->dx_nm * 1e-7;

    for (size_t i = 0; i < total_points; ++i) {
        res->x_nm[i] = i * p->dx_nm;
        res->psi[i] = curr_psi;

        double u = (curr_psi > 0.0) ? curr_psi / vt : 0.0;
        res->n_conc[i] = (N_I * N_I / p->n_a) * exp(u);
        res->p_conc[i] = (curr_psi > 0.0) ? p->n_a * exp(-u) : p->n_a;

        // Крок інтегрування RK4
        double k1_p = rhs_psi(curr_f);
        double k1_f = rhs_f(curr_psi, vt, p->n_a);

        double k2_p = rhs_psi(curr_f + 0.5 * dx_cm * k1_f);
        double k2_f = rhs_f(curr_psi + 0.5 * dx_cm * k1_p, vt, p->n_a);

        double k3_p = rhs_psi(curr_f + 0.5 * dx_cm * k2_f);
        double k3_f = rhs_f(curr_psi + 0.5 * dx_cm * k2_p, vt, p->n_a);

        double k4_p = rhs_psi(curr_f + dx_cm * k3_f);
        double k4_f = rhs_f(curr_psi + dx_cm * k3_p, vt, p->n_a);

        curr_psi += (dx_cm / 6.0) * (k1_p + 2.0 * k2_p + 2.0 * k3_p + k4_p);
        curr_f   += (dx_cm / 6.0) * (k1_f + 2.0 * k2_f + 2.0 * k3_f + k4_f);

        if (curr_psi < 0.0) curr_psi = 0.0;
    }

    // 3. Обчислення інверсійного заряду Q_n
    double n_0 = (N_I * N_I) / p->n_a;
    res->q_n = 0.0;
    for (size_t i = 0; i < total_points - 1; ++i) {
        if (res->n_conc[i] > p->n_a) {
            double avg_n = 0.5 * (res->n_conc[i] + res->n_conc[i + 1]) - n_0;
            res->q_n += Q_ELEM * avg_n * dx_cm;
        }
    }

    return true;
}

void mos_result_free(mos_result_t* res) {
    if (res) {
        free(res->x_nm); free(res->psi); free(res->n_conc); free(res->p_conc);
        res->x_nm = res->psi = res->n_conc = res->p_conc = NULL;
        res->count = 0;
    }
}

int main(void) {
    mos_params_t params = {
        .v_g = 2.5,
        .n_a = 1e16,
        .d_ox_nm = 5.0,
        .temp_k = 300.0,
        .v_fb = 0.0,
        .x_max_nm = 20.0,
        .dx_nm = 0.05
    };

    mos_result_t res;
    if (!mos_simulate(&params, &res)) {
        fprintf(stderr, "Помилка виконання C99 симуляції МДН-структури\n");
        return 1;
    }

    printf("--- Результати симуляції (C99) ---\n");
    printf("Поверхневий потенціал psi_s = %.4f В\n", res.psi_s);
    printf("Об'ємний потенціал Фермі psi_b = %.4f В\n", res.psi_b);
    printf("Поріг сильної інверсії 2*psi_b = %.4f В\n", 2.0 * res.psi_b);
    printf("Інверсійний заряд Q_n = %.4e Кл/см²\n\n", res.q_n);

    printf("Профіль біля поверхні (перші 5 вузлів):\n");
    for (size_t i = 0; i < 5 && i < res.count; ++i) {
        printf("  x = %.2f нм: ψ = %.4f В, n = %.3e см⁻³\n", res.x_nm[i], res.psi[i], res.n_conc[i]);
    }

    mos_result_free(&res);
    return 0;
}
