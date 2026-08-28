/* henon_demo.c — Приклад використання C API henon.h */
#include <stdio.h>
#include <henon.h>

int main(void) {
    henon_params_t params = henon_default_params();
    henon_point_t start = { .x = 0.1, .y = 0.1 };

    /* 1. Розрахунок нерухомих точок */
    henon_fixed_points_t fp = henon_find_fixed_points(params);
    if (fp.is_real) {
        printf("C: Нерухома точка p1 = (%.5f, %.5f)\n", fp.p1.x, fp.p1.y);
    }

    /* 2. Розрахунок показника Ляпунова */
    henon_lyapunov_t lyap;
    if (henon_compute_lyapunov(start, params, 1000, 100000, &lyap) == HENON_OK) {
        printf("C: lambda_1 = %.5f, D_KY = %.5f\n", lyap.lambda_1, lyap.kaplan_yorke);
    }

    return 0;
}
