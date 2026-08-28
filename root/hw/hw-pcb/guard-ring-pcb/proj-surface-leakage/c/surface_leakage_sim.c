/* surface_leakage_sim.c - 2D FDM Laplace solver for PCB surface leakage */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define GRID_W 80
#define GRID_H 80
#define CELL_SIZE_MM 0.1     /* Крок сітки: 0.1 мм на клітинку (плата 8x8 мм) */
#define SHEET_RES_OHM 1.0e10   /* Поверхневий опір зволоженого FR-4: 10 ГОм/квадрат */
#define MAX_ITER 10000
#define CONV_TOL 1.0e-6
#define OMEGA_SOR 1.75       /* Параметр прискорення збіжності SOR */

typedef enum {
    NODE_DIELECTRIC = 0,
    NODE_POWER_RAIL,
    NODE_HIGH_Z,
    NODE_GUARD_RING,
    NODE_GROUND
} NodeType;

typedef struct {
    double v[GRID_H][GRID_W];
    NodeType type[GRID_H][GRID_W];
} PcbMesh;

static void init_mesh(PcbMesh *mesh, bool enable_guard) {
    for (int y = 0; y < GRID_H; ++y) {
        for (int x = 0; x < GRID_W; ++x) {
            mesh->v[y][x] = 0.0;
            mesh->type[y][x] = NODE_DIELECTRIC;

            /* Зовнішня рамка - земляний полігон GND */
            if (x == 0 || x == GRID_W - 1 || y == 0 || y == GRID_H - 1) {
                mesh->type[y][x] = NODE_GROUND;
                mesh->v[y][x] = 0.0;
            }
            /* Шина живлення +15 В (ліва вертикальна смуга x = 10..14, y = 15..65) */
            else if (x >= 10 && x <= 14 && y >= 15 && y <= 65) {
                mesh->type[y][x] = NODE_POWER_RAIL;
                mesh->v[y][x] = 15.0;
            }
            /* Чутливий контактний майданчик High-Z (центр: x = 45..51, y = 37..43) */
            else if (x >= 45 && x <= 51 && y >= 37 && y <= 43) {
                mesh->type[y][x] = NODE_HIGH_Z;
                mesh->v[y][x] = 0.0; /* Віртуальна земля 0.0 В */
            }
            /* Охоронне кільце Guard Ring навколо High-Z (якщо увімкнено) */
            else if (enable_guard) {
                bool in_outer_box = (x >= 37 && x <= 59 && y >= 29 && y <= 51);
                bool in_inner_gap = (x >= 40 && x <= 56 && y >= 32 && y <= 48);

                if (in_outer_box && !in_inner_gap) {
                    mesh->type[y][x] = NODE_GUARD_RING;
                    mesh->v[y][x] = 0.0; /* V_guard = V_node = 0.0 В */
                }
            }
        }
    }
}

static int solve_laplace(PcbMesh *mesh) {
    int iter = 0;
    double max_diff;

    do {
        max_diff = 0.0;
        for (int y = 1; y < GRID_H - 1; ++y) {
            for (int x = 1; x < GRID_W - 1; ++x) {
                if (mesh->type[y][x] != NODE_DIELECTRIC) {
                    continue; /* Граничні умови Діріхле не змінюються */
                }

                double v_old = mesh->v[y][x];
                double v_relaxed = 0.25 * (mesh->v[y + 1][x] + mesh->v[y - 1][x] +
                                          mesh->v[y][x + 1] + mesh->v[y - 1][x]);
                double v_new = v_old + OMEGA_SOR * (v_relaxed - v_old);

                mesh->v[y][x] = v_new;
                double diff = fabs(v_new - v_old);
                if (diff > max_diff) {
                    max_diff = diff;
                }
            }
        }
        iter++;
    } while (max_diff > CONV_TOL && iter < MAX_ITER);

    return iter;
}

static double calculate_leakage_current(const PcbMesh *mesh) {
    double total_flux = 0.0;
    double sigma_s = 1.0 / SHEET_RES_OHM; /* Поверхнева провідність (См) */

    for (int y = 1; y < GRID_H - 1; ++y) {
        for (int x = 1; x < GRID_W - 1; ++x) {
            if (mesh->type[y][x] == NODE_HIGH_Z) {
                const int dx[4] = {1, -1, 0, 0};
                const int dy[4] = {0, 0, 1, -1};

                for (int d = 0; d < 4; ++d) {
                    int nx = x + dx[d];
                    int ny = y + dy[d];
                    if (mesh->type[ny][nx] == NODE_DIELECTRIC) {
                        double dv = mesh->v[ny][nx] - mesh->v[y][x];
                        total_flux += dv;
                    }
                }
            }
        }
    }

    return sigma_s * total_flux;
}

int main(void) {
    PcbMesh mesh_no_guard;
    PcbMesh mesh_with_guard;

    printf("=== СИМУЛЯТОР ПОВЕРХНЕВОГО ВИТОКУ НА ДРУКОВАНІЙ ПЛАТІ ===\n");
    printf("Поверхневий опір діелектрика: %.1e Ом/кв\n", SHEET_RES_OHM);
    printf("Розмір розрахункової сітки: %dx%d (крок %.2f мм)\n\n",
           GRID_W, GRID_H, CELL_SIZE_MM);

    /* 1. Розрахунок без Guard Ring */
    init_mesh(&mesh_no_guard, false);
    int iter1 = solve_laplace(&mesh_no_guard);
    double i_leak_no_guard = calculate_leakage_current(&mesh_no_guard);

    /* 2. Розрахунок з Guard Ring */
    init_mesh(&mesh_with_guard, true);
    int iter2 = solve_laplace(&mesh_with_guard);
    double i_leak_with_guard = calculate_leakage_current(&mesh_with_guard);

    printf("--- РЕЗУЛЬТАТИ МОДЕЛЮВАННЯ ---\n");
    printf("1. Без Guard Ring:\n");
    printf("   - Ітерацій збіжності: %d\n", iter1);
    printf("   - Струм витоку в High-Z вузол: %.3e А (%.2f пА)\n",
           i_leak_no_guard, i_leak_no_guard * 1.0e12);

    printf("\n2. З охоронним кільцем Guard Ring (V_guard = 0.0 В):\n");
    printf("   - Ітерацій збіжності: %d\n", iter2);
    printf("   - Струм витоку в High-Z вузол: %.3e А (%.2f фА)\n",
           i_leak_with_guard, i_leak_with_guard * 1.0e15);

    double attenuation = (i_leak_with_guard > 1.0e-25) ?
                         (i_leak_no_guard / i_leak_with_guard) : 1.0e12;
    printf("\nКоефіцієнт придушення витоку: %.1e разів\n", attenuation);

    return 0;
}
