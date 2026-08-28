#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define ETA_MAX_DEFAULT 10.0
#define NUM_STEPS 2000
#define MAX_ITER 100
#define TOL 1e-8

typedef struct {
    double eta;
    double f, fp, fpp;
    double theta, thetap;
} State;

typedef struct {
    double prandtl;
    double f_pp_0;
    double theta_p_0;
    double delta_v_eta;
    double delta_t_eta;
    double ratio_delta;
    double nusselt_coeff;
} SolverResult;

/* Прави частини системи 5 ОДР 1-го порядку */
static void system_derivatives(double prandtl, const double y[5], double dydeta[5]) {
    /* y[0]=f, y[1]=f', y[2]=f'', y[3]=theta, y[4]=theta' */
    dydeta[0] = y[1];
    dydeta[1] = y[2];
    dydeta[2] = -0.5 * y[0] * y[2];
    dydeta[3] = y[4];
    dydeta[4] = -0.5 * prandtl * y[0] * y[4];
}

/* Крок інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
static void rk4_step(double prandtl, double h, double y[5]) {
    double k1[5], k2[5], k3[5], k4[5], y_tmp[5];
    int i;

    system_derivatives(prandtl, y, k1);
    for (i = 0; i < 5; i++) y_tmp[i] = y[i] + 0.5 * h * k1[i];
    system_derivatives(prandtl, y_tmp, k2);
    for (i = 0; i < 5; i++) y_tmp[i] = y[i] + 0.5 * h * k2[i];
    system_derivatives(prandtl, y_tmp, k3);
    for (i = 0; i < 5; i++) y_tmp[i] = y[i] + h * k3[i];
    system_derivatives(prandtl, y_tmp, k4);

    for (i = 0; i < 5; i++) {
        y[i] += (h / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
    }
}

/* Інтегрування всієї траєкторії для заданих початкових припущень s_f та s_theta */
static double integrate_trajectory(double prandtl, double eta_max, double s_f, double s_theta,
                                    State* out_profile, int store_profile, double* out_theta_end) {
    double h = eta_max / NUM_STEPS;
    double y[5] = {0.0, 0.0, s_f, 0.0, s_theta};
    int i;

    if (store_profile && out_profile != NULL) {
        out_profile[0].eta = 0.0;
        out_profile[0].f = y[0]; out_profile[0].fp = y[1]; out_profile[0].fpp = y[2];
        out_profile[0].theta = y[3]; out_profile[0].thetap = y[4];
    }

    for (i = 1; i <= NUM_STEPS; i++) {
        rk4_step(prandtl, h, y);
        if (store_profile && out_profile != NULL) {
            out_profile[i].eta = i * h;
            out_profile[i].f = y[0]; out_profile[i].fp = y[1]; out_profile[i].fpp = y[2];
            out_profile[i].theta = y[3]; out_profile[i].thetap = y[4];
        }
    }

    if (out_theta_end) *out_theta_end = y[3];
    return y[1]; /* повертаємо f'(eta_max) */
}

/* Головна функція розв'язувача */
SolverResult solve_prandtl_boundary_layer(double prandtl) {
    SolverResult res;
    double eta_max = ETA_MAX_DEFAULT;
    if (prandtl < 0.1) eta_max = 12.0 / sqrt(prandtl); /* розширюємо домен для Pr << 1 */

    res.prandtl = prandtl;

    /* Етап 1: Стрільба для гідродинамічної частини f''(0) */
    double s_f0 = 0.2, s_f1 = 0.5;
    double err0 = integrate_trajectory(prandtl, eta_max, s_f0, 1.0, NULL, 0, NULL) - 1.0;
    double err1 = integrate_trajectory(prandtl, eta_max, s_f1, 1.0, NULL, 0, NULL) - 1.0;
    double s_f_best = s_f1;
    int iter;

    for (iter = 0; iter < MAX_ITER; iter++) {
        if (fabs(err1) < TOL) break;
        s_f_best = s_f1 - err1 * (s_f1 - s_f0) / (err1 - err0);
        s_f0 = s_f1; err0 = err1;
        s_f1 = s_f_best;
        err1 = integrate_trajectory(prandtl, eta_max, s_f1, 1.0, NULL, 0, NULL) - 1.0;
    }
    res.f_pp_0 = s_f_best;

    /* Етап 2: Стрільба для теплової частини theta'(0) */
    double s_t0 = 0.1, s_t1 = 1.0;
    double th_end0, th_end1;
    integrate_trajectory(prandtl, eta_max, res.f_pp_0, s_t0, NULL, 0, &th_end0);
    integrate_trajectory(prandtl, eta_max, res.f_pp_0, s_t1, NULL, 0, &th_end1);
    err0 = th_end0 - 1.0;
    err1 = th_end1 - 1.0;
    double s_t_best = s_t1;

    for (iter = 0; iter < MAX_ITER; iter++) {
        if (fabs(err1) < TOL) break;
        s_t_best = s_t1 - err1 * (s_t1 - s_t0) / (err1 - err0);
        s_t0 = s_t1; err0 = err1;
        s_t1 = s_t_best;
        integrate_trajectory(prandtl, eta_max, res.f_pp_0, s_t1, NULL, 0, &th_end1);
        err1 = th_end1 - 1.0;
    }
    res.theta_p_0 = s_t_best;
    res.nusselt_coeff = res.theta_p_0;

    /* Етап 3: Фінальне інтегрування та пошук товщин шарів delta_v та delta_t */
    State* profile = (State*)malloc((NUM_STEPS + 1) * sizeof(State));
    integrate_trajectory(prandtl, eta_max, res.f_pp_0, res.theta_p_0, profile, 1, NULL);

    res.delta_v_eta = eta_max;
    res.delta_t_eta = eta_max;
    int i;
    for (i = 0; i <= NUM_STEPS; i++) {
        if (profile[i].fp >= 0.99 && res.delta_v_eta == eta_max) res.delta_v_eta = profile[i].eta;
        if (profile[i].theta >= 0.99 && res.delta_t_eta == eta_max) res.delta_t_eta = profile[i].eta;
    }
    res.ratio_delta = res.delta_v_eta / res.delta_t_eta;

    free(profile);
    return res;
}

int main(void) {
    double pr_list[] = {0.005, 0.025, 0.71, 7.0, 100.0};
    int n = sizeof(pr_list) / sizeof(pr_list[0]);
    int i;

    printf("=== Чисельне моделювання примежового шару Блазіуса-Польгаузена ===\n");
    printf("Pr\t\tf''(0)\t\tθ'(0)\t\tη_δv\tη_δt\tδv/δt\n");
    printf("-------------------------------------------------------------------\n");

    for (i = 0; i < n; i++) {
        SolverResult r = solve_prandtl_boundary_layer(pr_list[i]);
        printf("%.3f\t\t%.5f\t%.5f\t%.2f\t%.2f\t%.3f\n",
               r.prandtl, r.f_pp_0, r.theta_p_0, r.delta_v_eta, r.delta_t_eta, r.ratio_delta);
    }
    return 0;
}
