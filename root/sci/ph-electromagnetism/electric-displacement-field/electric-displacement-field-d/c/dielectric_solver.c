/* dielectric_solver.c — 2D чисельний розв'язувач рівняння Пуассона для вектора D */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 80
#define NY 80
#define EPS0 8.854e-12

typedef struct {
    double phi[NX][NY];
    double eps_r[NX][NY];
    double rho_free[NX][NY];
    double Ex[NX][NY];
    double Ey[NX][NY];
    double Dx[NX][NY];
    double Dy[NX][NY];
} Grid2D;

void init_dielectric_grid(Grid2D *g) {
    int i, j;
    for (i = 0; i < NX; i++) {
        for (j = 0; j < NY; j++) {
            g->phi[i][j] = 0.0;
            g->rho_free[i][j] = 0.0;
            /* Нижня половина: повітря (eps_r = 1.0), верхня: кераміка (eps_r = 5.0) */
            if (j < NY / 2) {
                g->eps_r[i][j] = 1.0;
            } else {
                g->eps_r[i][j] = 5.0;
            }
        }
    }
    /* Задаємо граничні умови для потенціалу (конденсатор 100 В) */
    for (i = 0; i < NX; i++) {
        g->phi[i][0] = 0.0;          /* Нижня пластина = 0 В */
        g->phi[i][NY - 1] = 100.0;   /* Верхня пластина = 100 В */
    }
}

void solve_poisson_sor(Grid2D *g, int max_iter, double omega) {
    int iter, i, j;
    double h = 1.0 / (NX - 1);
    for (iter = 0; iter < max_iter; iter++) {
        for (i = 1; i < NX - 1; i++) {
            for (j = 1; j < NY - 1; j++) {
                double eps_e = 0.5 * (g->eps_r[i][j] + g->eps_r[i + 1][j]);
                double eps_w = 0.5 * (g->eps_r[i][j] + g->eps_r[i - 1][j]);
                double eps_n = 0.5 * (g->eps_r[i][j] + g->eps_r[i][j + 1]);
                double eps_s = 0.5 * (g->eps_r[i][j] + g->eps_r[i][j - 1]);

                double num = eps_e * g->phi[i + 1][j] + eps_w * g->phi[i - 1][j] +
                             eps_n * g->phi[i][j + 1] + eps_s * g->phi[i][j - 1] +
                             (h * h * g->rho_free[i][j] / EPS0);
                double den = eps_e + eps_w + eps_n + eps_s;
                double phi_new = num / den;

                g->phi[i][j] = g->phi[i][j] + omega * (phi_new - g->phi[i][j]);
            }
        }
    }
}

void compute_fields(Grid2D *g) {
    int i, j;
    double h = 1.0 / (NX - 1);
    for (i = 1; i < NX - 1; i++) {
        for (j = 1; j < NY - 1; j++) {
            g->Ex[i][j] = -(g->phi[i + 1][j] - g->phi[i - 1][j]) / (2.0 * h);
            g->Ey[i][j] = -(g->phi[i][j + 1] - g->phi[i][j - 1]) / (2.0 * h);

            /* D = eps0 * eps_r * E */
            g->Dx[i][j] = EPS0 * g->eps_r[i][j] * g->Ex[i][j];
            g->Dy[i][j] = EPS0 * g->eps_r[i][j] * g->Ey[i][j];
        }
    }
}

int main(void) {
    Grid2D *g = (Grid2D *)malloc(sizeof(Grid2D));
    if (!g) return 1;

    init_dielectric_grid(g);
    solve_poisson_sor(g, 2000, 1.85);
    compute_fields(g);

    int mid_x = NX / 2;
    int j_air = NY / 4;
    int j_cer = 3 * NY / 4;

    printf("Результати чисельного розрахунку полів D та E:\n");
    printf("Повітря (j=%d):  Ey = %.3f В/м, Dy = %.3e Кл/м²\n",
           j_air, g->Ey[mid_x][j_air], g->Dy[mid_x][j_air]);
    printf("Кераміка (j=%d): Ey = %.3f В/м, Dy = %.3e Кл/м²\n",
           j_cer, g->Ey[mid_x][j_cer], g->Dy[mid_x][j_cer]);

    free(g);
    return 0;
}
