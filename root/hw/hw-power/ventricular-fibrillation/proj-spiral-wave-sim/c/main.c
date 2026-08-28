#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 150
#define NY 150

typedef struct {
    double v[NY][NX];
    double w[NY][NX];
    double v_next[NY][NX];
    double w_next[NY][NX];
    double dt;
    double dx;
    double diff_const;
    double param_a;
    double param_eps;
    double param_gamma;
    double param_beta;
} CardiacGridC;

void grid_init(CardiacGridC *g) {
    g->dt = 0.04;
    g->dx = 0.5;
    g->diff_const = 1.0;
    g->param_a = 0.1;
    g->param_eps = 0.01;
    g->param_gamma = 0.5;
    g->param_beta = 0.0;

    for (int y = 0; y < NY; y++) {
        for (int x = 0; x < NX; x++) {
            g->v[y][x] = 0.0;
            g->w[y][x] = 0.0;
            g->v_next[y][x] = 0.0;
            g->w_next[y][x] = 0.0;
        }
    }
}

void apply_boundary_conditions(CardiacGridC *g) {
    for (int x = 0; x < NX; x++) {
        g->v[0][x] = g->v[1][x];
        g->v[NY - 1][x] = g->v[NY - 2][x];
    }
    for (int y = 0; y < NY; y++) {
        g->v[y][0] = g->v[y][1];
        g->v[y][NX - 1] = g->v[y][NX - 2];
    }
}

void apply_s1_stimulus(CardiacGridC *g) {
    for (int y = 0; y < NY; y++) {
        for (int x = 0; x < 5; x++) {
            g->v[y][x] = 0.9;
        }
    }
}

void apply_s2_stimulus(CardiacGridC *g) {
    for (int y = 0; y < NY / 2; y++) {
        for (int x = 0; x < NX / 2; x++) {
            g->v[y][x] = 0.9;
        }
    }
}

void grid_step(CardiacGridC *g) {
    apply_boundary_conditions(g);

    double idx2 = 1.0 / (g->dx * g->dx);
    for (int y = 1; y < NY - 1; y++) {
        for (int x = 1; x < NX - 1; x++) {
            double v_val = g->v[y][x];
            double w_val = g->w[y][x];

            double laplacian = (g->v[y + 1][x] + g->v[y - 1][x] +
                                g->v[y][x + 1] + g->v[y][x - 1] - 4.0 * v_val) * idx2;

            double f_v = v_val * (1.0 - v_val) * (v_val - g->param_a) - w_val;
            double g_v = g->param_gamma * v_val - g->param_beta - w_val;

            g->v_next[y][x] = v_val + g->dt * (g->diff_const * laplacian + f_v);
            g->w_next[y][x] = w_val + g->dt * (g->param_eps * g_v);
        }
    }

    for (int y = 1; y < NY - 1; y++) {
        for (int x = 1; x < NX - 1; x++) {
            g->v[y][x] = g->v_next[y][x];
            g->w[y][x] = g->w_next[y][x];
        }
    }
}

int count_phase_singularities(const CardiacGridC *g) {
    int singularities = 0;
    for (int y = 5; y < NY - 5; y += 2) {
        for (int x = 5; x < NX - 5; x += 2) {
            double v_val = g->v[y][x];
            double w_val = g->w[y][x];
            if (fabs(v_val - 0.2) < 0.05 && fabs(w_val - 0.05) < 0.02) {
                singularities++;
            }
        }
    }
    return singularities;
}

int main(void) {
    CardiacGridC grid;
    grid_init(&grid);

    printf("Початок моделювання S1-S2 протоколу...\n");
    apply_s1_stimulus(&grid);

    for (int step = 0; step < 1000; step++) {
        grid_step(&grid);

        if (step == 220) {
            printf("Подача передчасного стимулу S2 на кроці %d...\n", step);
            apply_s2_stimulus(&grid);
        }

        if (step % 200 == 0) {
            int ps = count_phase_singularities(&grid);
            printf("Крок %4d: V в центрі = %.3f, фазових сингулярностей ≈ %d\n",
                   step, grid.v[NY / 2][NX / 2], ps);
        }
    }

    printf("Моделювання успішно завершено.\n");
    return 0;
}
