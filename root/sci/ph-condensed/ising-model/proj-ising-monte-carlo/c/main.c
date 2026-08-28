#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define L 64
#define N (L * L)

/* Оптимізована структура симуляції з таблицею експонент */
typedef struct {
    int spins[L][L];
    double exp_table[5]; /* Lookup table для exp(-beta * dE) */
    double J;
    double T;
    double beta;
    long long total_energy;
    long long total_magnetization;
} IsingSim;

/* Таблиця для шквал-індексування періодичних межевих умов (тор) */
static int p_next[L];
static int p_prev[L];

void ising_init(IsingSim *sim, double J, double T) {
    sim->J = J;
    sim->T = T;
    sim->beta = 1.0 / T;
    sim->total_energy = 0;
    sim->total_magnetization = 0;

    /* Ініціалізація граничних умов */
    for (int i = 0; i < L; i++) {
        p_next[i] = (i + 1) % L;
        p_prev[i] = (i - 1 + L) % L;
    }

    /* Таблиця експонент для dE = -8J, -4J, 0, 4J, 8J */
    /* Індекси таблиці: (dE / 4J) + 2 */
    for (int k = -2; k <= 2; k++) {
        double dE = 4.0 * J * k;
        sim->exp_table[k + 2] = (dE <= 0) ? 1.0 : exp(-sim->beta * dE);
    }

    /* Початковий гарячий/випадковий стан спінів */
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            sim->spins[r][c] = (rand() % 2 == 0) ? 1 : -1;
            sim->total_magnetization += sim->spins[r][c];
        }
    }

    /* Початковий розрахунок повної енергії */
    long long E = 0;
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            int s = sim->spins[r][c];
            int sum_nn = sim->spins[p_next[r]][c] + sim->spins[r][p_next[c]];
            E -= J * s * sum_nn;
        }
    }
    sim->total_energy = E;
}

/* Один крок Метрополіса (спроба перевороту одного спіна) */
void ising_metropolis_step(IsingSim *sim) {
    int r = rand() % L;
    int c = rand() % L;
    int s = sim->spins[r][c];

    int sum_neighbors = sim->spins[p_next[r]][c] + sim->spins[p_prev[r]][c] +
                        sim->spins[r][p_next[c]] + sim->spins[r][p_prev[c]];

    int dE = 2 * sim->J * s * sum_neighbors;

    /* Прийняття за таблицею Метрополіса */
    int lookup_idx = (dE / (2 * (int)sim->J)) / 2 + 2;
    double prob = sim->exp_table[lookup_idx];

    double r_val = (double)rand() / RAND_MAX;
    if (r_val < prob) {
        sim->spins[r][c] = -s;
        sim->total_energy += dE;
        sim->total_magnetization += (-2 * s);
    }
}

/* Один пасс (Monte Carlo Sweep) = N спроб Метрополіса */
void ising_sweep(IsingSim *sim) {
    for (int i = 0; i < N; i++) {
        ising_metropolis_step(sim);
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    IsingSim sim;

    double T_crit = 2.269;
    ising_init(&sim, 1.0, T_crit);

    /* Прогрів (Thermalization burn-in) */
    for (int i = 0; i < 10000; i++) {
        ising_sweep(&sim);
    }

    /* Накопичення статистики */
    double sum_m = 0.0;
    double sum_m2 = 0.0;
    int num_samples = 5000;

    for (int s = 0; s < num_samples; s++) {
        ising_sweep(&sim);
        double m_abs = fabs((double)sim.total_magnetization / N);
        sum_m += m_abs;
        sum_m2 += m_abs * m_abs;
    }

    double avg_m = sum_m / num_samples;
    double avg_m2 = sum_m2 / num_samples;
    double chi = (avg_m2 - avg_m * avg_m) * N / sim.T;

    printf("2D Ising Model (L=%d, T=%.3f)\n", L, sim.T);
    printf("Magnetization <|m|>: %.4f\n", avg_m);
    printf("Susceptibility chi:  %.4f\n", chi);

    return 0;
}
