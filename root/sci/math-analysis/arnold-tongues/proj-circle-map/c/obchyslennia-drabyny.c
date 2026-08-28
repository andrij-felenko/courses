#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double omega;
    double rotation_number;
    double derivative;
} staircase_point_t;

void compute_devils_staircase(double k_val, size_t num_points, size_t steps, staircase_point_t *out_points) {
    const double two_pi = 2.0 * M_PI;

    for (size_t i = 0; i < num_points; ++i) {
        double omega = (double)i / (double)(num_points - 1);
        double x = 0.1;

        /* Перехідний процес */
        for (size_t s = 0; s < steps; ++s) {
            x = x + omega - (k_val / two_pi) * sin(two_pi * x);
        }

        /* Вимірювання */
        double start_x = x;
        for (size_t s = 0; s < steps; ++s) {
            x = x + omega - (k_val / two_pi) * sin(two_pi * x);
        }

        double w = (x - start_x) / (double)steps;
        out_points[i].omega = omega;
        out_points[i].rotation_number = w;
        out_points[i].derivative = 0.0;
    }

    /* Числове диференціювання методом центральних різниць */
    double d_omega = 1.0 / (double)(num_points - 1);
    for (size_t i = 1; i < num_points - 1; ++i) {
        out_points[i].derivative = (out_points[i + 1].rotation_number - out_points[i - 1].rotation_number) / (2.0 * d_omega);
    }
}

int main(void) {
    const size_t n_pts = 11;
    staircase_point_t points[11];

    compute_devils_staircase(1.0, n_pts, 5000, points);

    printf("=== Таблиця драбини диявола (K = 1.0) ===\n");
    printf("   Omega  |  W(Omega) |   dW/dOmega\n");
    printf("-----------------------------------\n");
    for (size_t i = 0; i < n_pts; ++i) {
        printf("  %6.4f  |  %8.6f |  %10.4f\n", points[i].omega, points[i].rotation_number, points[i].derivative);
    }

    return 0;
}
