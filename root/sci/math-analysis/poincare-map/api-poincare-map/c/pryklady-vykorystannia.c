/* =========================================================================
 * Повний приклад на мові C (Обчислення перерізу осцилятора Дуффінга)
 * ========================================================================= */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "poincare_sec.h"

static poincare_status_t duffing_rhs(size_t dim, double t, const double* state, double* rhs_out, void* user_data) {
    (void)dim; (void)user_data;
    rhs_out[0] = state[1];
    rhs_out[1] = -0.2 * state[1] + state[0] - state[0] * state[0] * state[0] + 0.3 * cos(t);
    return POINCARE_SUCCESS;
}

static poincare_status_t duffing_section(size_t dim, const double* state, double* val_out, double* grad_out, void* user_data) {
    (void)dim; (void)user_data;
    *val_out = state[1]; // Секуща поверхня v = 0
    if (grad_out) {
        grad_out[0] = 0.0;
        grad_out[1] = 1.0;
    }
    return POINCARE_SUCCESS;
}

int main(void) {
    poincare_config_t config;
    poincare_config_init_default(&config);

    double state[2] = {0.1, 0.0};
    double t = 0.0;
    double return_time = 0.0;

    printf("Початок обчислення точок перерізу Пуанкаре...\n");

    for (int i = 0; i < 10; ++i) {
        poincare_status_t status = poincare_step_section(
            2, duffing_rhs, duffing_section, &config, &t, state, &return_time, NULL
        );

        if (status != POINCARE_SUCCESS) {
            fprintf(stderr, "Помилка обчислення на кроці %d: код %d\n", i, status);
            return EXIT_FAILURE;
        }

        printf("Точка %d: t = %.4f, x = %.6f, v = %.6f, T_ret = %.4f\n", 
               i, t, state[0], state[1], return_time);
    }

    return EXIT_SUCCESS;
}
