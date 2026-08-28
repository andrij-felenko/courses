/* sim_line.c — Симуляція зосередженого LC-ланцюга мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAX_CELLS 1000

typedef struct {
    int num_cells;
    double l_total;     /* Загальна індуктивність (Гн) */
    double c_total;     /* Загальна ємність (Ф) */
    double r_load;      /* Опір навантаження (Ом) */
    double v_nodes[MAX_CELLS + 1];
    double i_branches[MAX_CELLS];
} LCChain;

void lc_chain_init(LCChain *chain, int num_cells, double l_tot, double c_tot, double r_load) {
    if (num_cells > MAX_CELLS) num_cells = MAX_CELLS;
    chain->num_cells = num_cells;
    chain->l_total = l_tot;
    chain->c_total = c_tot;
    chain->r_load = r_load;
    for (int i = 0; i <= num_cells; i++) chain->v_nodes[i] = 0.0;
    for (int i = 0; i < num_cells; i++) chain->i_branches[i] = 0.0;
}

void lc_chain_step(LCChain *chain, double v_in, double dt) {
    double l_cell = chain->l_total / chain->num_cells;
    double c_cell = chain->c_total / chain->num_cells;
    int n = chain->num_cells;

    /* Вхідна напруга на першому вузлі */
    chain->v_nodes[0] = v_in;

    /* Оновлення струмів у гілках (dI/dt = ΔV / L) */
    for (int k = 0; k < n - 1; k++) {
        double v_diff = chain->v_nodes[k] - chain->v_nodes[k + 1];
        chain->i_branches[k] += (v_diff / l_cell) * dt;
    }

    /* Останній струм з урахуванням навантаження R_load */
    double v_last = chain->v_nodes[n - 1];
    double v_out = chain->v_nodes[n];
    chain->i_branches[n - 1] += ((v_last - v_out) / l_cell) * dt;

    /* Оновлення напруг у вузлах (dV/dt = ΔI / C) */
    for (int k = 1; k < n; k++) {
        double i_diff = chain->i_branches[k - 1] - chain->i_branches[k];
        chain->v_nodes[k] += (i_diff / c_cell) * dt;
    }

    /* Напруга на навантаженні: I_out = V_out / R_load */
    double i_load = v_out / chain->r_load;
    chain->v_nodes[n] += ((chain->i_branches[n - 1] - i_load) / c_cell) * dt;
}

int main(void) {
    double l_total = 100e-9; /* 100 нГн */
    double c_total = 40e-12;  /* 40 пФ */
    double z0 = sqrt(l_total / c_total); /* Z0 ≈ 50 Ом */
    double r_load = 50.0;     /* Узгоджене навантаження */
    double t_prop = sqrt(l_total * c_total); /* Час затримки лінії ≈ 2 нс */

    printf("=== Порівняння апроксимації зосереджених LC-осередків ===\n");
    printf("Характерний хвильовий опір Z0 = %.2f Ом\n", z0);
    printf("Фізичний час затримки лінії t_prop = %.3f нс\n\n", t_prop * 1e9);

    int test_cells[] = {1, 4, 16, 64};
    double dt = 1e-12; /* 1 пс */
    double t_sim = 6e-9; /* 6 нс симуляції */

    for (int idx = 0; idx < 4; idx++) {
        int cells = test_cells[idx];
        LCChain chain;
        lc_chain_init(&chain, cells, l_total, c_total, r_load);

        double t_50percent = -1.0;
        for (double t = 0; t <= t_sim; t += dt) {
            /* Перехідний фронт зі швидкістю наростання 0.2 нс */
            double v_in = (t < 0.2e-9) ? (t / 0.2e-9) : 1.0;
            lc_chain_step(&chain, v_in, dt);

            double v_out = chain.v_nodes[cells];
            if (v_out >= 0.5 && t_50percent < 0) {
                t_50percent = t;
            }
        }
        printf("Накладені осередки N = %2d | Затримка фронту (50%% V_max): %.3f нс\n",
               cells, t_50percent * 1e9);
    }

    return 0;
}
