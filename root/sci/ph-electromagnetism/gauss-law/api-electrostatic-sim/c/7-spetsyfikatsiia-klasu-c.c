// Приклад використання C API
#include <stdio.h>
#include "libelectrostatics.h"

int run_c_simulation(void) {
    grid_config_t cfg = {
        .nx = 50, .ny = 50, .nz = 50,
        .dx = 0.02, .dy = 0.02, .dz = 0.02,
        .boundary_x_min = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_x_max = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_y_min = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_y_max = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_z_min = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_z_max = {BOUNDARY_DIRICHLET, 0.0, 0.0}
    };

    void *grid = NULL;
    if (sim_create_grid(&cfg, &grid) != SIM_SUCCESS) {
        printf("Failed to allocate grid!\n");
        return -1;
    }

    // Задаємо заряд у центрі
    sim_set_charge_density(grid, 25, 25, 25, 1.0e-6);

    size_t iters = 0;
    sim_status_t status = sim_solve_poisson_sor(grid, 1e-5, 1000, 1.6, &iters);
    if (status == SIM_SUCCESS) {
        printf("Poisson solved in %zu iterations.\n", iters);

        gauss_verification_result_t gres;
        sim_verify_gauss_law(grid, 15, 35, 15, 35, 15, 35, &gres);
        printf("Gauss Relative Error: %.2f%%\n", gres.relative_error_percent);
    }

    sim_destroy_grid(grid);
    return 0;
}
