/* Моделювання дробового шуму та фактора Фано на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define PI 3.14159265358979323846
#define ELECTRON_CHARGE 1.602176634e-19

typedef struct {
    double fano_factor;
    double mean_current;
    double psd_measured;
    double psd_theoretical;
} noise_stats_t;

/* Генерація рівномірно розподіленого випадкового числа [0, 1) */
static double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Генерація інтервалу часу за пуассонівським або кулонівським сценарієм */
static double generate_interval(double mean_rate, double fano) {
    if (fano >= 0.99 && fano <= 1.01) {
        /* Класичний Пуассонівський процес: експоненціальний розподіл */
        double u = rand_uniform();
        if (u < 1e-12) u = 1e-12;
        return -log(u) / mean_rate;
    } else if (fano < 1.0) {
        /* Субпуассонівський процес: зменшена дисперсія інтервалів (Erlang / Gamma) */
        int k = (int)(1.0 / fano + 0.5);
        if (k < 1) k = 1;
        double sum = 0.0;
        for (int i = 0; i < k; i++) {
            double u = rand_uniform();
            if (u < 1e-12) u = 1e-12;
            sum += -log(u);
        }
        return (sum / k) / mean_rate;
    } else {
        /* Суперпуассонівський процес: кластеризація (суміш двох швидкостей) */
        double p_burst = 0.2;
        double rate_factor = (rand_uniform() < p_burst) ? (1.0 / (fano * 1.5)) : 1.0;
        double u = rand_uniform();
        if (u < 1e-12) u = 1e-12;
        return -log(u) / (mean_rate * rate_factor);
    }
}

/* Симуляція та обчислення спектральної густини */
noise_stats_t simulate_shot_noise(double target_fano, double rate, double dt, int num_samples) {
    noise_stats_t stats;
    stats.fano_factor = target_fano;

    double *current = (double*)malloc(num_samples * sizeof(double));
    if (!current) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < num_samples; i++) {
        current[i] = 0.0;
    }

    double t = 0.0;
    double t_max = dt * num_samples;
    long long total_electrons = 0;

    /* Монте-Карло генерація вильотів електронів */
    while (t < t_max) {
        double interval = generate_interval(rate, target_fano);
        t += interval;
        if (t < t_max) {
            int idx = (int)(t / dt);
            if (idx >= 0 && idx < num_samples) {
                current[idx] += ELECTRON_CHARGE / dt;
                total_electrons++;
            }
        }
    }

    /* Обчислення середнього струму та дисперсії */
    double sum_i = 0.0;
    for (int i = 0; i < num_samples; i++) {
        sum_i += current[i];
    }
    stats.mean_current = sum_i / num_samples;

    double var_i = 0.0;
    for (int i = 0; i < num_samples; i++) {
        double diff = current[i] - stats.mean_current;
        var_i += diff * diff;
    }
    var_i /= num_samples;

    /* Спектральна густина потужності S_I = 2 * Var(I) * dt */
    stats.psd_measured = 2.0 * var_i * dt;
    stats.psd_theoretical = 2.0 * ELECTRON_CHARGE * stats.mean_current * target_fano;

    free(current);
    return stats;
}

int main(void) {
    srand((unsigned int)time(NULL));

    double rate = 1e9;         /* 10^9 електронів за секунду */
    double dt = 1e-11;         /* Крок дискретизації 10 пс */
    int samples = 100000;      /* 100 000 відліків */

    printf("=== МОДЕЛЮВАННЯ ДРОБОВОГО ШУМУ ТА ФАКТОРА ФАНО ===\n");
    printf("Частота емісії: %.1e е⁻/с, крок dt: %.1e с\n\n", rate, dt);

    double fano_targets[] = {0.5, 1.0, 2.0};
    const char *names[] = {"Субпуассонівський (F=0.5)", "Пуассонівський (F=1.0)", "Суперпуассонівський (F=2.0)"};

    for (int i = 0; i < 3; i++) {
        noise_stats_t res = simulate_shot_noise(fano_targets[i], rate, dt, samples);
        printf("Режим: %s\n", names[i]);
        printf("  Середній струм ⟨I⟩:      %.4e А\n", res.mean_current);
        printf("  Виміряна PSD S_I:        %.4e А²/Гц\n", res.psd_measured);
        printf("  Теоретична PSD (2qI·F):  %.4e А²/Гц\n", res.psd_theoretical);
        printf("  Відношення S_I / 2qI:    %.3f\n\n", res.psd_measured / (2.0 * ELECTRON_CHARGE * res.mean_current));
    }

    return 0;
}
