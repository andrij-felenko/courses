#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Обчислення математичної потужності сигналу
static double compute_power(const double *buf, size_t len) {
    double p = 0.0;
    for (size_t i = 0; i < len; ++i) {
        p += buf[i] * buf[i];
    }
    return p / (double)len;
}

// Обчислення відношення сигнал/шум (SNR) у децибелах відносно оригинала
static double compute_snr(const double *orig, const double *curr, size_t len) {
    double p_sig = 0.0;
    double p_noise = 0.0;

    for (size_t i = 0; i < len; ++i) {
        p_sig += orig[i] * orig[i];
        double diff = curr[i] - orig[i];
        p_noise += diff * diff;
    }

    // Захист від ділення на нуль при абсолютній точності
    if (p_noise < 1e-15) {
        return 999.0;
    }

    return 10.0 * log10(p_sig / p_noise);
}

// Переквантування з вирівняною сіткою (ідемпотентна операція)
static void quantize_aligned(double *buf, size_t len, double step) {
    for (size_t i = 0; i < len; ++i) {
        buf[i] = round(buf[i] / step) * step;
    }
}

// Переквантування зі зсувом сітки (симуляція незбігу базисів)
static void quantize_misaligned(double *buf, size_t len, double step, double phase_shift) {
    for (size_t i = 0; i < len; ++i) {
        double val = buf[i] * (1.0 + phase_shift);
        val = round(val / step) * step;
        buf[i] = val / (1.0 + phase_shift);
    }
}

int main(void) {
    const size_t N_SAMPLES = 4000;
    const int GENERATIONS = 10;
    const double STEP = 0.05;         // Крок квантування
    const double EPS = 0.002;          // Дрейф сітки (0.2%)

    double *orig = (double *)malloc(N_SAMPLES * sizeof(double));
    double *aligned = (double *)malloc(N_SAMPLES * sizeof(double));
    double *misaligned = (double *)malloc(N_SAMPLES * sizeof(double));

    if (!orig || !aligned || !misaligned) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(orig); free(aligned); free(misaligned);
        return 1;
    }

    // Генерація еталонної синусоїди
    for (size_t i = 0; i < N_SAMPLES; ++i) {
        double t = (double)i / (double)N_SAMPLES;
        orig[i] = sin(2.0 * M_PI * 5.0 * t);
        aligned[i] = orig[i];
        misaligned[i] = orig[i];
    }

    printf("Покоління | SNR Aligned (дБ) | SNR Misaligned (дБ)\n");
    printf("----------+-------------------+--------------------\n");

    for (int gen = 1; gen <= GENERATIONS; ++gen) {
        quantize_aligned(aligned, N_SAMPLES, STEP);
        quantize_misaligned(misaligned, N_SAMPLES, STEP, EPS);

        double snr_a = compute_snr(orig, aligned, N_SAMPLES);
        double snr_m = compute_snr(orig, misaligned, N_SAMPLES);

        printf("   %2d     |     %7.2f       |      %7.2f\n", gen, snr_a, snr_m);
    }

    free(orig);
    free(aligned);
    free(misaligned);
    return 0;
}
