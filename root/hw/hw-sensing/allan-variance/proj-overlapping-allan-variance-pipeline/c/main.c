#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "allan_variance.h"

/* Генерація псевдовипадкового числа з нормальним розподілом (метод Бокса-Мюллера) */
static double rand_normal(double mean, double stddev) {
    double u1 = (double)(rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = (double)(rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * 3.14159265358979323846 * u2);
    return mean + z0 * stddev;
}

int main(void) {
    printf("=== Демонстрація розрахунку дисперсії Аллана (C99 OAVAR / MVAR) ===\n\n");

    const size_t N = 100000;      /* 100 000 відліків */
    const double dt = 0.01;       /* f_s = 100 Hz, dt = 10 ms */

    printf("Генерація синтетичного сигналу гіроскопа (N = %zu відліків, dt = %.3f c)...\n", N, dt);
    double *gyro_data = (double *)malloc(N * sizeof(double));
    if (!gyro_data) {
        fprintf(stderr, "Помилка виділення пам'яті під сигнал!\n");
        return 1;
    }

    /* Моделювання сигналу: Білий шум (ARW) + Випадкове блукання зсуву нуля (RRW) */
    const double white_noise_sigma = 0.1;    /* град/с */
    const double bias_drift_step = 0.0002;   /* крок випадкового блукання */
    double bias = 5.0;                      /* постійний зсув нуля +5 град/с */

    for (size_t i = 0; i < N; ++i) {
        bias += rand_normal(0.0, bias_drift_step);
        gyro_data[i] = bias + rand_normal(0.0, white_noise_sigma);
    }

    /* Логарифмічна сітка точок m */
    const size_t m_taus[] = {
        1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192
    };
    const size_t num_taus = sizeof(m_taus) / sizeof(m_taus[0]);

    AllanResult *results = (AllanResult *)malloc(num_taus * sizeof(AllanResult));
    if (!results) {
        free(gyro_data);
        return 1;
    }

    printf("Запуск потокового обчислення OADEV / MDEV через префіксні суми фази...\n\n");
    if (!allan_analyze_pipeline(gyro_data, N, dt, m_taus, num_taus, results)) {
        fprintf(stderr, "Помилка виконання конвеєра аналізу Аллана!\n");
        free(gyro_data);
        free(results);
        return 1;
    }

    printf("%-10s | %-8s | %-12s | %-12s | %-8s | %-24s\n",
           "tau, c", "m", "OADEV (°/s)", "MDEV (°/s)", "EDF", "95% Довірчий інтервал");
    printf("----------------------------------------------------------------------------------------\n");

    for (size_t i = 0; i < num_taus; ++i) {
        if (results[i].adev > 0.0) {
            printf("%-10.3f | %-8zu | %-12.6f | %-12.6f | %-8.1f | [%.6f ... %.6f]\n",
                   results[i].tau,
                   results[i].m,
                   results[i].adev,
                   results[i].mdev,
                   results[i].edf,
                   results[i].adev_lower,
                   results[i].adev_upper);
        }
    }

    printf("----------------------------------------------------------------------------------------\n");
    printf("Розрахунок завершено успішно без витоків пам'яті.\n");

    free(gyro_data);
    free(results);
    return 0;
}
