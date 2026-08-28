/* main.c - Приклад використання LyapunovLab API мовою C */
#include "lyapunov_lab.h"
#include <stdio.h>
#include <stdlib.h>

static void lorenz_rhs_cb(double t, const double *x, double *dxdt, void *user_data) {
    (void)t; (void)user_data;
    dxdt[0] = 10.0 * (x[1] - x[0]);
    dxdt[1] = x[0] * (28.0 - x[2]) - x[1];
    dxdt[2] = x[0] * x[1] - (8.0 / 3.0) * x[2];
}

static void lorenz_jac_cb(double t, const double *x, double *J, void *user_data) {
    (void)t; (void)user_data;
    J[0] = -10.0; J[1] = 10.0;  J[2] = 0.0;
    J[3] = 28.0 - x[2]; J[4] = -1.0; J[5] = -x[0];
    J[6] = x[1];  J[7] = x[0];  J[8] = -8.0 / 3.0;
}

int main(void) {
    LyapunovConfig cfg = {
        .dim = 3,
        .dt = 0.01,
        .total_steps = 50000,
        .transient_steps = 5000,
        .qr_period = 1,
        .method = LYAPUNOV_INTEGRATOR_RK4
    };

    LyapunovSystem sys = {
        .rhs = lorenz_rhs_cb,
        .jacobian = lorenz_jac_cb,
        .user_data = NULL
    };

    double init_state[3] = { 1.0, 1.0, 1.0 };
    LyapunovMetrics *metrics = lyapunov_metrics_create(cfg.dim);

    LyapunovStatus status = lyapunov_compute_spectrum(&sys, &cfg, init_state, metrics);
    if (status == LYAPUNOV_SUCCESS) {
        printf("Обчислення завершено успішно:\n");
        printf("  lambda_1 = %+.4f\n", metrics->spectrum[0]);
        printf("  lambda_2 = %+.4f\n", metrics->spectrum[1]);
        printf("  lambda_3 = %+.4f\n", metrics->spectrum[2]);
        printf("  D_L = %.3f\n", metrics->lyapunov_dimension);
    } else {
        fprintf(stderr, "Помилка: %s\n", lyapunov_status_string(status));
    }

    lyapunov_metrics_destroy(metrics);
    return 0;
}
