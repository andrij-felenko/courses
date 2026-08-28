#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 81
#define NY 81
#define EPSILON_0 8.854187817e-12

typedef enum {
    NODE_FREE = 0,
    NODE_CONDUCTOR,
    NODE_SOURCE,
    NODE_GROUND
} NodeKind;

typedef struct {
    double v[NX][NY];
    NodeKind kind[NX][NY];
    double grid_step;
    double v_in;
    double omega;
    double tolerance;
    int max_iterations;
} GridSolver;

void grid_init(GridSolver *s, double v_in, double step) {
    s->grid_step = step;
    s->v_in = v_in;
    s->omega = 1.85;
    s->tolerance = 1e-6;
    s->max_iterations = 5000;

    for (int i = 0; i < NX; ++i) {
        for (int j = 0; j < NY; ++j) {
            s->v[i][j] = 0.0;
            s->kind[i][j] = NODE_FREE;
        }
    }

    // Геометрія L-подібного вигину провідника
    for (int i = 20; i <= 40; ++i) {
        for (int j = 0; j <= 20; ++j) {
            s->kind[i][j] = NODE_CONDUCTOR;
            s->v[i][j] = v_in * (1.0 - (double)j / 80.0);
        }
    }
    for (int i = 20; i <= 80; ++i) {
        for (int j = 20; j <= 40; ++j) {
            s->kind[i][j] = NODE_CONDUCTOR;
            s->v[i][j] = v_in * (1.0 - (double)(i + j) / 120.0);
        }
    }

    // Задання напруги джерела та землі
    for (int i = 20; i <= 40; ++i) {
        s->kind[i][0] = NODE_SOURCE;
        s->v[i][0] = v_in;
    }
    for (int j = 20; j <= 40; ++j) {
        s->kind[NX - 1][j] = NODE_GROUND;
        s->v[NX - 1][j] = 0.0;
    }
}

void grid_solve(GridSolver *s) {
    int iter = 0;
    double max_diff = 0.0;
    do {
        max_diff = 0.0;
        for (int i = 1; i < NX - 1; ++i) {
            for (int j = 1; j < NY - 1; ++j) {
                if (s->kind[i][j] == NODE_SOURCE || s->kind[i][j] == NODE_GROUND) {
                    continue;
                }
                double old_v = s->v[i][j];
                double target = 0.25 * (s->v[i + 1][j] + s->v[i - 1][j] + s->v[i][j + 1] + s->v[i][j - 1]);
                double updated = old_v + s->omega * (target - old_v);
                s->v[i][j] = updated;

                double diff = fabs(updated - old_v);
                if (diff > max_diff) {
                    max_diff = diff;
                }
            }
        }
        iter++;
    } while (max_diff > s->tolerance && iter < s->max_iterations);

    printf("C-солівер виконано за %d ітерацій. Неузгодженість: %.2e В\n", iter, max_diff);
}

double compute_charge(const GridSolver *s, int i, int j, int ndx, int ndy) {
    if (i <= 0 || i >= NX - 1 || j <= 0 || j >= NY - 1) return 0.0;
    double v_surf = s->v[i][j];
    double v_ext = s->v[i + ndx][j + ndy];
    double e_norm = -(v_ext - v_surf) / s->grid_step;
    return EPSILON_0 * e_norm;
}

int main(void) {
    GridSolver solver;
    grid_init(&solver, 12.0, 1e-3);
    grid_solve(&solver);

    double sigma_outer = compute_charge(&solver, 20, 20, -1, -1);
    double sigma_inner = compute_charge(&solver, 40, 40, 1, 1);

    printf("Поверхневий заряд на зовнішньому куті: %.4e Кл/м²\n", sigma_outer);
    printf("Поверхневий заряд на внутрішньому куті: %.4e Кл/м²\n", sigma_inner);

    return 0;
}
