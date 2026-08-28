#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MAX_NODES 8
#define MAX_BRANCHES 12
#define MU_0 1.2566370614359173e-6

typedef enum {
    MAT_LINEAR_AIR = 0,
    MAT_FERRITE_N87 = 1
} MaterialType;

typedef struct {
    int node_from;
    int node_to;
    double length;      /* довжина ділянки, м */
    double area;        /* площа перерізу, м^2 */
    double mmf;         /* ампер-витки N*I, А-вит */
    MaterialType mat;   /* тип матеріалу */
    double mu_r0;       /* початкова проникність */
    double b_sat;       /* індукція насичення, Тл */
    /* Розрахункові змінні стану */
    double mu_r;
    double permeance;
    double flux;
    double b_field;
    double h_field;
} MagBranch;

typedef struct {
    int num_nodes;
    int num_branches;
    int ground_node;
    MagBranch branches[MAX_BRANCHES];
} MagCircuit;

/* Розрахунок нелінійної проникності за моделлю Брауера */
static double calc_brauer_mur(double h, double mu_r0, double b_sat) {
    if (h < 1e-9) return mu_r0;
    double h_c = b_sat / (MU_0 * (mu_r0 - 1.0));
    double mu_r = 1.0 + (b_sat / MU_0) / (h + h_c);
    return mu_r;
}

/* Прямий розв'язувач лінійної системи методом Гауса */
static bool solve_linear_system(double A[MAX_NODES][MAX_NODES], double b[MAX_NODES], 
                                double x[MAX_NODES], int n) {
    for (int i = 0; i < n; i++) {
        int max_row = i;
        for (int k = i + 1; k < n; k++) {
            if (fabs(A[k][i]) > fabs(A[max_row][i])) max_row = k;
        }
        for (int k = i; k < n; k++) {
            double tmp = A[i][k]; A[i][k] = A[max_row][k]; A[max_row][k] = tmp;
        }
        double tmp_b = b[i]; b[i] = b[max_row]; b[max_row] = tmp_b;

        if (fabs(A[i][i]) < 1e-20) return false;

        for (int k = i + 1; k < n; k++) {
            double factor = A[k][i] / A[i][i];
            b[k] -= factor * b[i];
            for (int j = i; j < n; j++) A[k][j] -= factor * A[i][j];
        }
    }

    for (int i = n - 1; i >= 0; i--) {
        double sum = 0.0;
        for (int j = i + 1; j < n; j++) sum += A[i][j] * x[j];
        x[i] = (b[i] - sum) / A[i][i];
    }
    return true;
}

/* Ітераційний розрахунок магнітної сітки */
bool solve_magnetic_circuit(MagCircuit *ckt, double tol, int max_iter, double alpha) {
    /* Початкова ініціалізація проникності */
    for (int b = 0; b < ckt->num_branches; b++) {
        ckt->branches[b].mu_r = (ckt->branches[b].mat == MAT_LINEAR_AIR) ? 1.0 : ckt->branches[b].mu_r0;
    }

    int n_eq = ckt->num_nodes - 1; /* без опорного вузла */
    double node_potentials[MAX_NODES] = {0};

    for (int iter = 0; iter < max_iter; iter++) {
        /* Оновлення пермеансів */
        for (int b = 0; b < ckt->num_branches; b++) {
            MagBranch *br = &ckt->branches[b];
            br->permeance = MU_0 * br->mu_r * br->area / br->length;
        }

        /* Побудова вузлової матриці провідностей */
        double G[MAX_NODES][MAX_NODES] = {{0}};
        double RHS[MAX_NODES] = {0};

        for (int b = 0; b < ckt->num_branches; b++) {
            MagBranch *br = &ckt->branches[b];
            int u = br->node_from;
            int v = br->node_to;
            double p = br->permeance;
            double src = p * br->mmf;

            if (u != ckt->ground_node) {
                G[u][u] += p;
                RHS[u] -= src;
                if (v != ckt->ground_node) G[u][v] -= p;
            }
            if (v != ckt->ground_node) {
                G[v][v] += p;
                RHS[v] += src;
                if (u != ckt->ground_node) G[v][u] -= p;
            }
        }

        double V_sol[MAX_NODES] = {0};
        if (!solve_linear_system(G, RHS, V_sol, n_eq)) {
            fprintf(stderr, "Помилка: вироджена матриця магнітної сітки!\n");
            return false;
        }

        for (int i = 0; i < n_eq; i++) node_potentials[i] = V_sol[i];
        node_potentials[ckt->ground_node] = 0.0;

        /* Оновлення полів і перевірка збіжності */
        double max_err = 0.0;
        for (int b = 0; b < ckt->num_branches; b++) {
            MagBranch *br = &ckt->branches[b];
            double v_from = node_potentials[br->node_from];
            double v_to = node_potentials[br->node_to];
            double drop = v_from - v_to + br->mmf;
            br->h_field = fabs(drop) / br->length;

            if (br->mat == MAT_FERRITE_N87) {
                double mu_target = calc_brauer_mur(br->h_field, br->mu_r0, br->b_sat);
                double err = fabs(mu_target - br->mu_r) / br->mu_r;
                if (err > max_err) max_err = err;
                br->mu_r = (1.0 - alpha) * br->mu_r + alpha * mu_target;
            }
        }

        if (max_err < tol) {
            /* Фінальний розрахунок потоків та індукцій */
            for (int b = 0; b < ckt->num_branches; b++) {
                MagBranch *br = &ckt->branches[b];
                double v_from = node_potentials[br->node_from];
                double v_to = node_potentials[br->node_to];
                br->flux = br->permeance * (v_from - v_to + br->mmf);
                br->b_field = fabs(br->flux) / br->area;
            }
            return true;
        }
    }
    return false; /* не зійшлося за max_iter */
}

int main(void) {
    MagCircuit ckt;
    ckt.num_nodes = 2; /* 0: Верхнє ярмо, 1: Нижнє ярмо (земля) */
    ckt.ground_node = 1;
    ckt.num_branches = 4;

    /* Гілка 0: Центральний феритовий керн (N=40 витків, I=4.5 А -> MMF=180 А-вит) */
    ckt.branches[0] = (MagBranch){
        .node_from = 0, .node_to = 1, .length = 0.035, .area = 1.78e-4,
        .mmf = 180.0, .mat = MAT_FERRITE_N87, .mu_r0 = 2200.0, .b_sat = 0.39
    };
    /* Гілка 1: Повітряний зазор у центральному керні (0.8 мм) */
    ckt.branches[1] = (MagBranch){
        .node_from = 0, .node_to = 1, .length = 0.0008, .area = 1.78e-4,
        .mmf = 0.0, .mat = MAT_LINEAR_AIR, .mu_r0 = 1.0, .b_sat = 0.0
    };
    /* Гілка 2: Лівий бічний керн + половина ярма (площа перерізу вдвічі менша) */
    ckt.branches[2] = (MagBranch){
        .node_from = 0, .node_to = 1, .length = 0.065, .area = 0.89e-4,
        .mmf = 0.0, .mat = MAT_FERRITE_N87, .mu_r0 = 2200.0, .b_sat = 0.39
    };
    /* Гілка 3: Правий бічний керн + половина ярма */
    ckt.branches[3] = (MagBranch){
        .node_from = 0, .node_to = 1, .length = 0.065, .area = 0.89e-4,
        .mmf = 0.0, .mat = MAT_FERRITE_N87, .mu_r0 = 2200.0, .b_sat = 0.39
    };

    printf("=== Чисельний розрахунок розгалуженого магнітного кола (C) ===\n");
    if (solve_magnetic_circuit(&ckt, 1e-6, 200, 0.35)) {
        printf("Збіжність досягнута успішно.\n\n");
        for (int i = 0; i < ckt.num_branches; i++) {
            MagBranch *br = &ckt.branches[i];
            printf("Гілка %d: Потік = %7.3f мкВб | B = %5.3f Тл | H = %6.1f А/м | mu_r = %6.1f\n",
                   i, br->flux * 1e6, br->b_field, br->h_field, br->mu_r);
        }
        double total_flux_center = fabs(ckt.branches[0].flux);
        double turns = 40.0;
        double current = 4.5;
        double inductance = (turns * total_flux_center) / current;
        printf("\nРезультуюча індуктивність L: %.2f мкГн\n", inductance * 1e6);
        printf("Запас до насичення фериту в центрі: %.1f%%\n", 
               (1.0 - ckt.branches[0].b_field / 0.39) * 100.0);
    } else {
        printf("Розрахунок не зійшовся.\n");
    }
    return 0;
}
