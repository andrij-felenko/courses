#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NX 64
#define NY 32
#define MAX_ITER 5000
#define TOL 1e-5
#define SIGMA 5.8e7  /* Питома провідність міді [См/м] */

typedef struct {
    double v[NY][NX];
    double jx[NY][NX];
    double jy[NY][NX];
    int mask[NY][NX];  /* 1 - провідник, 0 - отвір / повітря */
} FieldGrid;

void init_grid(FieldGrid *g) {
    int i, j;
    for (j = 0; j < NY; j++) {
        for (i = 0; i < NX; i++) {
            g->v[j][i] = 0.0;
            g->jx[j][i] = 0.0;
            g->jy[j][i] = 0.0;
            g->mask[j][i] = 1;
            
            /* Створюємо прямокутне звуження (вирізи зверху й знизу в центрі) */
            if (i >= 24 && i <= 40) {
                if (j < 10 || j > 21) {
                    g->mask[j][i] = 0; /* виріз */
                }
            }
        }
    }
    
    /* Граничні умови Дирихле: Вхід V = 10.0 В (i=0), Вихід V = 0.0 В (i=NX-1) */
    for (j = 0; j < NY; j++) {
        if (g->mask[j][0]) g->v[j][0] = 10.0;
        if (g->mask[j][NX-1]) g->v[j][NX-1] = 0.0;
    }
}

void solve_potential(FieldGrid *g) {
    int iter, i, j;
    double max_diff;

    for (iter = 0; iter < MAX_ITER; iter++) {
        max_diff = 0.0;
        for (j = 1; j < NY - 1; j++) {
            for (i = 1; i < NX - 1; i++) {
                if (!g->mask[j][i]) continue;

                double old_v = g->v[j][i];
                double sum = 0.0;
                int count = 0;

                /* Ураховуємо диференціальні межі з ізолятором */
                if (g->mask[j][i+1]) { sum += g->v[j][i+1]; count++; }
                if (g->mask[j][i-1]) { sum += g->v[j][i-1]; count++; }
                if (g->mask[j+1][i]) { sum += g->v[j+1][i]; count++; }
                if (g->mask[j-1][i]) { sum += g->v[j-1][i]; count++; }

                if (count > 0) {
                    g->v[j][i] = sum / (double)count;
                    double diff = fabs(g->v[j][i] - old_v);
                    if (diff > max_diff) max_diff = diff;
                }
            }
        }
        if (max_diff < TOL) break;
    }
}

void compute_current_density(FieldGrid *g, double h) {
    int i, j;
    for (j = 1; j < NY - 1; j++) {
        for (i = 1; i < NX - 1; i++) {
            if (!g->mask[j][i]) continue;

            double dv_dx = (g->v[j][i+1] - g->v[j][i-1]) / (2.0 * h);
            double dv_dy = (g->v[j+1][i] - g->v[j-1][i]) / (2.0 * h);

            g->jx[j][i] = -SIGMA * dv_dx;
            g->jy[j][i] = -SIGMA * dv_dy;
        }
    }
}

int main(void) {
    FieldGrid *grid = (FieldGrid *)calloc(1, sizeof(FieldGrid));
    if (!grid) return 1;

    init_grid(grid);
    solve_potential(grid);
    compute_current_density(grid, 0.001); /* крок сітки h = 1 мм */

    /* Виводимо значення щільності струму у центрі звуження (i=32, j=16) */
    double j_mag = sqrt(grid->jx[16][32] * grid->jx[16][32] + grid->jy[16][32] * grid->jy[16][32]);
    printf("Розрахунок завершено.\n");
    printf("Щільність струму у звуженні J(32,16) = %.3e А/м²\n", j_mag);

    free(grid);
    return 0;
}
