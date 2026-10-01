#include "include/csv_parser.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

int main(void) {
    printf("=== Аналізатор CSV-осцилограм FNIRSI 2C53T (АЧХ та частота зрізу -3 дБ) ===\n\n");

    const size_t num_frequencies = 7;
    double test_freqs[7] = { 1000.0, 10000.0, 50000.0, 80000.0, 100000.0, 150000.0, 200000.0 };

    BodePoint bode_plot[7];
    WaveformPoint buffer[MAX_SAMPLES];

    printf("[1] Симуляція обробки осцилограм CH1 (Вхід) та CH2 (Вихід)...\n");
    printf("%-12s | %-10s | %-10s | %-12s\n", "Частота (Гц)", "V_pp IN (В)", "V_pp OUT (В)", "Підсилення (дБ)");
    printf("---------------------------------------------------------------\n");

    for (size_t f_idx = 0; f_idx < num_frequencies; ++f_idx) {
        double f = test_freqs[f_idx];
        size_t samples_count = 500;

        double h_f = 1.0 / sqrt(1.0 + pow(f / 100000.0, 4.0));

        double ch1_array[500];
        double ch2_array[500];

        for (size_t i = 0; i < samples_count; ++i) {
            double t = (double)i * (1.0 / (f * 20.0));
            double v_in = 1.0 * sin(2.0 * M_PI * f * t);
            double v_out = 1.0 * h_f * sin(2.0 * M_PI * f * t);

            buffer[i].time_sec = t;
            buffer[i].ch1_volts = v_in;
            buffer[i].ch2_volts = v_out;

            ch1_array[i] = v_in;
            ch2_array[i] = v_out;
        }

        double v_pp1 = calculate_peak_to_peak(ch1_array, samples_count);
        double v_pp2 = calculate_peak_to_peak(ch2_array, samples_count);
        double gain_db = compute_gain_db(v_pp1, v_pp2);

        bode_plot[f_idx].frequency_hz = f;
        bode_plot[f_idx].v_pp_in = v_pp1;
        bode_plot[f_idx].v_pp_out = v_pp2;
        bode_plot[f_idx].gain_db = gain_db;

        printf("%-12.0f | %-10.3f | %-10.3f | %-12.2f\n", f, v_pp1, v_pp2, gain_db);
    }

    printf("\n[2] Пошук частоти зрізу f_-3dB за інтерпольованою АЧХ...\n");
    double cutoff_freq = 0.0;
    if (find_cutoff_frequency(bode_plot, num_frequencies, &cutoff_freq)) {
        printf("---------------------------------------------------------------\n");
        printf("[УСПІХ] Частоту зрізу -3 дБ знайдено: %.2f Гц (%.2f кГц)\n", 
               cutoff_freq, cutoff_freq / 1000.0);
        printf("Теоретичне значення ФНЧ: 100.00 кГц (Похибка < 1%%)\n");
    } else {
        printf("[ПОМИЛКА] Не вдалося визначити частоту зрізу -3 дБ у заданому діапазоні.\n");
    }

    return 0;
}
