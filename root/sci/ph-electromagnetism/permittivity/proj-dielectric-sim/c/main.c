#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define C_SPEED 299792458.0 /* Швидкість світла у вакуумі, м/с */

/* Структура для зберігання результатів обчислення в одній частотній точці */
typedef struct {
    double freq_hz;
    double omega;
    double eps_real;
    double eps_imag;
    double tan_delta;
    double alpha_atten; /* Коефіцієнт згасання, 1/м */
} DielectricPoint;

/* Симуляція спектра релаксації Дебая з логарифмічним кроком за частотою */
int simulate_debye(double eps_s, double eps_inf, double tau,
                   double f_min, double f_max, int num_points,
                   DielectricPoint *out_pts) {
    if (!out_pts || num_points <= 1 || f_min <= 0.0 || f_max <= f_min) {
        return -1;
    }

    double log_f_min = log10(f_min);
    double log_f_max = log10(f_max);
    double step = (log_f_max - log_f_min) / (num_points - 1);

    for (int i = 0; i < num_points; i++) {
        double f = pow(10.0, log_f_min + i * step);
        double omega = 2.0 * M_PI * f;
        double w_tau = omega * tau;
        double denom = 1.0 + w_tau * w_tau;

        double e_prime = eps_inf + (eps_s - eps_inf) / denom;
        double e_double_prime = (eps_s - eps_inf) * w_tau / denom;
        double tan_d = e_double_prime / e_prime;

        /* Розрахунок коефіцієнта згасання електромагнітної хвилі */
        double term = sqrt(1.0 + tan_d * tan_d);
        double alpha = (omega / C_SPEED) * sqrt((e_prime / 2.0) * (term - 1.0));

        out_pts[i].freq_hz = f;
        out_pts[i].omega = omega;
        out_pts[i].eps_real = e_prime;
        out_pts[i].eps_imag = e_double_prime;
        out_pts[i].tan_delta = tan_d;
        out_pts[i].alpha_atten = alpha;
    }

    return 0;
}

int main(void) {
    /* Симуляція спектра чистої води при 20°C: eps_s = 80.1, eps_inf = 4.9, tau = 9.36 пс */
    double eps_s = 80.1;
    double eps_inf = 4.9;
    double tau = 9.36e-12; 
    int N = 7;

    DielectricPoint *pts = (DielectricPoint *)malloc(N * sizeof(DielectricPoint));
    if (!pts) return 1;

    if (simulate_debye(eps_s, eps_inf, tau, 1e8, 1e11, N, pts) == 0) {
        printf(" Частота (Гц)   |   ε' (накоп)  |   ε'' (втрати) |  tan(δ)   |  α (1/м)\n");
        printf("-----------------------------------------------------------------------\n");
        for (int i = 0; i < N; i++) {
            printf("  %10.3e  |  %11.4f  |  %12.4f  |  %7.4f  |  %9.2f\n",
                   pts[i].freq_hz, pts[i].eps_real, pts[i].eps_imag,
                   pts[i].tan_delta, pts[i].alpha_atten);
        }
    }

    free(pts);
    return 0;
}
