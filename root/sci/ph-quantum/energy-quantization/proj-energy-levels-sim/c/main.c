#include <stdio.h>
#include <stdlib.h>
#include <math.h>

double c_potential(double z) {
    return 0.5 * z * z + 0.1 * z * z * z * z;
}

double c_numerov_shoot(double E, double z_min, double z_max, int N) {
    double h = (z_max - z_min) / N;
    double h2 = h * h;
    double psi_prev = 0.0;
    double psi_curr = 1e-5;

    for (int i = 1; i < N; ++i) {
        double z_prev = z_min + (i - 1) * h;
        double z_curr = z_min + i * h;
        double z_next = z_min + (i + 1) * h;

        double g_prev = 2.0 * (E - c_potential(z_prev));
        double g_curr = 2.0 * (E - c_potential(z_curr));
        double g_next = 2.0 * (E - c_potential(z_next));

        double num = 2.0 * (1.0 - (5.0 * h2 / 12.0) * g_curr) * psi_curr - (1.0 + (h2 / 12.0) * g_prev) * psi_prev;
        double den = 1.0 + (h2 / 12.0) * g_next;
        double psi_next = num / den;

        psi_prev = psi_curr;
        psi_curr = psi_next;
    }
    return psi_curr;
}

int main(void) {
    double z_min = -6.0, z_max = 6.0;
    int N = 2000;
    printf("=== Рівні енергії ангармонічного осцилятора (C Shooting Method) ===\n");

    double bounds[4][2] = {{0.4, 0.7}, {1.2, 1.6}, {2.2, 2.7}, {3.4, 4.0}};
    for (int n = 0; n < 4; ++n) {
        double low = bounds[n][0], high = bounds[n][1];
        while ((high - low) > 1e-7) {
            double mid = 0.5 * (low + high);
            if (c_numerov_shoot(low, z_min, z_max, N) * c_numerov_shoot(mid, z_min, z_max, N) <= 0.0) {
                high = mid;
            } else {
                low = mid;
            }
        }
        printf("Рівень n=%d: E_%d = %.6f\n", n, n, 0.5 * (low + high));
    }
    return 0;
}
