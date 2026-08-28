#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <time.h>

#define NUM_SUBCARRIERS 64
#define PI 3.14159265358979323846

/* Обчислення Дискретного Перетворення Фур'є (DFT) */
void compute_dft(const double complex *in, double complex *out, int n) {
    for (int k = 0; k < n; k++) {
        out[k] = 0.0 + 0.0 * I;
        for (int m = 0; m < n; m++) {
            double angle = -2.0 * PI * k * m / n;
            out[k] += in[m] * (cos(angle) + I * sin(angle));
        }
    }
}

/* Генерація стандартного гаусового шуму (перетворення Бокса-Мюллера) */
double generate_gaussian_noise(void) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-10) u1 = 1e-10;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * PI * u2);
}

int main(void) {
    srand((unsigned int)time(NULL));

    /* 1. Імпульсна характеристика багатопроменевого каналу h[n] з глибоким нулем */
    double complex h_time[NUM_SUBCARRIERS] = {0};
    h_time[0] = 0.8 + 0.0 * I;  /* Прямий промінь */
    h_time[1] = 0.6 + 0.0 * I;  /* Перевідбитий промінь (створює заваду) */

    /* Частотна характеристика каналу H[k] */
    double complex H_freq[NUM_SUBCARRIERS];
    compute_dft(h_time, H_freq, NUM_SUBCARRIERS);

    /* 2. Генерація корисних BPSK/QAM символів s[k] з нормованою потужністю σ_s² = 1 */
    double complex s_symbols[NUM_SUBCARRIERS];
    for (int k = 0; k < NUM_SUBCARRIERS; k++) {
        double val_i = (rand() % 2 == 0) ? 1.0 : -1.0;
        double val_q = (rand() % 2 == 0) ? 1.0 : -1.0;
        s_symbols[k] = (val_i + I * val_q) / sqrt(2.0);
    }

    /* Випробування при низькому SNR (10 дБ) та високому SNR (30 дБ) */
    double snr_db_list[] = {10.0, 30.0};
    int num_tests = sizeof(snr_db_list) / sizeof(snr_db_list[0]);

    printf("=== Симуляція вирівнювання Zero-Forcing та MMSE ===\n\n");

    for (int test = 0; test < num_tests; test++) {
        double snr_db = snr_db_list[test];
        double snr_linear = pow(10.0, snr_db / 10.0);
        double sigma_w2 = 1.0 / snr_linear; /* σ_w² = σ_s² / SNR */
        double noise_std = sqrt(sigma_w2 / 2.0);

        double complex y_received[NUM_SUBCARRIERS];
        double complex s_zf[NUM_SUBCARRIERS];
        double complex s_mmse[NUM_SUBCARRIERS];

        double mse_zf = 0.0;
        double mse_mmse = 0.0;

        /* 3. Моделювання каналу, додавання шуму та вирівнювання */
        for (int k = 0; k < NUM_SUBCARRIERS; k++) {
            /* Прийнятий сигнал: Y[k] = H[k] * S[k] + W[k] */
            double noise_i = generate_gaussian_noise() * noise_std;
            double noise_q = generate_gaussian_noise() * noise_std;
            double complex noise = noise_i + I * noise_q;

            y_received[k] = H_freq[k] * s_symbols[k] + noise;

            /* Zero-Forcing: W_zf[k] = 1 / H[k] */
            double complex w_zf_k = 1.0 / H_freq[k];
            s_zf[k] = y_received[k] * w_zf_k;

            /* MMSE: W_mmse[k] = H*[k] / (|H[k]|² + 1/SNR) */
            double h_abs2 = cabs(H_freq[k]) * cabs(H_freq[k]);
            double complex w_mmse_k = conj(H_freq[k]) / (h_abs2 + sigma_w2);
            s_mmse[k] = y_received[k] * w_mmse_k;

            /* Обчислення квадратичної помилки */
            double diff_zf = cabs(s_zf[k] - s_symbols[k]);
            double diff_mmse = cabs(s_mmse[k] - s_symbols[k]);

            mse_zf += diff_zf * diff_zf;
            mse_mmse += diff_mmse * diff_mmse;
        }

        mse_zf /= NUM_SUBCARRIERS;
        mse_mmse /= NUM_SUBCARRIERS;

        printf("SNR = %.1f dB (1/SNR = %.4f):\n", snr_db, sigma_w2);
        printf("  Zero-Forcing MSE : %.6f\n", mse_zf);
        printf("  MMSE MSE         : %.6f\n", mse_mmse);
        printf("  Виграш MMSE     : %.2f рази нижча помилка\n\n", mse_zf / mse_mmse);
    }

    return 0;
}
