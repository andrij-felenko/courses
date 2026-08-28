/* c */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

/* Структура для зберігання статистичних параметрів хвильового пакета */
typedef struct {
    double norm;
    double mean_x;
    double var_x;
} WavepacketStats;

WavepacketStats compute_stats(const double complex *psi, int n, double dx, double x_min) {
    double norm = 0.0;
    double mean_x = 0.0;
    double var_x = 0.0;

    for (int i = 0; i < n; i++) {
        double prob = cabs(psi[i]) * cabs(psi[i]);
        double x = x_min + i * dx;
        norm += prob * dx;
        mean_x += x * prob * dx;
    }

    if (norm > 0.0) {
        mean_x /= norm;
        for (int i = 0; i < n; i++) {
            double prob = cabs(psi[i]) * cabs(psi[i]);
            double x = x_min + i * dx;
            var_x += (x - mean_x) * (x - mean_x) * prob * dx;
        }
        var_x /= norm;
    }

    WavepacketStats stats = {norm, mean_x, sqrt(var_x)};
    return stats;
}

/* Алгоритм прогонки (метод Томаса) для розв'язання тридіагональної СЛАУ */
void solve_tridiagonal(int n, const double complex *a, const double complex *b,
                       const double complex *c, double complex *d, double complex *x) {
    double complex *c_prime = (double complex *)malloc(n * sizeof(double complex));
    double complex *d_prime = (double complex *)malloc(n * sizeof(double complex));

    c_prime[0] = c[0] / b[0];
    d_prime[0] = d[0] / b[0];

    for (int i = 1; i < n; i++) {
        double complex denom = b[i] - a[i] * c_prime[i - 1];
        c_prime[i] = c[i] / denom;
        d_prime[i] = (d[i] - a[i] * d_prime[i - 1]) / denom;
    }

    x[n - 1] = d_prime[n - 1];
    for (int i = n - 2; i >= 0; i--) {
        x[i] = d_prime[i] - c_prime[i] * x[i + 1];
    }

    free(c_prime);
    free(d_prime);
}

int main(void) {
    const int N = 400;
    const double x_min = -20.0;
    const double x_max = 20.0;
    const double dx = (x_max - x_min) / (N - 1);
    const double dt = 0.01;
    const double hbar = 1.0;
    const double m = 1.0;
    const double sigma_0 = 1.0;
    const double k0 = 2.0;
    const int num_steps = 200;

    double complex *psi = (double complex *)malloc(N * sizeof(double complex));
    double complex *rhs = (double complex *)malloc(N * sizeof(double complex));
    double complex *psi_next = (double complex *)malloc(N * sizeof(double complex));

    /* Ініціалізація початкового Гаусового пакета */
    double norm_factor = 1.0 / pow(2.0 * PI * sigma_0 * sigma_0, 0.25);
    for (int i = 0; i < N; i++) {
        double x = x_min + i * dx;
        psi[i] = norm_factor * exp(-x * x / (4.0 * sigma_0 * sigma_0)) * cexp(I * k0 * x);
    }

    /* Формування діагональних елементів Кранка - Ніколсон */
    double alpha = hbar * dt / (4.0 * m * dx * dx);
    double complex diag_main = 1.0 + 2.0 * I * alpha;
    double complex diag_sub = -I * alpha;

    double complex *a = (double complex *)calloc(N, sizeof(double complex));
    double complex *b = (double complex *)malloc(N * sizeof(double complex));
    double complex *c = (double complex *)calloc(N, sizeof(double complex));

    for (int i = 0; i < N; i++) {
        b[i] = diag_main;
        if (i > 0) a[i] = diag_sub;
        if (i < N - 1) c[i] = diag_sub;
    }

    printf("Крок\tЧас t\tНорма\tСереднє X\tШирина sigma(t)\n");
    for (int step = 0; step <= num_steps; step += 40) {
        WavepacketStats stats = compute_stats(psi, N, dx, x_min);
        printf("%d\t%.2f\t%.5f\t%.4f\t\t%.4f\n", step, step * dt, stats.norm, stats.mean_x, stats.var_x);

        if (step == num_steps) break;

        for (int iter = 0; iter < 40; iter++) {
            for (int i = 1; i < N - 1; i++) {
                rhs[i] = (1.0 - 2.0 * I * alpha) * psi[i] + I * alpha * (psi[i - 1] + psi[i + 1]);
            }
            rhs[0] = 0.0;
            rhs[N - 1] = 0.0;

            solve_tridiagonal(N, a, b, c, rhs, psi_next);
            for (int i = 0; i < N; i++) psi[i] = psi_next[i];
        }
    }

    free(psi); free(rhs); free(psi_next);
    free(a); free(b); free(c);
    return 0;
}
