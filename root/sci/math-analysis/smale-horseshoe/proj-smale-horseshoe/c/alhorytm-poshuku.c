#include <stdio.h>
#include <stdlib.h>
#include <math.h>

double compute_capacity_dimension(double alpha, double beta) {
    double d_x = log(2.0) / log(1.0 / alpha);
    double d_y = log(2.0) / log(beta);
    return d_x + d_y;
}

void find_periodic_orbit_code(const int* code, size_t period, double alpha, double beta, Point2D* out_point) {
    double x = 0.0;
    double y = 0.0;
    double alpha_k = 1.0;
    double beta_k = 1.0 / beta;

    for (size_t iter = 0; iter < 10; ++iter) {
        for (size_t i = 0; i < period; ++i) {
            if (code[i] == 1) {
                x += alpha_k * (1.0 - alpha);
                y += beta_k;
            }
            alpha_k *= alpha;
            beta_k /= beta;
        }
    }
    out_point->x = x;
    out_point->y = y;
}
