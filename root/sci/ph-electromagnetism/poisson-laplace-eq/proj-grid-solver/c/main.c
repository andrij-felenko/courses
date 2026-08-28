#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структурне представлення сітки Poisson 2D */
typedef struct {
    size_t nx;
    size_t ny;
    double h;
    double *phi;        /* Буфер потенціалу: index = i * ny + j */
    double *rho;        /* Густина об'ємного заряду */
    bool *is_boundary;  /* Маска фіксованих вузлів Діріхле */
} PoissonGrid2D;

/* Ініціалізація сітки та виділення динамічної пам'яті */
PoissonGrid2D* poisson_create(size_t nx, size_t ny, double h) {
    if (nx < 3 || ny < 3 || h <= 0.0) return NULL;

    PoissonGrid2D *grid = (PoissonGrid2D*)malloc(sizeof(PoissonGrid2D));
    if (!grid) return NULL;

    grid->nx = nx;
    grid->ny = ny;
    grid->h = h;
    size_t total = nx * ny;

    grid->phi = (double*)calloc(total, sizeof(double));
    grid->rho = (double*)calloc(total, sizeof(double));
    grid->is_boundary = (bool*)calloc(total, sizeof(bool));

    if (!grid->phi || !grid->rho || !grid->is_boundary) {
        free(grid->phi);
        free(grid->rho);
        free(grid->is_boundary);
        free(grid);
        return NULL;
    }
    return grid;
}

/* Звільнення ресурсів */
void poisson_free(PoissonGrid2D *grid) {
    if (!grid) return;
    free(grid->phi);
    free(grid->rho);
    free(grid->is_boundary);
    free(grid);
}

/* Встановлення потенціалу на зовнішніх межах Діріхле */
void poisson_set_boundary_dirichlet(PoissonGrid2D *grid, double v_top, double v_bot, double v_left, double v_right) {
    size_t nx = grid->nx;
    size_t ny = grid->ny;

    for (size_t i = 0; i < nx; ++i) {
        size_t idx_bot = i * ny + 0;
        grid->phi[idx_bot] = v_bot;
        grid->is_boundary[idx_bot] = true;

        size_t idx_top = i * ny + (ny - 1);
        grid->phi[idx_top] = v_top;
        grid->is_boundary[idx_top] = true;
    }

    for (size_t j = 0; j < ny; ++j) {
        size_t idx_left = 0 * ny + j;
        grid->phi[idx_left] = v_left;
        grid->is_boundary[idx_left] = true;

        size_t idx_right = (nx - 1) * ny + j;
        grid->phi[idx_right] = v_right;
        grid->is_boundary[idx_right] = true;
    }
}

/* Одна ітерація метода SOR. Повертає максимальну зміну (L-infinity норму) */
double poisson_step_sor(PoissonGrid2D *grid, double omega, double eps) {
    size_t nx = grid->nx;
    size_t ny = grid->ny;
    double h2 = grid->h * grid->h;
    double max_diff = 0.0;

    for (size_t i = 1; i < nx - 1; ++i) {
        for (size_t j = 1; j < ny - 1; ++j) {
            size_t idx = i * ny + j;
            if (grid->is_boundary[idx]) continue;

            size_t idx_ip1 = (i + 1) * ny + j;
            size_t idx_im1 = (i - 1) * ny + j;
            size_t idx_jp1 = i * ny + (j + 1);
            size_t idx_jm1 = i * ny + (j - 1);

            double phi_gs = 0.25 * (grid->phi[idx_ip1] + grid->phi[idx_im1] +
                                    grid->phi[idx_jp1] + grid->phi[idx_jm1]) +
                            0.25 * h2 * (grid->rho[idx] / eps);

            double old_val = grid->phi[idx];
            double new_val = (1.0 - omega) * old_val + omega * phi_gs;
            grid->phi[idx] = new_val;

            double diff = fabs(new_val - old_val);
            if (diff > max_diff) {
                max_diff = diff;
            }
        }
    }
    return max_diff;
}

/* Ітераційний цикл розв'язання до досягнення точності tolerance */
size_t poisson_solve(PoissonGrid2D *grid, double omega, double eps, double tolerance, size_t max_iters) {
    for (size_t iter = 0; iter < max_iters; ++iter) {
        double diff = poisson_step_sor(grid, omega, eps);
        if (diff < tolerance) {
            return iter + 1;
        }
    }
    return max_iters;
}
