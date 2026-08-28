/* rkky_spin_glass.c — Чисельне моделювання спінового скла РККЙ мовою C */
#stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double y;
    int spin; // +1 або -1
} SpinSite;

/* Обчислення безрозмірної осциляційної функції РККЙ F(x) = (x*cos(x) - sin(x)) / x^4 */
double rkky_function(double r, double k_F) {
    double x = 2.0 * k_F * r;
    if (x < 0.05) return 0.0; // Захист від сингулярності самовпливу у точці r=0
    return (x * cos(x) - sin(x)) / (x * x * x * x);
}

/* Розрахунок повної потенціальної енергії системи */
double calculate_total_energy(const SpinSite* sites, const double* J_matrix, int N) {
    double energy = 0.0;
    for (int i = 0; i < N; i++) {
        for (int j = i + 1; j < N; j++) {
            energy -= J_matrix[i * N + j] * sites[i].spin * sites[j].spin;
        }
    }
    return energy;
}

int main(void) {
    const int N = 80;                // Кількість магнітних домішок
    const double L = 50.0;           // Розмір двовимірної комірки (у нанометрах)
    const double k_F = 1.36;         // Хвильовий вектор Фермі міді (1/нм)
    const double J0 = 10.0;          // Масштабний коефіцієнт обміну (меВ)
    const int mc_steps = 3000;       // Кількість кроків Монте-Карло на кожну температуру

    srand((unsigned int)time(NULL));

    SpinSite* sites = (SpinSite*)malloc(N * sizeof(SpinSite));
    double* J_matrix = (double*)malloc(N * N * sizeof(double));

    // 1. Випадкове розміщення магнітних домішок у матриці
    for (int i = 0; i < N; i++) {
        sites[i].x = ((double)rand() / RAND_MAX) * L;
        sites[i].y = ((double)rand() / RAND_MAX) * L;
        sites[i].spin = (rand() % 2 == 0) ? 1 : -1;
    }

    // 2. Заповнення симетричної матриці обмінних інтегралів J_ij
    int afm_bonds = 0;
    int fm_bonds = 0;

    for (int i = 0; i < N; i++) {
        J_matrix[i * N + i] = 0.0;
        for (int j = i + 1; j < N; j++) {
            double dx = sites[i].x - sites[j].x;
            double dy = sites[i].y - sites[j].y;
            double r = sqrt(dx * dx + dy * dy);
            
            double J_val = J0 * rkky_function(r, k_F);
            J_matrix[i * N + j] = J_val;
            J_matrix[j * N + i] = J_val;

            if (J_val < 0) afm_bonds++;
            else if (J_val > 0) fm_bonds++;
        }
    }

    printf("=== Моделювання спінового скла РККЙ (Метод Монте-Карло) ===\n");
    printf("Кількість магнітних домішок: N = %d\n", N);
    printf("Розмір системи: L = %.1f нм, Хвильове число k_F = %.2f 1/нм\n", L, k_F);
    printf("Баланс обмінних зв'язків: FM (J>0) = %d, AFM (J<0) = %d (Частка AFM: %.1f%%)\n\n", 
           fm_bonds, afm_bonds, (double)afm_bonds / (fm_bonds + afm_bonds) * 100.0);

    // 3. Покрокове зниження температури (Температурний скан)
    printf("  Т (K)  |  Енергія E (меВ)  |  Параметр порядку q_EA  |  Стан системи\n");
    printf("-----------------------------------------------------------------------\n");

    for (double T = 15.0; T >= 0.5; T -= 1.0) {
        double beta = 1.0 / (0.08617 * T); // k_B = 0.08617 меВ/K
        double spin_accum[80] = {0.0};
        int sample_count = 0;

        // Монте-Карло релаксація
        for (int step = 0; step < mc_steps; step++) {
            int idx = rand() % N;
            
            // Розрахунок зміни енергії ΔE при перевороті спіна idx
            double dE = 0.0;
            for (int j = 0; j < N; j++) {
                if (idx != j) {
                    dE += 2.0 * J_matrix[idx * N + j] * sites[idx].spin * sites[j].spin;
                }
            }

            // Критерій Метрополіса
            if (dE <= 0.0 || ((double)rand() / RAND_MAX) < exp(-dE * beta)) {
                sites[idx].spin = -sites[idx].spin;
            }

            // Накопичення часової статистики після досягнення рівноваги
            if (step >= mc_steps / 2) {
                for (int i = 0; i < N; i++) {
                    spin_accum[i] += sites[i].spin;
                }
                sample_count++;
            }
        }

        // Обчислення параметра порядку Едвардса — Андерсона q_EA
        double q_ea = 0.0;
        for (int i = 0; i < N; i++) {
            double avg_s = spin_accum[i] / sample_count;
            q_ea += avg_s * avg_s;
        }
        q_ea /= N;

        double current_E = calculate_total_energy(sites, J_matrix, N);
        const char* state_str = (q_ea < 0.15) ? "Парамагнетик" : 
                               (q_ea < 0.50) ? "Перехідна область" : "Спінове скло";

        printf("%6.1f  |  %15.2f  |  %20.4f  |  %s\n", T, current_E, q_ea, state_str);
    }

    free(sites);
    free(J_matrix);
    return 0;
}
