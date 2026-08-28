#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static double harmonic_potential(double x, void *user_data) {
    (void)user_data;
    return 0.5 * x * x;
}

int main(void) {
    qs_grid_config_t grid_cfg = {
        .x_min = -6.0, .x_max = 6.0, .num_points = 2001, .mass = 1.0, .hbar = 1.0
    };
    qs_solver_params_t params = {
        .method = QS_METHOD_NUMEROV, .tolerance = 1e-8, .max_iterations = 300,
        .boundary_left = QS_BOUNDARY_DIRICHLET, .boundary_right = QS_BOUNDARY_DIRICHLET,
        .num_eigenvalues = 3
    };

    qs_solver_t *solver = qs_solver_create(&grid_cfg, &params);
    if (!solver) return 1;

    qs_solver_set_potential_func(solver, harmonic_potential, NULL);

    qs_result_t result;
    if (qs_solver_run(solver, &result) == QS_SUCCESS) {
        printf("Знайдено власних станів: %u\n", result.num_found);
        for (uint32_t i = 0; i < result.num_found; ++i) {
            printf("E[%u] = %.6f\n", result.states[i].state_index, result.states[i].energy);
        }
        qs_result_free(&result);
    }
    qs_solver_destroy(solver);
    return 0;
}
