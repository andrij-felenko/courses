#include "vorticity_solver.h"
#include <stdio.h>
#include <math.h>
#include <stdlib.h>

int main(void) {
    solver_config_t config = {
        .nx = 128,
        .ny = 128,
        .dx = 0.01,
        .dy = 0.01,
        .dt = 0.001,
        .viscosity = 0.0, /* Ідеальна рідина: ν = 0 */
        .bc_type = BC_PERIODIC
    };

    vorticity_solver_t* solver = NULL;
    if (vorticity_solver_create(&config, &solver) != SOLVER_SUCCESS) {
        fprintf(stderr, "Помилка створення соловера\n");
        return 1;
    }

    /* Заповнення початкового поля вихровості (вихір Гаусса) */
    double* omega = (double*)malloc(sizeof(double) * config.nx * config.ny);
    for (size_t j = 0; j < config.ny; ++j) {
        for (size_t i = 0; i < config.nx; ++i) {
            double x = i * config.dx - 0.64;
            double y = j * config.dy - 0.64;
            omega[j * config.nx + i] = 10.0 * exp(-(x*x + y*y) / 0.02);
        }
    }
    vorticity_solver_set_vorticity(solver, omega);
    free(omega);

    /* Задаємо замкнений квадратний контур */
    point2d_t contour[4] = {
        {0.40, 0.40},
        {0.88, 0.40},
        {0.88, 0.88},
        {0.40, 0.88}
    };

    circulation_stats_t stats_init;
    vorticity_solver_compute_circulation(solver, contour, 4, &stats_init);
    printf("Початкова циркуляція Г0 = %.6f м2/с\n", stats_init.circulation);

    /* Моделювання 100 кроків */
    for (int step = 0; step < 100; ++step) {
        vorticity_solver_step(solver);
    }

    circulation_stats_t stats_final;
    vorticity_solver_compute_circulation(solver, contour, 4, &stats_final);
    printf("Кінцева циркуляція   Г1 = %.6f м2/с\n", stats_final.circulation);
    printf("Відносна зміна dГ/Г0    = %.2e\n", 
           fabs(stats_final.circulation - stats_init.circulation) / stats_init.circulation);

    vorticity_solver_destroy(solver);
    return 0;
}
