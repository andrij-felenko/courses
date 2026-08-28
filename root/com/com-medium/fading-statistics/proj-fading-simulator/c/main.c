#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для збереження результатів аналізу каналу */
typedef struct {
    double mean_amplitude;
    double mean_power;
    double outage_probability;
    double amount_of_fading;
} ChannelStats;

/* Генератор нормально розподіленого числа N(0, 1) за методом Бокса-Мюллера */
double generate_gaussian(void) {
    double u1 = (double)rand() / (RAND_MAX + 1.0);
    double u2 = (double)rand() / (RAND_MAX + 1.0);
    if (u1 < 1e-12) u1 = 1e-12;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

/* Генератор амплітуди Релея з параметром масштабу sigma */
double sample_rayleigh(double sigma) {
    double i = sigma * generate_gaussian();
    double q = sigma * generate_gaussian();
    return sqrt(i * i + q * q);
}

/* Генератор амплітуди Райса (K - фактор Райса, sigma - розсіяна складова) */
double sample_rician(double K_lin, double sigma) {
    double s = sqrt(2.0 * K_lin * sigma * sigma);
    double i = s + sigma * generate_gaussian();
    double q = sigma * generate_gaussian();
    return sqrt(i * i + q * q);
}

/* Генератор амплітуди Накагамі-m */
double sample_nakagami(double m, double omega) {
    if (fabs(m - 1.0) < 1e-3) {
        return sample_rayleigh(sqrt(omega / 2.0));
    }
    
    int k_count = (int)(2.0 * m + 0.5);
    if (k_count < 1) k_count = 1;
    
    double sum_sq = 0.0;
    double scale = sqrt(omega / (2.0 * m));
    for (int k = 0; k < k_count; k++) {
        double val = scale * generate_gaussian();
        sum_sq += val * val;
    }
    return sqrt(sum_sq);
}

/* Аналіз масиву вибірок амплітуди */
ChannelStats analyze_samples(const double *samples, int count, double threshold) {
    ChannelStats stats;
    double sum_r = 0.0;
    double sum_p = 0.0;
    double sum_p2 = 0.0;
    int outages = 0;

    for (int i = 0; i < count; i++) {
        double r = samples[i];
        double p = r * r;
        sum_r += r;
        sum_p += p;
        sum_p2 += p * p;
        if (r < threshold) {
            outages++;
        }
    }

    stats.mean_amplitude = sum_r / count;
    stats.mean_power = sum_p / count;
    stats.outage_probability = (double)outages / count;
    
    double var_p = (sum_p2 / count) - (stats.mean_power * stats.mean_power);
    stats.amount_of_fading = var_p / (stats.mean_power * stats.mean_power);

    return stats;
}

int main(void) {
    const int N = 100000;
    const double threshold = 0.3;
    
    double *rayleigh_arr = (double*)malloc(N * sizeof(double));
    double *rician_arr   = (double*)malloc(N * sizeof(double));
    double *nakagami_arr = (double*)malloc(N * sizeof(double));

    if (!rayleigh_arr || !rician_arr || !nakagami_arr) {
        printf("Помилка виділення пам'яті!\n");
        return 1;
    }

    printf("=== Статистичний симулятор каналів завмирань (%d вибірок) ===\n\n", N);

    /* Заповнення масивів вибірок */
    for (int n = 0; n < N; n++) {
        rayleigh_arr[n] = sample_rayleigh(0.7071);     /* E[r^2] = 1.0 */
        rician_arr[n]   = sample_rician(3.98, 0.316);  /* K = 6 дБ */
        nakagami_arr[n] = sample_nakagami(0.5, 1.0);   /* m = 0.5 (severe) */
    }

    ChannelStats st_ray = analyze_samples(rayleigh_arr, N, threshold);
    ChannelStats st_ric = analyze_samples(rician_arr, N, threshold);
    ChannelStats st_nak = analyze_samples(nakagami_arr, N, threshold);

    printf("Поріг амплітуди чутливості: R_th = %.2f\n\n", threshold);
    
    printf("%-20s %-12s %-12s %-15s %-12s\n", "Модель каналу", "Середне r", "Середня P", "Outage Prob (%)", "Depth AF");
    printf("-----------------------------------------------------------------------\n");
    printf("%-20s %-12.4f %-12.4f %-15.2f %-12.4f\n", "Релей (m=1, NLOS)", st_ray.mean_amplitude, st_ray.mean_power, st_ray.outage_probability * 100.0, st_ray.amount_of_fading);
    printf("%-20s %-12.4f %-12.4f %-15.2f %-12.4f\n", "Райс (K=6 дБ, LOS)", st_ric.mean_amplitude, st_ric.mean_power, st_ric.outage_probability * 100.0, st_ric.amount_of_fading);
    printf("%-20s %-12.4f %-12.4f %-15.2f %-12.4f\n", "Накагамі (m=0.5)", st_nak.mean_amplitude, st_nak.mean_power, st_nak.outage_probability * 100.0, st_nak.amount_of_fading);

    free(rayleigh_arr);
    free(rician_arr);
    free(nakagami_arr);

    return 0;
}
