#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define NUM_ELECTRONS  50000
#define NUM_STEPS      20000
#define DT             1.0e-16   /* Крок інтегрування: 0.1 фс */
#define TAU            2.5e-14   /* Час релаксації для Cu: 25 фс */
#define E_FIELD        1.0e4     /* Напруженість поля: 10 кВ/м */
#define CONCENTRATION  8.5e28    /* Концентрація електронів Cu: 8.5e28 м^-3 */

#define ELEC_CHARGE    1.602176634e-19 /* Кл */
#define ELEC_MASS      9.1093837015e-31 /* кг */
#define KB             1.380649e-23     /* Дж/К */
#define TEMPERATURE    300.0            /* К */

typedef struct {
    double vx;
    double vy;
    double vz;
} Electron;

/* Генерація рівномірно розподіленого випадкового числа від 0.0 до 1.0 */
static inline double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Генерація компоненти швидкості за нормальним розподілом Гауса (Box-Muller) */
static double rand_gaussian(double sigma) {
    double u1 = rand_uniform();
    double u2 = rand_uniform();
    while (u1 <= 1e-15) {
        u1 = rand_uniform();
    }
    return sigma * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

int main(void) {
    srand((unsigned int)time(NULL));

    double sigma_v = sqrt(KB * TEMPERATURE / ELEC_MASS);
    Electron *electrons = (Electron *)malloc(NUM_ELECTRONS * sizeof(Electron));
    if (!electrons) {
        fprintf(stderr, "Помилка виділення динамічної пам'яті\n");
        return 1;
    }

    /* Ініціалізація ансамблю електронів тепловими швидкостями */
    for (int i = 0; i < NUM_ELECTRONS; ++i) {
        electrons[i].vx = rand_gaussian(sigma_v);
        electrons[i].vy = rand_gaussian(sigma_v);
        electrons[i].vz = rand_gaussian(sigma_v);
    }

    double acc_x = - (ELEC_CHARGE * E_FIELD) / ELEC_MASS;
    double p_coll = 1.0 - exp(-DT / TAU);

    double sum_vx_drift = 0.0;
    int sample_count = 0;

    /* Головний цикл дискретної симуляції за часом */
    for (int step = 0; step < NUM_STEPS; ++step) {
        double step_vx_sum = 0.0;

        for (int i = 0; i < NUM_ELECTRONS; ++i) {
            /* Прискорення зовнішнім електричним полем */
            electrons[i].vx += acc_x * DT;

            /* Перевірка акту статистичного розсіювання */
            if (rand_uniform() < p_coll) {
                electrons[i].vx = rand_gaussian(sigma_v);
                electrons[i].vy = rand_gaussian(sigma_v);
                electrons[i].vz = rand_gaussian(sigma_v);
            }

            step_vx_sum += electrons[i].vx;
        }

        /* Накопичуємо статистику після проходження перехідного процесу (після перших 20% кроків) */
        if (step > NUM_STEPS / 5) {
            sum_vx_drift += (step_vx_sum / NUM_ELECTRONS);
            sample_count++;
        }
    }

    double mean_vd_sim = sum_vx_drift / sample_count;
    double mean_vd_theory = - (ELEC_CHARGE * TAU / ELEC_MASS) * E_FIELD;

    double j_sim = - CONCENTRATION * ELEC_CHARGE * mean_vd_sim;
    double sigma_sim = j_sim / E_FIELD;
    double sigma_theory = (CONCENTRATION * ELEC_CHARGE * ELEC_CHARGE * TAU) / ELEC_MASS;
    double mobility_sim = fabs(mean_vd_sim) / E_FIELD;
    double diff_coeff = (KB * TEMPERATURE / ELEC_MASS) * TAU;

    printf("=== Результати Монте-Карло симуляції моделі Друде ===\n");
    printf("Дрейфова швидкість (симуляція): %12.4e м/с\n", mean_vd_sim);
    printf("Дрейфова швидкість (теорія):    %12.4e м/с\n", mean_vd_theory);
    printf("Густина струму j (симуляція):   %12.4e А/м²\n", j_sim);
    printf("Питома провідність σ (симул.):  %12.4e См/м\n", sigma_sim);
    printf("Питома провідність σ (теорія):  %12.4e См/м\n", sigma_theory);
    printf("Питомий опір ρ (симуляція):     %12.4e Ом·м\n", 1.0 / sigma_sim);
    printf("Рухливість електронів μ:        %12.4e м²/(В·с)\n", mobility_sim);
    printf("Коефіцієнт дифузії D (теорія):  %12.4e м²/с\n", diff_coeff);
    printf("Співвідношення Ейнштейна D/μ:   %12.4e В (теорія kBT/e: %.4e В)\n",
           diff_coeff / mobility_sim, KB * TEMPERATURE / ELEC_CHARGE);

    free(electrons);
    return 0;
}
