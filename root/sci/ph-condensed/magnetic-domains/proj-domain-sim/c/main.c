#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define GRID_SIZE 40

typedef struct {
    int grid[GRID_SIZE][GRID_SIZE];
    double J_exchange;
    double temperature;
} DomainSimulatorC;

void domain_sim_init(DomainSimulatorC *sim, double J_exchange, double temperature) {
    sim->J_exchange = J_exchange;
    sim->temperature = temperature;
    for (int r = 0; r < GRID_SIZE; r++) {
        for (int c = 0; c < GRID_SIZE; c++) {
            sim->grid[r][c] = ((double)rand() / RAND_MAX > 0.5) ? 1 : -1;
        }
    }
}

void domain_sim_step(DomainSimulatorC *sim, double external_h) {
    int n = GRID_SIZE;
    int total_trials = n * n;

    for (int k = 0; k < total_trials; k++) {
        int r = rand() % n;
        int c = rand() % n;
        int spin = sim->grid[r][c];

        int top = sim->grid[(r - 1 + n) % n][c];
        int bottom = sim->grid[(r + 1) % n][c];
        int left = sim->grid[r][(c - 1 + n) % n];
        int right = sim->grid[r][(c + 1) % n];
        int neighbors_sum = top + bottom + left + right;

        double delta_e = 2.0 * spin * (sim->J_exchange * neighbors_sum + external_h);

        if (delta_e <= 0.0 || ((double)rand() / RAND_MAX) < exp(-delta_e / sim->temperature)) {
            sim->grid[r][c] = -spin;
        }
    }
}

double domain_sim_magnetization(const DomainSimulatorC *sim) {
    int sum = 0;
    for (int r = 0; r < GRID_SIZE; r++) {
        for (int c = 0; c < GRID_SIZE; c++) {
            sum += sim->grid[r][c];
        }
    }
    return (double)sum / (GRID_SIZE * GRID_SIZE);
}

void domain_sim_print(const DomainSimulatorC *sim) {
    printf("=== C DOMAIN MAP ===\n");
    for (int r = 0; r < GRID_SIZE; r++) {
        for (int c = 0; c < GRID_SIZE; c++) {
            putchar(sim->grid[r][c] > 0 ? '#' : '.');
        }
        putchar('\n');
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    DomainSimulatorC sim;
    domain_sim_init(&sim, 1.0, 1.3);

    printf("C Simulator: M_init = %.3f\n", domain_sim_magnetization(&sim));

    for (int step = 0; step < 120; step++) {
        domain_sim_step(&sim, 0.0);
    }

    printf("C Simulator: M_final = %.3f\n", domain_sim_magnetization(&sim));
    domain_sim_print(&sim);
    return 0;
}
