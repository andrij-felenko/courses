/* Повний приклад використання C API */
#include <stdio.h>
#include <stdlib.h>
#include "syk_solver.h"

int main(void) {
    SYKSolverConfig cfg = {
        .N_fermions = 16,
        .q_body = 4,
        .beta = 20.0,
        .J_coupling = 1.0,
        .grid_points = 512,
        .mix_alpha = 0.15,
        .tolerance = 1e-7,
        .max_iters = 500
    };

    syk_solver_handle_t* solver = NULL;
    syk_status_t st = syk_solver_create(&cfg, &solver);
    if (st != SYK_SUCCESS) {
        fprintf(stderr, "Помилка створення солуера: %d\n", st);
        return 1;
    }

    printf("Запуск ітераційного солуера SYK на C API...\n");
    st = syk_solver_run(solver);
    if (st == SYK_SUCCESS) {
        printf("Солуер успішно досяг збіжності!\n");

        double* tau_grid = (double*)malloc(sizeof(double) * cfg.grid_points);
        double* g_tau = (double*)malloc(sizeof(double) * cfg.grid_points);

        syk_solver_get_g_tau(solver, tau_grid, g_tau);
        printf("G(tau = beta/2) = %.8f\n", g_tau[cfg.grid_points / 2]);

        free(tau_grid);
        free(g_tau);
    } else {
        fprintf(stderr, "Помилка обчислення: не досягнуто збіжності!\n");
    }

    syk_solver_destroy(solver);
    return 0;
}
