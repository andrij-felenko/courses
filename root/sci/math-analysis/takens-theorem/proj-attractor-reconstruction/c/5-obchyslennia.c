/* Обчислення кореляційного інтегралу мовою C */
int compute_correlation_integral_c(const DelayMatrixC *mat, const double *r_vals, size_t n_r, double *out_cr) {
    if (!mat || !mat->data || !r_vals || !out_cr) return -1;

    size_t n = mat->rows;
    size_t m = mat->cols;
    size_t total_pairs = (n * (n - 1)) / 2;
    if (total_pairs == 0) return -2;

    for (size_t k = 0; k < n_r; ++k) {
        double r = r_vals[k];
        double r_sq = r * r;
        size_t count = 0;

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                double dist_sq = 0.0;
                for (size_t d = 0; d < m; ++d) {
                    double diff = mat->data[i * m + d] - mat->data[j * m + d];
                    dist_sq += diff * diff;
                }
                if (dist_sq < r_sq) {
                    count++;
                }
            }
        }
        out_cr[k] = (double)count / (double)total_pairs;
    }
    return 0;
}
