/* Обчислення кореляційного інтегралу мовою C++ */
std::vector<double> compute_correlation_integral_cpp(const DelayMatrixCpp& mat, std::span<const double> r_vals) {
    const size_t n = mat.rows();
    const size_t m = mat.cols();
    const size_t total_pairs = (n * (n - 1)) / 2;
    std::vector<double> cr_results(r_vals.size(), 0.0);

    if (total_pairs == 0) return cr_results;

    for (size_t k = 0; k < r_vals.size(); ++k) {
        const double r_sq = r_vals[k] * r_vals[k];
        size_t count = 0;

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                double dist_sq = 0.0;
                for (size_t d = 0; d < m; ++d) {
                    const double diff = mat(i, d) - mat(j, d);
                    dist_sq += diff * diff;
                }
                if (dist_sq < r_sq) {
                    count++;
                }
            }
        }
        cr_results[k] = static_cast<double>(count) / static_cast<double>(total_pairs);
    }

    return cr_results;
}
