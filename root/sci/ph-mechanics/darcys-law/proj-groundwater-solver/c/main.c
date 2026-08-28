/* C implementation of 2D Darcy Groundwater Solver */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 50
#define NY 50
#define MAX_ITER 5000
#define TOL 1e-5
#define OMEGA 1.75  /* Релаксаційний параметр SOR */

typedef struct {
    double p[NX][NY];
    double k[NX][NY];
    double vx[NX][NY];
    double vy[NX][NY];
    double dx;
    double dy;
    double visco;
} DarcyGrid;

void init_grid(DarcyGrid *grid) {
    grid->dx = 1.0; /* крок сітки в метрах */
    grid->dy = 1.0;
    grid->visco = 1.0e-3; /* в'язкість води Па·с */

    for (int i = 0; i < NX; ++i) {
        for (int j = 0; j < NY; ++j) {
            grid->p[i][j] = 0.0;
            grid->k[i][j] = 1.0e-11; /* базовий пісок: 10 Дарсі = 10^-11 м² */
            grid->vx[i][j] = 0.0;
            grid->vy[i][j] = 0.0;

            /* Створення нееднорідності: непроникний глиняний бар'єр у центрі */
            if (i >= 20 && i <= 30 && j >= 15 && j <= 35) {
                grid->k[i][j] = 1.0e-15; /* глина: 1 мікродарсі = 10^-15 м² */
            }
        }
    }

    /* Граничні умови: заданий тиск на лівій та правій межах (градієнт) */
    for (int j = 0; j < NY; ++j) {
        grid->p[0][j] = 100000.0; /* 100 кПа зліва */
        grid->p[NX - 1][j] = 0.0; /* 0 Па справа */
    }
}

void solve_darcy_pressure(DarcyGrid *grid) {
    for (int iter = 0; iter < MAX_ITER; ++iter) {
        double max_err = 0.0;

        for (int i = 1; i < NX - 1; ++i) {
            for (int j = 1; j < NY - 1; ++j) {
                /* Усереднена гармонічна проникність між суміжними комірками */
                double k_east  = 2.0 * grid->k[i][j] * grid->k[i+1][j] / (grid->k[i][j] + grid->k[i+1][j]);
                double k_west  = 2.0 * grid->k[i][j] * grid->k[i-1][j] / (grid->k[i][j] + grid->k[i-1][j]);
                double k_north = 2.0 * grid->k[i][j] * grid->k[i][j+1] / (grid->k[i][j] + grid->k[i][j+1]);
                double k_south = 2.0 * grid->k[i][j] * grid->k[i][j-1] / (grid->k[i][j] + grid->k[i][j-1]);

                double denom = k_east + k_west + k_north + k_south;
                double p_new = (k_east * grid->p[i+1][j] + k_west * grid->p[i-1][j] +
                                k_north * grid->p[i][j+1] + k_south * grid->p[i][j-1]) / denom;

                double diff = fabs(p_new - grid->p[i][j]);
                if (diff > max_err) max_err = diff;

                /* SOR оновлення */
                grid->p[i][j] += OMEGA * (p_new - grid->p[i][j]);
            }
        }

        if (max_err < TOL) {
            printf("Збіжність досягнута за %d ітерацій.\n", iter);
            break;
        }
    }
}

void compute_darcy_velocities(DarcyGrid *grid) {
    for (int i = 1; i < NX - 1; ++i) {
        for (int j = 1; j < NY - 1; ++j) {
            double dp_dx = (grid->p[i+1][j] - grid->p[i-1][j]) / (2.0 * grid->dx);
            double dp_dy = (grid->p[i][j+1] - grid->p[i][j-1]) / (2.0 * grid->dy);

            /* Вектор Дарсі: v_d = - (k / μ) * ∇p */
            grid->vx[i][j] = - (grid->k[i][j] / grid->visco) * dp_dx;
            grid->vy[i][j] = - (grid->k[i][j] / grid->visco) * dp_dy;
        }
    }
}

int main(void) {
    DarcyGrid grid;
    init_grid(&grid);
    solve_darcy_pressure(&grid);
    compute_darcy_velocities(&grid);

    printf("Тиск у центрі пласта (25,25): %.2f Па\n", grid.p[NX/2][NY/2]);
    printf("Швидкість Дарсі vx у комірці (10,25): %.4e м/с\n", grid.vx[10][NY/2]);
    printf("Швидкість Дарсі vx у бар'єрі (25,25): %.4e м/с\n", grid.vx[NX/2][NY/2]);
    return 0;
}
