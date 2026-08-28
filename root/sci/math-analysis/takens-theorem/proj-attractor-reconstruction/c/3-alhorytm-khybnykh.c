#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Обчислення FNN мовою C з прямим пошуком найближчого сусіда */
int compute_fnn_c(const double *signal, size_t n, size_t delay, size_t max_m, double r_tol, double *out_fnn) {
    if (!signal || !out_fnn || n == 0) return -1;

    double mean = 0.0, var = 0.0;
    for (size_t i = 0; i < n; ++i) mean += signal[i];
    mean /= (double)n;
    for (size_t i = 0; i < n; ++i) var += (signal[i] - mean) * (signal[i] - mean);
    double r_attr = sqrt(var / (double)n);
    if (r_attr == 0.0) r_attr = 1.0;

    for (size_t m = 1; m <= max_m; ++m) {
        if (n <= m * delay) break;
        size_t n_vectors = n - m * delay;

        size_t false_count = 0;
        for (size_t i = 0; i < n_vectors; ++i) {
            double min_dist_sq = 1e30;
            size_t nn_idx = i;

            for (size_t j = 0; j < n_vectors; ++j) {
                if (i == j) continue;
                double dist_sq = 0.0;
                for (size_t k = 0; k < m; ++k) {
                    double diff = signal[i + k * delay] - signal[j + k * delay];
                    dist_sq += diff * diff;
                }
                if (dist_sq < min_dist_sq) {
                    min_dist_sq = dist_sq;
                    nn_idx = j;
                }
            }

            double dist_m = sqrt(min_dist_sq);
            if (dist_m > 1e-12) {
                double diff_next = fabs(signal[i + m * delay] - signal[nn_idx + m * delay]);
                double dist_m1 = sqrt(min_dist_sq + diff_next * diff_next);
                if ((diff_next / dist_m > r_tol) || (dist_m1 / r_attr > 2.0)) {
                    false_count++;
                }
            }
        }
        out_fnn[m - 1] = (double)false_count / (double)n_vectors;
    }
    return 0;
}
