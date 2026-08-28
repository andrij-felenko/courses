#include <vector>
#include <cmath>
#include <numeric>
#include <span >
#include <limits>
#include <expected>

/* Обчислення FNN мовою C++ з використанням стандартних контейнерів */
std::expected<std::vector<double>, EmbeddingError>
compute_fnn_cpp(std::span<const double> signal, size_t delay, size_t max_m = 6, double r_tol = 15.0) {
    if (signal.empty() || delay == 0) {
        return std::unexpected(EmbeddingError::InvalidInput);
    }

    const double mean = std::accumulate(signal.begin(), signal.end(), 0.0) / static_cast<double>(signal.size());
    double var = 0.0;
    for (double v : signal) var += (v - mean) * (v - mean);
    const double r_attr = std::sqrt(var / static_cast<double>(signal.size()));

    std::vector<double> fnn_results(max_m, 0.0);

    for (size_t m = 1; m <= max_m; ++m) {
        if (signal.size() <= m * delay) break;
        const size_t n_vectors = signal.size() - m * delay;

        size_t false_count = 0;
        for (size_t i = 0; i < n_vectors; ++i) {
            double min_dist_sq = std::numeric_limits<double>::max();
            size_t nn_idx = i;

            for (size_t j = 0; j < n_vectors; ++j) {
                if (i == j) continue;
                double dist_sq = 0.0;
                for (size_t k = 0; k < m; ++k) {
                    const double diff = signal[i + k * delay] - signal[j + k * delay];
                    dist_sq += diff * diff;
                }
                if (dist_sq < min_dist_sq) {
                    min_dist_sq = dist_sq;
                    nn_idx = j;
                }
            }

            const double dist_m = std::sqrt(min_dist_sq);
            if (dist_m > 1e-12) {
                const double diff_next = std::abs(signal[i + m * delay] - signal[nn_idx + m * delay]);
                const double dist_m1 = std::sqrt(min_dist_sq + diff_next * diff_next);
                if ((diff_next / dist_m > r_tol) || (dist_m1 / (r_attr > 0 ? r_attr : 1.0) > 2.0)) {
                    false_count++;
                }
            }
        }
        fnn_results[m - 1] = static_cast<double>(false_count) / static_cast<double>(n_vectors);
    }

    return fnn_results;
}
