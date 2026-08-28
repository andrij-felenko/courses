#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

/* Обчислення середньої взаємної інформації мовою C */
int compute_mutual_info_c(const double *signal, size_t n, size_t max_delay, size_t n_bins, double *out_mi) {
    if (!signal || !out_mi || n == 0 || n_bins == 0) return -1;

    double s_min = signal[0], s_max = signal[0];
    for (size_t i = 1; i < n; ++i) {
        if (signal[i] < s_min) s_min = signal[i];
        if (signal[i] > s_max) s_max = signal[i];
    }
    double range = s_max - s_min;
    if (range == 0.0) range = 1.0;

    double *hist2d = (double*)calloc(n_bins * n_bins, sizeof(double));
    double *px = (double*)calloc(n_bins, sizeof(double));
    double *py = (double*)calloc(n_bins, sizeof(double));

    if (!hist2d || !px || !py) {
        free(hist2d); free(px); free(py);
        return -2;
    }

    for (size_t p = 1; p <= max_delay; ++p) {
        if (p >= n) break;
        size_t pairs_count = n - p;

        memset(hist2d, 0, n_bins * n_bins * sizeof(double));
        memset(px, 0, n_bins * sizeof(double));
        memset(py, 0, n_bins * sizeof(double));

        for (size_t k = 0; k < pairs_count; ++k) {
            size_t bx = (size_t)(((signal[k] - s_min) / range) * n_bins);
            size_t by = (size_t)(((signal[k + p] - s_min) / range) * n_bins);
            if (bx >= n_bins) bx = n_bins - 1;
            if (by >= n_bins) by = n_bins - 1;

            hist2d[bx * n_bins + by] += 1.0;
            px[bx] += 1.0;
            py[by] += 1.0;
        }

        double mi = 0.0;
        double norm = (double)pairs_count;
        for (size_t i = 0; i < n_bins; ++i) {
            for (size_t j = 0; j < n_bins; ++j) {
                double pxy = hist2d[i * n_bins + j] / norm;
                double p_x = px[i] / norm;
                double p_y = py[j] / norm;
                if (pxy > 0.0 && p_x > 0.0 && p_y > 0.0) {
                    mi += pxy * (log2(pxy / (p_x * p_y)));
                }
            }
        }
        out_mi[p - 1] = mi;
    }

    free(hist2d);
    free(px);
    free(py);
    return 0;
}
