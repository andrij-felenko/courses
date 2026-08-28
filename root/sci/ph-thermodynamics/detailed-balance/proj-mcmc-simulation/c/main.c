#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define NUM_STATES 8
#define NUM_STEPS 10000000

// Профіль енергетичних рівнів (двоямний потенціал)
static const double ENERGY[NUM_STATES] = {4.0, 1.0, 0.0, 2.5, 3.0, 0.5, 1.5, 5.0};

typedef struct {
    double counts[NUM_STATES][NUM_STATES];
    double visits[NUM_STATES];
    double prob[NUM_STATES];
} mcmc_stats_t;

// Генератор випадкових чисел [0, 1)
static inline double rand_double(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

// Запуск симуляції Метрополіса
void run_metropolis(double temp, mcmc_stats_t *stats) {
    int current_state = 0;

    // Скидання лічильників
    for (int i = 0; i < NUM_STATES; i++) {
        stats->visits[i] = 0.0;
        for (int j = 0; j < NUM_STATES; j++) {
            stats->counts[i][j] = 0.0;
        }
    }

    for (long step = 0; step < NUM_STEPS; step++) {
        stats->visits[current_state] += 1.0;

        // Пропозиція переходу до сусіднього стану (з періодичними межами)
        int step_dir = (rand_double() < 0.5) ? -1 : 1;
        int next_candidate = (current_state + step_dir + NUM_STATES) % NUM_STATES;

        double delta_e = ENERGY[next_candidate] - ENERGY[current_state];
        double accept_prob = (delta_e <= 0.0) ? 1.0 : exp(-delta_e / temp);

        if (rand_double() < accept_prob) {
            stats->counts[current_state][next_candidate] += 1.0;
            current_state = next_candidate;
        } else {
            stats->counts[current_state][current_state] += 1.0;
        }
    }

    // Обчислення стаціонарних ймовірностей P(i)
    for (int i = 0; i < NUM_STATES; i++) {
        stats->prob[i] = stats->visits[i] / (double)NUM_STEPS;
    }
}

// Перевірка детального балансу P(i)*W(i->j) == P(j)*W(j->i)
void verify_detailed_balance(const mcmc_stats_t *stats, double temp) {
    double max_imbalance = 0.0;

    printf("\n=== Аудит детального балансу C (T = %.2f) ===\n", temp);
    printf("Стан i -> j | P(i)*W(i->j) | P(j)*W(j->i) | Дисбаланс |J_ij|\n");
    printf("-----------------------------------------------------------\n");

    for (int i = 0; i < NUM_STATES; i++) {
        for (int j = i + 1; j < NUM_STATES; j++) {
            if (stats->visits[i] == 0 || stats->visits[j] == 0) continue;

            double w_ij = stats->counts[i][j] / stats->visits[i];
            double w_ji = stats->counts[j][i] / stats->visits[j];

            double flux_forward = stats->prob[i] * w_ij;
            double flux_backward = stats->prob[j] * w_ji;
            double imbalance = fabs(flux_forward - flux_backward);

            if (imbalance > max_imbalance) {
                max_imbalance = imbalance;
            }

            if (w_ij > 0.0 || w_ji > 0.0) {
                printf("  %d -> %d    |  %.6f  |  %.6f  |  %.8f\n",
                       i, j, flux_forward, flux_backward, imbalance);
            }
        }
    }

    printf("-----------------------------------------------------------\n");
    printf("Максимальний потік дисбалансу: %.8f\n", max_imbalance);
    if (max_imbalance < 1e-3) {
        printf("ВИСНОВОК: Принцип детального балансу виконується строго!\n");
    }
}

int main(void) {
    srand(42);
    mcmc_stats_t stats;
    double temperature = 1.5;

    run_metropolis(temperature, &stats);
    verify_detailed_balance(&stats, temperature);

    return 0;
}
