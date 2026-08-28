#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 41
#define NY 41
#define STEPS 120
#define DX 0.2
#define DY 0.2
#define DT 0.05
#define CS2 0.333333

typedef struct {
    double e[NX][NY];
    double vx[NX][NY];
    double vy[NX][NY];
} HydroGrid;

void init_glauber_ellipse(HydroGrid *grid, double rx, double ry, double e0) {
    int cx = NX / 2;
    int cy = NY / 2;

    for (int i = 0; i < NX; i++) {
        for (int j = 0; j < NY; j++) {
            double x = (i - cx) * DX;
            double y = (j - cy) * DY;
            double r2_ell = (x * x) / (rx * rx) + (y * y) / (ry * ry);

            if (r2_ell <= 1.0) {
                grid->e[i][j] = e0 * (1.0 - r2_ell);
            } else {
                grid->e[i][j] = 0.0;
            }
            grid->vx[i][j] = 0.0;
            grid->vy[i][j] = 0.0;
        }
    }
}

void step_hydrodynamics(HydroGrid *grid) {
    static double next_e[NX][NY];
    static double next_vx[NX][NY];
    static double next_vy[NX][NY];

    for (int i = 1; i < NX - 1; i++) {
        for (int j = 1; j < NY - 1; j++) {
            double de_dx = (grid->e[i + 1][j] - grid->e[i - 1][j]) / (2.0 * DX);
            double de_dy = (grid->e[i][j + 1] - grid->e[i][j - 1]) / (2.0 * DY);

            double e_curr = grid->e[i][j] + 1e-6;
            double p_curr = CS2 * e_curr;
            double dp_dx = CS2 * de_dx;
            double dp_dy = CS2 * de_dy;

            /* Прискорення за рахунок градієнта тиску grad(P) / (e + P) */
            double ax = -dp_dx / (e_curr + p_curr);
            double ay = -dp_dy / (e_curr + p_curr);

            next_vx[i][j] = grid->vx[i][j] + ax * DT;
            next_vy[i][j] = grid->vy[i][j] + ay * DT;

            /* Перенос енергії div(e * v) */
            double div_ev = (grid->e[i + 1][j] * grid->vx[i + 1][j] - grid->e[i - 1][j] * grid->vx[i - 1][j]) / (2.0 * DX) +
                            (grid->e[i][j + 1] * grid->vy[i][j + 1] - grid->e[i][j - 1] * grid->vy[i][j - 1]) / (2.0 * DY);

            next_e[i][j] = grid->e[i][j] - div_ev * DT;
            if (next_e[i][j] < 0.0) next_e[i][j] = 0.0;
        }
    }

    for (int i = 1; i < NX - 1; i++) {
        for (int j = 1; j < NY - 1; j++) {
            grid->e[i][j] = next_e[i][j];
            grid->vx[i][j] = next_vx[i][j];
            grid->vy[i][j] = next_vy[i][j];
        }
    }
}

double calculate_v2(const HydroGrid *grid) {
    double sum_num = 0.0;
    double sum_den = 0.0;

    for (int i = 0; i < NX; i++) {
        for (int j = 0; j < NY; j++) {
            double e_val = grid->e[i][j];
            double vx = grid->vx[i][j];
            double vy = grid->vy[i][j];

            double px = e_val * vx;
            double py = e_val * vy;

            double p2 = px * px + py * py;
            if (p2 > 1e-8) {
                sum_num += (px * px - py * py);
                sum_den += (px * px + py * py);
            }
        }
    }
    return (sum_den > 0.0) ? (sum_num / sum_den) : 0.0;
}

int main(void) {
    HydroGrid *grid = (HydroGrid *)calloc(1, sizeof(HydroGrid));
    if (!grid) return 1;

    /* Створення початкового еліпса: Rx = 2.0 fm, Ry = 3.5 fm (еліптична анізотропія) */
    init_glauber_ellipse(grid, 2.0, 3.5, 10.0);

    printf("Крок 0: початковий v2 = %.4f\n", calculate_v2(grid));

    for (int step = 1; step <= STEPS; step++) {
        step_hydrodynamics(grid);
        if (step % 30 == 0) {
            printf("Крок %d: v2 = %.4f\n", step, calculate_v2(grid));
        }
    }

    free(grid);
    return 0;
}
