#include <stdio.h>
#include "center_manifold.h"

/* Нелінійність f(x, y) = x*y */
static void my_func_f(const double *x, const double *y, double *out_f, void *user_data) {
    (void)user_data;
    out_f[0] = x[0] * y[0];
}

/* Нелінійність g(x, y) = x^2 */
static void my_func_g(const double *x, const double *y, double *out_g, void *user_data) {
    (void)user_data;
    (void)y;
    out_g[0] = x[0] * x[0];
}

int main(void) {
    cm_solver_config_t config;
    cm_config_init_default(&config);
    config.max_taylor_order = 3;
    
    cm_system_t *sys = NULL;
    if (cm_system_create(&sys, 1, 1) != CM_SUCCESS) {
        fprintf(stderr, "Помилка створення системи\n");
        return 1;
    }
    
    sys->matrix_A[0] = 0.0;    /* Нейтральний спектр */
    sys->matrix_B[0] = -5.0;   /* Стійкий спектр (gamma = 5) */
    sys->func_f = my_func_f;
    sys->func_g = my_func_g;
    
    cm_manifold_t *mf = NULL;
    cm_status_e status = cm_compute_manifold(sys, &config, &mf);
    if (status != CM_SUCCESS) {
        fprintf(stderr, "Помилка обчислення многовиду: %d\n", status);
        cm_system_destroy(sys);
        return 1;
    }
    
    printf("Многовид успішно побудовано (порядок %u)\n", mf->order);
    
    double x_state[1] = {0.3};
    double dt = 0.01;
    
    for (int step = 0; step < 50; step++) {
        cm_step_reduced_rk4(sys, mf, x_state, dt);
        if (step % 10 == 0) {
            double y_eval[1];
            cm_eval_manifold(mf, x_state, y_eval);
            printf("Крок %2d: x = %.6f, h(x) = %.6f\n", step, x_state[0], y_eval[0]);
        }
    }
    
    cm_manifold_destroy(mf);
    cm_system_destroy(sys);
    return 0;
}
