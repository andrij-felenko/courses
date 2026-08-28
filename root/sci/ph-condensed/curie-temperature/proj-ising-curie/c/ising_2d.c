/*
 * ising_2d.c — Моделювання 2D моделі Ізінга методом Монте-Карло (C99)
 * Обчислює намагніченість <|M|>, сприйнятливість chi та теплоємність Cp.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define L 32              /* Розмір квадратної ґратки L x L */
#define N (L * L)         /* Загальна кількість спінів */
#define J_EXCHANGE 1.0    /* Константа обмінної взаємодії */

/* Таблиця заздалегідь обчислених ймовірностей Больцмана для прискорення */
static double exp_table[9];

/* Періодичні межові умови */
static inline int pbc(int coord) {
    if (coord < 0) return coord + L;
    if (coord >= L) return coord - L;
    return coord;
}

/* Ініціалізація таблиці експонент для даної температури T */
static void init_boltzmann_table(double temp) {
    /* ΔE може бути +4J або +8J для ΔE > 0 */
    exp_table[4] = exp(-4.0 * J_EXCHANGE / temp);
    exp_table[8] = exp(-8.0 * J_EXCHANGE / temp);
}

/* Ініціалізація спінів у випадковий гарячий стан (T -> inf) */
static void init_spins_random(int spin[L][L]) {
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            spin[r][c] = (rand() % 2 == 0) ? 1 : -1;
        }
    }
}

/* Повна енергія системи */
static double calc_total_energy(const int spin[L][L]) {
    double energy = 0.0;
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            int s = spin[r][c];
            int sum_neighbors = spin[pbc(r + 1)][c] + spin[r][pbc(c + 1)];
            energy -= J_EXCHANGE * s * sum_neighbors;
        }
    }
    return energy;
}

/* Загальна намагніченість ґратки */
static double calc_total_magnetization(const int spin[L][L]) {
    int sum = 0;
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            sum += spin[r][c];
        }
    }
    return (double)sum;
}

/* Один крок Монте-Карло (MCS) — N спроб перевороту */
static void monte_carlo_step(int spin[L][L], double temp) {
    for (int step = 0; step < N; step++) {
        int r = rand() % L;
        int c = rand() % L;
        int s = spin[r][c];
        
        int sum_neighbors = spin[pbc(r - 1)][c] + spin[pbc(r + 1)][c] +
                            spin[r][pbc(c - 1)] + spin[r][pbc(c + 1)];
        int dE = 2 * J_EXCHANGE * s * sum_neighbors;

        if (dE <= 0) {
            spin[r][c] = -s;
        } else {
            double p = exp_table[dE];
            double r_val = (double)rand() / (RAND_MAX + 1.0);
            if (r_val < p) {
                spin[r][c] = -s;
            }
        }
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    int spin[L][L];

    printf("===============================================================\n");
    printf(" 2D Ising Monte Carlo Simulation (C99)\n");
    printf(" Grid: %dx%d (%d spins)\n", L, L, N);
    printf(" Theoretical Curie Temp Tc = %.5f J/kB\n", 2.0 / log(1.0 + sqrt(2.0)));
    printf("===============================================================\n\n");
    printf("  Temp(T) |   <|M|>   |  Chi (Susc)  |   Cp (Heat)  | Notes\n");
    printf("---------------------------------------------------------------\n");

    for (double T = 1.2; T <= 3.41; T += 0.1) {
        init_spins_random(spin);
        init_boltzmann_table(T);

        /* 1. Термалізація (вивід у рівноважний стан) — 3000 MCS */
        for (int mcs = 0; mcs < 3000; mcs++) {
            monte_carlo_step(spin, T);
        }

        /* 2. Збір термодинамічних статистик — 3000 MCS */
        double sum_m = 0.0, sum_m2 = 0.0;
        double sum_e = 0.0, sum_e2 = 0.0;
        int samples = 3000;

        for (int mcs = 0; mcs < samples; mcs++) {
            monte_carlo_step(spin, T);
            
            double m_val = fabs(calc_total_magnetization(spin)) / N;
            double e_val = calc_total_energy(spin) / N;

            sum_m += m_val;
            sum_m2 += m_val * m_val;
            sum_e += e_val;
            sum_e2 += e_val * e_val;
        }

        double avg_m = sum_m / samples;
        double avg_m2 = sum_m2 / samples;
        double avg_e = sum_e / samples;
        double avg_e2 = sum_e2 / samples;

        /* Сприйнятливість chi = N/T * (<M^2> - <|M|>^2) */
        double chi = (N / T) * (avg_m2 - avg_m * avg_m);

        /* Теплоємність Cp = N/T^2 * (<E^2> - <E>^2) */
        double cp = (N / (T * T)) * (avg_e2 - avg_e * avg_e);

        const char* note = (fabs(T - 2.27) < 0.05) ? "<-- Critical Curie Point Tc" : "";
        printf("  %6.2f  |  %8.4f |  %11.4f |  %11.4f | %s\n", T, avg_m, chi, cp, note);
    }

    return 0;
}
