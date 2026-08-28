#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 64
#define NY 64
#define MAX_ITER 2000
#define TOL 1e-6

typedef struct {
    double phi[NX][NY];
    double Ax[NX][NY];
    double Ay[NX][NY];
    double Az[NX][NY];
    double Ex[NX][NY];
    double Ey[NX][NY];
    double Bx[NX][NY];
    double By[NX][NY];
} GridField;

void init_grid(GridField *g) {
    for (int i = 0; i < NX; i++) {
        for (int j = 0; j < NY; j++) {
            g->phi[i][j] = 0.0;
            g->Ax[i][j] = 0.0;
            g->Ay[i][j] = 0.0;
            g->Az[i][j] = 0.0;
            g->Ex[i][j] = 0.0;
            g->Ey[i][j] = 0.0;
            g->Bx[i][j] = 0.0;
            g->By[i][j] = 0.0;
        }
    }
}

/* Ітераційний розв'язувач Пуассона методом Якобі */
void solve_poisson_2d(double field[NX][NY], double rhs[NX][NY], double dx) {
    double next[NX][NY];
    double dx2 = dx * dx;

    for (int iter = 0; iter < MAX_ITER; iter++) {
        double max_diff = 0.0;
        for (int i = 1; i < NX - 1; i++) {
            for (int j = 1; j < NY - 1; j++) {
                next[i][j] = 0.25 * (field[i+1][j] + field[i-1][j] +
                                    field[i][j+1] + field[i][j-1] +
                                    dx2 * rhs[i][j]);
                double diff = fabs(next[i][j] - field[i][j]);
                if (diff > max_diff) max_diff = diff;
            }
        }
        for (int i = 1; i < NX - 1; i++) {
            for (int j = 1; j < NY - 1; j++) {
                field[i][j] = next[i][j];
            }
        }
        if (max_diff < TOL) break;
    }
}

/* Обчислення фізичних полів E та B за потенціалами */
void compute_physical_fields(GridField *g, double dx) {
    for (int i = 1; i < NX - 1; i++) {
        for (int j = 1; j < NY - 1; j++) {
            /* E = -∇φ */
            g->Ex[i][j] = -(g->phi[i+1][j] - g->phi[i-1][j]) / (2.0 * dx);
            g->Ey[i][j] = -(g->phi[i][j+1] - g->phi[i][j-1]) / (2.0 * dx);

            /* B = ∇ × A (двовимірний випадок з Az) */
            g->Bx[i][j] = (g->Az[i][j+1] - g->Az[i][j-1]) / (2.0 * dx);
            g->By[i][j] = -(g->Az[i+1][j] - g->Az[i-1][j]) / (2.0 * dx);
        }
    }
}

/* Калібрувальне перетворення: A -> A + ∇λ, φ -> φ */
void apply_gauge_transform(GridField *g, double dx, double gauge_scale) {
    for (int i = 1; i < NX - 1; i++) {
        for (int j = 1; j < NY - 1; j++) {
            double x = (i - NX / 2.0) * dx;
            double y = (j - NY / 2.0) * dx;
            /* λ(x, y) = gauge_scale * x * y */
            double dlambda_dx = gauge_scale * y;
            double dlambda_dy = gauge_scale * x;

            g->Ax[i][j] += dlambda_dx;
            g->Ay[i][j] += dlambda_dy;
        }
    }
}

int main(void) {
    GridField g;
    init_grid(&g);

    double dx = 0.1;
    double rho[NX][NY] = {0};
    double Jz[NX][NY] = {0};

    /* Точкове джерело заряду та струму в центрі */
    rho[NX/2][NY/2] = 10.0;
    Jz[NX/2][NY/2] = 5.0;

    solve_poisson_2d(g.phi, rho, dx);
    solve_poisson_2d(g.Az, Jz, dx);
    compute_physical_fields(&g, dx);

    double orig_Ex = g.Ex[NX/2 + 5][NY/2 + 5];
    double orig_Bx = g.Bx[NX/2 + 5][NY/2 + 5];

    /* Застосування калібрувального зсуву */
    apply_gauge_transform(&g, dx, 2.5);

    /* Перераховуємо поля після калібрувального зсуву */
    compute_physical_fields(&g, dx);

    double new_Ex = g.Ex[NX/2 + 5][NY/2 + 5];
    double new_Bx = g.Bx[NX/2 + 5][NY/2 + 5];

    printf("Початкове E_x: %f, після калібрування: %f (різниця: %e)\n", orig_Ex, new_Ex, fabs(orig_Ex - new_Ex));
    printf("Початкове B_x: %f, після калібрування: %f (різниця: %e)\n", orig_Bx, new_Bx, fabs(orig_Bx - new_Bx));

    return 0;
}
