#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/*
 * Генератор нормально розподілених випадкових чисел N(mean, stddev)
 * за алгоритмом перетворення Бокса — Мюллера.
 */
double generate_gaussian(double mean, double stddev) {
    static int have_spare = 0;
    static double spare;

    if (have_spare) {
        have_spare = 0;
        return mean + stddev * spare;
    }

    have_spare = 1;
    double u, v, s;
    do {
        u = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
        v = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
        s = u * u + v * v;
    } while (s >= 1.0 || s == 0.0);

    s = sqrt(-2.0 * log(s) / s);
    spare = v * s;
    return mean + stddev * (u * s);
}

int main(void) {
    const double kB = 1.380649e-23;
    const double R = 10000.0;     /* 10 кОм */
    const double T = 300.0;       /* 300 К */
    const double C = 1e-11;       /* 10 пФ */
    const double fs = 1e7;        /* 10 МГц */
    const size_t N = 1000000;
    const double dt = 1.0 / fs;

    const double sigma_v = sqrt(2.0 * kB * T * R * fs);
    const double alpha = exp(-dt / (R * C));

    double u_out = 0.0;
    double sum_sq = 0.0;

    for (size_t i = 0; i < N; ++i) {
        double u_in = generate_gaussian(0.0, sigma_v);
        u_out = alpha * u_out + (1.0 - alpha) * u_in;
        sum_sq += u_out * u_out;
    }

    double var_empirical = sum_sq / (double)N;
    double var_theoretical = kB * T / C;
    double rel_error = fabs(var_empirical - var_theoretical) / var_theoretical * 100.0;

    printf("=== Результати моделювання теплового шуму (C) ===\n");
    printf("Опір R = %.1f kOhm, Ємність C = %.1f pF, Температура T = %.1f K\n", R / 1000.0, C * 1e12, T);
    printf("Теоретична дисперсія <U^2> : %.6e V^2\n", var_theoretical);
    printf("Емпірична дисперсія        : %.6e V^2\n", var_empirical);
    printf("Відносна похибка          : %.2f%%\n\n", rel_error);

    return 0;
}
