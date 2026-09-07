#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "iq_demodulator.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

int main(void) {
    const double sample_rate = 100000.0; /* 100 кГц дискретизація */
    const double signal_freq = 1000.0;   /* 1 кГц тестова частота */
    const size_t num_periods = 10;       /* 10 періодів накопичення */
    const size_t total_samples = (size_t)(sample_rate / signal_freq) * num_periods;

    /* Еталонний досліджуваний двополюсник: послідовне коло R = 100 Ом, C = 1 мкФ */
    const double true_r = 100.0;
    const double true_c = 1.0e-6;
    const double omega = 2.0 * M_PI * signal_freq;
    const double true_x = -1.0 / (omega * true_c); /* ≈ -159.155 Ом */

    printf("=== Цифровий демодулятор комплексного імпедансу (C99) ===\n");
    printf("Частота збудження:  %.2f Гц\n", signal_freq);
    printf("Частота АЦП:        %.2f кГц\n", sample_rate / 1000.0);
    printf("Очікуваний R:       %.3f Ом\n", true_r);
    printf("Очікуваний X_c:     %.3f Ом\n\n", true_x);

    iq_demodulator_t demod;
    if (!iq_demodulator_init(&demod, sample_rate, signal_freq)) {
        fprintf(stderr, "Помилка ініціалізації демодулятора!\n");
        return 1;
    }

    /* Генерація синтетичних відліків АЦП із додаванням шуму та 3-ї гармоніки */
    double v_amp = 1.0; /* Амплітуда напруги 1.0 В */
    double z_mod = sqrt(true_r * true_r + true_x * true_x);
    double i_amp = v_amp / z_mod;
    double phase_shift = atan2(true_x, true_r); /* Фазовий зсув струму відносно напруги */

    for (size_t n = 0; n < total_samples; ++n) {
        double t = (double)n / sample_rate;
        
        /* Сигнал напруги з невеликим шумом і третьою гармонікою */
        double noise_v = ((double)rand() / (double)RAND_MAX - 0.5) * 0.02;
        double harmonic3_v = 0.05 * sin(3.0 * omega * t);
        double v_sample = v_amp * sin(omega * t) + harmonic3_v + noise_v;

        /* Сигнал струму: зсув по фазі (-phase_shift через I = V / Z) */
        double noise_i = ((double)rand() / (double)RAND_MAX - 0.5) * (0.02 * i_amp);
        double i_sample = i_amp * sin(omega * t - phase_shift) + noise_i;

        iq_demodulator_feed(&demod, v_sample, i_sample);
    }

    impedance_result_t result;
    if (iq_demodulator_calculate(&demod, &result)) {
        printf("--- Результати IQ-демодуляції ---\n");
        printf("Активний опір (R):       %8.3f Ом  (похибка: %+.2f%%)\n", 
               result.r_real, ((result.r_real - true_r) / true_r) * 100.0);
        printf("Реактивний опір (X):     %8.3f Ом  (похибка: %+.2f%%)\n", 
               result.x_imag, ((result.x_imag - true_x) / true_x) * 100.0);
        printf("Модуль імпедансу |Z|:    %8.3f Ом\n", result.z_magnitude);
        printf("Фазовий кут:             %8.2f град\n", result.phase_deg);
        printf("Тангенс кута втрат (D):  %8.4f\n", result.dissipation);
        printf("Добротність (Q):         %8.4f\n", result.quality_fac);
        
        /* Розрахунок відновленої ємності */
        if (result.x_imag < 0.0) {
            double calculated_c = -1.0 / (omega * result.x_imag);
            printf("Обчислена ємність C:     %8.3f мкФ (еталон: %.3f мкФ)\n", 
                   calculated_c * 1.0e6, true_c * 1.0e6);
        }
    } else {
        printf("Помилка: не вдалося розрахувати імпеданс (струм занадто малий).\n");
    }

    return 0;
}
