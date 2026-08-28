#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура конфігурації симуляції зонного очищення кремнію */
typedef struct {
    int num_cells;       /* Загальна кількість осередків сітки (M) */
    int zone_cells;      /* Кількість осередків у розплавленій зоні (Nz) */
    double k_eff;        /* Ефективний коефіцієнт сегрегації домішки */
    double initial_conc; /* Початкова однорідна концентрація домішки C0 */
} zone_config_t;

/* Виконання одного проходу розплавленої зони вздовж зливка */
void run_single_pass(double *C, const zone_config_t *cfg) {
    int M = cfg->num_cells;
    int Nz = cfg->zone_cells;
    double k = cfg->k_eff;

    double *C_next = (double *)malloc(M * sizeof(double));
    if (!C_next) return;

    for (int i = 0; i < M; i++) {
        C_next[i] = C[i];
    }

    /* 1. Основна фаза: переміщення зони постійної довжини Nz */
    for (int start = 0; start <= M - Nz; start++) {
        double sum_mass = 0.0;
        for (int j = 0; j < Nz; j++) {
            sum_mass += C_next[start + j];
        }

        double C_L = sum_mass / (double)Nz;
        double C_solid = k * C_L;
        C[start] = C_solid;

        double rem_mass = sum_mass - C_solid;
        double C_rem_avg = rem_mass / (double)(Nz - 1);

        for (int j = 1; j < Nz; j++) {
            C_next[start + j] = C_rem_avg;
        }
    }

    /* 2. Кінцева фаза: направлена кристалізація залишку розплавленої зони */
    int end_start = M - Nz + 1;
    for (int start = end_start; start < M - 1; start++) {
        int Nz_curr = M - start;
        double sum_mass = 0.0;
        for (int j = 0; j < Nz_curr; j++) {
            sum_mass += C_next[start + j];
        }

        double C_L = sum_mass / (double)Nz_curr;
        double C_solid = k * C_L;
        C[start] = C_solid;

        double rem_mass = sum_mass - C_solid;
        double C_rem_avg = (Nz_curr > 1) ? (rem_mass / (double)(Nz_curr - 1)) : 0.0;

        for (int j = 1; j < Nz_curr; j++) {
            C_next[start + j] = C_rem_avg;
        }
    }

    /* Останній осередок уміщує точний залишок домішки (закон збереження маси) */
    double total_initial_mass = 0.0;
    double current_crystallized_mass = 0.0;
    for (int i = 0; i < M; i++) total_initial_mass += C_next[i];
    for (int i = 0; i < M - 1; i++) current_crystallized_mass += C[i];

    C[M - 1] = total_initial_mass - current_crystallized_mass;
    if (C[M - 1] < 0.0) C[M - 1] = 0.0;

    free(C_next);
}

int main(void) {
    zone_config_t cfg;
    cfg.num_cells = 100;
    cfg.zone_cells = 10;   /* Відносна довжина зони l/L = 0.10 */
    cfg.k_eff = 0.10;       /* Коефіцієнт сегрегації k = 0.1 */
    cfg.initial_conc = 1.0;

    int num_passes = 10;
    double *C = (double *)malloc(cfg.num_cells * sizeof(double));
    if (!C) return 1;

    for (int i = 0; i < cfg.num_cells; i++) {
        C[i] = cfg.initial_conc;
    }

    for (int p = 1; p <= num_passes; p++) {
        run_single_pass(C, &cfg);
    }

    printf("=== Результати симуляції зонного очищення кремнію (n = %d проходів) ===\n", num_passes);
    printf("Позиція x/L | Концентрація C(x)/C0 | Ступінь очищення\n");
    printf("------------------------------------------------------\n");
    for (int i = 0; i < cfg.num_cells; i += 10) {
        double x_rel = (double)i / (double)cfg.num_cells;
        double purity_factor = (C[i] > 0.0) ? (1.0 / C[i]) : 0.0;
        printf("   %4.2f     |     %.8f     |    %.1f x\n", x_rel, C[i], purity_factor);
    }
    printf("   1.00     |     %.8f     |    накопичення\n", C[cfg.num_cells - 1]);

    free(C);
    return 0;
}
