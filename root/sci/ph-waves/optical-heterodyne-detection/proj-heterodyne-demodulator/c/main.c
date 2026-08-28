#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double sample_rate;    // Частота дискретизації АЦП (Гц)
    double f_if;           // Проміжна частота (Гц)
    double p_signal;       // Потужність оптичного сигналу (Вт)
    double p_lo;           // Потужність оптичного гетеродина (Вт)
    double responsivity;   // Чутливість фотодіода (А/Вт)
    size_t num_samples;    // Загальна кількість відліків
} heterodyne_config_t;

// Генератор нормального білого шуму (метод Бокса-Мюллера)
static double generate_gaussian_noise(double std_dev) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-12) u1 = 1e-12;
    return std_dev * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

// Симуляція гетеродинного детектування та IQ-демодуляції
void run_heterodyne_simulation(const heterodyne_config_t* cfg) {
    double dt = 1.0 / cfg->sample_rate;
    double i_lo = cfg->responsivity * cfg->p_lo;
    
    // Дробовий шум гетеродина: std_dev = sqrt(2 * e * I_lo * B_sample)
    double q_elem = 1.602176634e-19;
    double shot_noise_std = sqrt(2.0 * q_elem * i_lo * (cfg->sample_rate / 2.0));

    double* i_out = (double*)malloc(cfg->num_samples * sizeof(double));
    double* q_out = (double*)malloc(cfg->num_samples * sizeof(double));
    double* phase_recovered = (double*)malloc(cfg->num_samples * sizeof(double));

    if (!i_out || !q_out || !phase_recovered) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        free(i_out); free(q_out); free(phase_recovered);
        return;
    }

    int filter_window = (int)(cfg->sample_rate / (cfg->f_if * 2.0));
    if (filter_window < 1) filter_window = 1;

    double peak_beat_current = 2.0 * cfg->responsivity * sqrt(cfg->p_signal * cfg->p_lo);

    printf("=== СИМУЛЯЦІЯ ОПТИЧНОГО ГЕТЕРОДИНА (C) ===\n");
    printf("Потужність сигналу P_s: %.2e Вт\n", cfg->p_signal);
    printf("Потужність гетеродина P_LO: %.2e Вт\n", cfg->p_lo);
    printf("Піковий струм биття: %.3f мкА\n", peak_beat_current * 1e6);
    printf("СКВ дробового шуму: %.3f мкА\n\n", shot_noise_std * 1e6);

    for (size_t k = 0; k < cfg->num_samples; k++) {
        double t = k * dt;
        // Задаємо тестову фазову модуляцію BPSK (зміна фази 0 або PI/2)
        double phase_target = (t > (cfg->num_samples * dt / 2.0)) ? M_PI / 2.0 : 0.0;

        // Балансний фотострум биття + дробовий шум
        double beat_signal = peak_beat_current * cos(2.0 * M_PI * cfg->f_if * t + phase_target);
        double noise = generate_gaussian_noise(shot_noise_std);
        double i_bal = beat_signal + noise;

        // Множення на квадратурні гетеродинні носії
        double raw_i = i_bal * cos(2.0 * M_PI * cfg->f_if * t);
        double raw_q = i_bal * (-sin(2.0 * M_PI * cfg->f_if * t));

        i_out[k] = raw_i;
        q_out[k] = raw_q;
    }

    // Низькочастотна фільтрація (ковзне усереднення) та відновлення фази
    for (size_t k = 0; k < cfg->num_samples; k++) {
        double sum_i = 0.0, sum_q = 0.0;
        int count = 0;

        for (int w = -filter_window; w <= filter_window; w++) {
            int idx = (int)k + w;
            if (idx >= 0 && idx < (int)cfg->num_samples) {
                sum_i += i_out[idx];
                sum_q += q_out[idx];
                count++;
            }
        }

        double filtered_i = sum_i / count;
        double filtered_q = sum_q / count;
        phase_recovered[k] = atan2(filtered_q, filtered_i);
    }

    // Виведення контрольних точок
    printf("Час (мкс) | Відновлена фаза (рад) | Цільова фаза\n");
    printf("-----------------------------------------------\n");
    size_t step = cfg->num_samples / 5;
    for (size_t k = step / 2; k < cfg->num_samples; k += step) {
        double t_us = (k * dt) * 1e6;
        double target = (k * dt > (cfg->num_samples * dt / 2.0)) ? M_PI / 2.0 : 0.0;
        printf("%9.2f | %21.4f | %12.4f\n", t_us, phase_recovered[k], target);
    }

    free(i_out);
    free(q_out);
    free(phase_recovered);
}

int main(void) {
    heterodyne_config_t cfg = {
        .sample_rate = 1.0e9,     // 1 ГВибірок/с
        .f_if = 100.0e6,          // 100 МГц проміжна частота
        .p_signal = 1.0e-9,       // 1 нВт слабкий сигнал
        .p_lo = 1.0e-3,           // 1 мВт потужний гетеродин
        .responsivity = 0.85,     // 0.85 А/Вт при 1550 нм
        .num_samples = 2000
    };

    run_heterodyne_simulation(&cfg);
    return 0;
}
