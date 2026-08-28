#include <vector>
#include <cmath>
#include <algorithm>
#include <span >
#include <expected>

/* Обчислення взаємної інформації мовою C++ з використанням std::span та std::vector */
enum class EmbeddingError { InvalidInput, MemoryAllocationFailed };

std::expected<std::vector<double>, EmbeddingError>
compute_mutual_info_cpp(std::span<const double> signal, size_t max_delay, size_t n_bins = 32) {
    if (signal.empty() || n_bins == 0) {
        return std::unexpected(EmbeddingError::InvalidInput);
    }

    auto [min_it, max_it] = std::minmax_element(signal.begin(), signal.end());
    const double s_min = *min_it;
    const double s_max = *max_it;
    const double range = (s_max > s_min) ? (s_max - s_min) : 1.0;

    std::vector<double> mi_results(max_delay, 0.0);

    for (size_t p = 1; p <= max_delay && p < signal.size(); ++p) {
        const size_t pairs_count = signal.size() - p;
        std::vector<double> hist2d(n_bins * n_bins, 0.0);
        std::vector<double> px(n_bins, 0.0);
        std::vector<double> py(n_bins, 0.0);

        for (size_t k = 0; k < pairs_count; ++k) {
            auto bx = static_cast<size_t>(((signal[k] - s_min) / range) * n_bins);
            auto by = static_cast<size_t>(((signal[k + p] - s_min) / range) * n_bins);
            bx = std::min(bx, n_bins - 1);
            by = std::min(by, n_bins - 1);

            hist2d[bx * n_bins + by] += 1.0;
            px[bx] += 1.0;
            py[by] += 1.0;
        }

        double mi = 0.0;
        const double norm = static_cast<double>(pairs_count);
        for (size_t i = 0; i < n_bins; ++i) {
            for (size_t j = 0; j < n_bins; ++j) {
                const double pxy = hist2d[i * n_bins + j] / norm;
                const double p_x = px[i] / norm;
                const double p_y = py[j] / norm;
                if (pxy > 0.0 && p_x > 0.0 && p_y > 0.0) {
                    mi += pxy * std::log2(pxy / (p_x * p_y));
                }
            }
        }
        mi_results[p - 1] = mi;
    }

    return mi_results;
}
