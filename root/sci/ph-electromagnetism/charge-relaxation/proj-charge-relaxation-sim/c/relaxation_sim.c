/*
 * relaxation_sim.c — Програма чисельного моделювання релаксації заряду (Мова C)
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define EPS0 8.854187817e-12

typedef struct {
    int n_grid;
    double dx;
    double dt;
    double *eps;
    double *sigma;
    double *rho;
    double *potential;
    double *j_current;
} Grid1D;

Grid1D* grid1d_create(int n_grid, double length) {
    Grid1D *g = (Grid1D*)malloc(sizeof(Grid1D));
    if (!g) return NULL;

    g->n_grid = n_grid;
    g->dx = length / (n_grid - 1);
    g->dt = 0.0;

    g->eps = (double*)calloc(n_grid, sizeof(double));
    g->sigma = (double*)calloc(n_grid, sizeof(double));
    g->rho = (double*)calloc(n_grid, sizeof(double));
    g->potential = (double*)calloc(n_grid, sizeof(double));
    g->j_current = (double*)calloc(n_grid - 1, sizeof(double));

    return g;
}

void grid1d_free(Grid1D *g) {
    if (!g) return;
    free(g->eps);
    free(g->sigma);
    free(g->rho);
    free(g->potential);
    free(g->j_current);
    free(g);
}

/* Обчислення електричного потенціалу шляхом розв'язання рівняння Пуассона 1D */
void solve_poisson(Grid1D *g, double v_left, double v_right) {
    int n = g->n_grid;
    double dx2 = g->dx * g->dx;

    /* Проста ітераційна процедура методом Гаусса-Зайделя */
    g->potential[0] = v_left;
    g->potential[n - 1] = v_right;

    for (int iter = 0; iter < 2000; iter++) {
        for (int i = 1; i < n - 1; i++) {
            double eps_avg = 0.5 * (g->eps[i] + g->eps[i + 1]);
            double rho_val = g->rho[i];
            g->potential[i] = 0.5 * (g->potential[i - 1] + g->potential[i + 1] + (rho_val * dx2) / eps_avg);
        }
    }
}

/* Крок часової інтеграції рівняння неперервності */
void step_relaxation(Grid1D *g) {
    int n = g->n_grid;

    /* 1. Розрахунок струму на межах комірок */
    for (int i = 0; i < n - 1; i++) {
        double sigma_edge = 0.5 * (g->sigma[i] + g->sigma[i + 1]);
        double e_field = (g->potential[i] - g->potential[i + 1]) / g->dx;
        g->j_current[i] = sigma_edge * e_field;
    }

    /* 2. Оновлення об'ємного заряду */
    for (int i = 1; i < n - 1; i++) {
        double div_j = (g->j_current[i] - g->j_current[i - 1]) / g->dx;
        g->rho[i] -= g->dt * div_j;
    }
}

int main(void) {
    int n_pts = 101;
    double length = 0.01; /* 1 см */
    Grid1D *g = grid1d_create(n_pts, length);

    /* Налаштування двох середовищ (Максвелл-Вагнер): ліве і праве */
    for (int i = 0; i < n_pts; i++) {
        if (i < n_pts / 2) {
            g->eps[i] = 4.0 * EPS0;   /* εr1 = 4 */
            g->sigma[i] = 1e-6;       /* σ1 = 1 мкСм/м */
        } else {
            g->eps[i] = 10.0 * EPS0;  /* εr2 = 10 */
            g->sigma[i] = 1e-5;       /* σ2 = 10 мкСм/м */
        }
        g->rho[i] = 0.0;
    }

    /* Внесення початкової плями заряду у центрі лівого середовища */
    g->rho[25] = 1e-4; /* C/m^3 */

    /* Розрахунок стійкого кроку по часу */
    double min_tau = 4.0 * EPS0 / 1e-5;
    g->dt = 0.1 * min_tau;

    printf("Крок по часу dt = %.3e с, dx = %.3e м\n", g->dt, g->dx);
    printf("Час (с)\t\tЗаряд у вузлі 25\tЗаряд на межі (вузол 50)\n");

    for (int step = 0; step <= 100; step++) {
        solve_poisson(g, 10.0, 0.0);
        
        if (step % 20 == 0) {
            double current_time = step * g->dt;
            printf("%.3e\t%.6e\t%.6e\n", current_time, g->rho[25], g->rho[50]);
        }

        step_relaxation(g);
    }

    grid1d_free(g);
    return 0;
}
