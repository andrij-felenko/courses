/* Simulation of 2D Antiferromagnetic Ising Model using Metropolis Monte Carlo (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define L 40
#define N_SPINS (L * L)
#define MC_SWEEPS 5000
#define THERM_SWEEPS 1000

typedef struct {
    int spins[L][L];
    double J; /* J < 0 for antiferromagnetism */
    double H;
    double T;
} Simulation;

/* Initialize lattice into exact antiferromagnetic ground state (Checkerboard) */
void init_checkerboard(Simulation *sim) {
    for (int i = 0; i < L; i++) {
        for (int j = 0; j < L; j++) {
            if ((i + j) % 2 == 0) {
                sim->spins[i][j] = 1;  /* Sublattice A */
            } else {
                sim->spins[i][j] = -1; /* Sublattice B */
            }
        }
    }
}

/* Generate uniformly distributed random double in range [0, 1) */
double get_random_double() {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Calculate dE for flipping spin at row r, column c */
double calculate_site_energy_change(const Simulation *sim, int r, int c) {
    int s = sim->spins[r][c];
    int top    = sim->spins[(r - 1 + L) % L][c];
    int bottom = sim->spins[(r + 1) % L][c];
    int left   = sim->spins[r][(c - 1 + L) % L];
    int right  = sim->spins[r][(c + 1) % L];
    
    int neighbor_sum = top + bottom + left + right;
    
    /* dE = 2 * s * (J * sum_neighbors + H) */
    return 2.0 * s * (sim->J * neighbor_sum + sim->H);
}

/* Execute one Monte Carlo Sweep (N_SPINS flip attempts) */
void monte_carlo_sweep(Simulation *sim) {
    for (int step = 0; step < N_SPINS; step++) {
        int r = rand() % L;
        int c = rand() % L;
        
        double dE = calculate_site_energy_change(sim, r, c);
        
        if (dE <= 0.0 || get_random_double() < exp(-dE / sim->T)) {
            sim->spins[r][c] = -sim->spins[r][c];
        }
    }
}

/* Compute sublattices and net magnetizations */
void compute_magnetizations(const Simulation *sim, double *m_a, double *m_b, double *m_stag, double *m_net) {
    double sum_a = 0.0;
    double sum_b = 0.0;
    
    for (int i = 0; i < L; i++) {
        for (int j = 0; j < L; j++) {
            if ((i + j) % 2 == 0) {
                sum_a += sim->spins[i][j];
            } else {
                sum_b += sim->spins[i][j];
            }
        }
    }
    
    *m_a = sum_a / (N_SPINS / 2.0);
    *m_b = sum_b / (N_SPINS / 2.0);
    *m_stag = fabs(*m_a - *m_b) / 2.0;
    *m_net = fabs(sum_a + sum_b) / (double)N_SPINS;
}

int main(void) {
    srand((unsigned int)time(NULL));
    Simulation sim;
    sim.J = -1.0; /* Antiferromagnetic exchange coupling */
    sim.H = 0.0;  /* Zero external field */
    
    printf("Temp\tM_A\tM_B\tM_staggered\tM_net\n");
    printf("---------------------------------------------------\n");
    
    for (double T = 0.4; T <= 4.0; T += 0.2) {
        sim.T = T;
        init_checkerboard(&sim);
        
        /* Thermalization phase (erase transient initial memory) */
        for (int s = 0; s < THERM_SWEEPS; s++) {
            monte_carlo_sweep(&sim);
        }
        
        /* Measurement phase */
        double avg_ma = 0.0, avg_mb = 0.0, avg_mstag = 0.0, avg_mnet = 0.0;
        for (int s = 0; s < MC_SWEEPS; s++) {
            monte_carlo_sweep(&sim);
            double ma, mb, mstag, mnet;
            compute_magnetizations(&sim, &ma, &mb, &mstag, &mnet);
            avg_ma += ma;
            avg_mb += mb;
            avg_mstag += mstag;
            avg_mnet += mnet;
        }
        
        avg_ma /= MC_SWEEPS;
        avg_mb /= MC_SWEEPS;
        avg_mstag /= MC_SWEEPS;
        avg_mnet /= MC_SWEEPS;
        
        printf("%.2f\t%.3f\t%.3f\t%.3f\t\t%.3f\n", T, avg_ma, avg_mb, avg_mstag, avg_mnet);
    }
    
    return 0;
}
