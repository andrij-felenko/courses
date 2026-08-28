#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <span>
#include <optional>
#include <iomanip>

struct BandwidthMetrics {
    double center_frequency_hz{0.0};
    double bw_3db_hz{0.0};
    double bw_obw99_hz{0.0};
    double f_low_3db_hz{0.0};
    double f_high_3db_hz{0.0};
    double f_low_obw_hz{0.0};
    double f_high_obw_hz{0.0};
};

class BandwidthEstimator {
public:
    [[nodiscard]] static std::optional<BandwidthMetrics> calculate(
        std::span<const double> psd,
        double start_frequency_hz,
        double bin_resolution_hz) noexcept
    {
        if (psd.size() < 3 || bin_resolution_hz <= 0.0) {
            return std::nullopt;
        }

        const auto max_it = std::max_element(psd.begin(), psd.end());
        const double p_max = *max_it;
        const auto max_idx = static_cast<size_t>(std::distance(psd.begin(), max_it));

        const double p_total = std::accumulate(psd.begin(), psd.end(), 0.0);
        if (p_max <= 1e-15 || p_total <= 1e-15) {
            return std::nullopt;
        }

        BandwidthMetrics metrics;
        metrics.center_frequency_hz = start_frequency_hz + static_cast<double>(max_idx) * bin_resolution_hz;

        // 1. Пошук і суб-бінова інтерполяція точок половинної потужності (-3 дБ)
        const double target_3db = p_max * 0.5;

        double left_idx = static_cast<double>(max_idx);
        for (size_t i = max_idx; i > 0; --i) {
            if (psd[i - 1] <= target_3db) {
                const double delta_p = psd[i] - psd[i - 1];
                const double frac = (delta_p > 1e-12) ? (target_3db - psd[i - 1]) / delta_p : 0.0;
                left_idx = static_cast<double>(i - 1) + frac;
                break;
            }
        }

        double right_idx = static_cast<double>(max_idx);
        for (size_t i = max_idx; i < psd.size() - 1; ++i) {
            if (psd[i + 1] <= target_3db) {
                const double delta_p = psd[i + 1] - psd[i];
                const double frac = (std::abs(delta_p) > 1e-12) ? (target_3db - psd[i]) / delta_p : 0.0;
                right_idx = static_cast<double>(i) + frac;
                break;
            }
        }

        metrics.f_low_3db_hz = start_frequency_hz + left_idx * bin_resolution_hz;
        metrics.f_high_3db_hz = start_frequency_hz + right_idx * bin_resolution_hz;
        metrics.bw_3db_hz = metrics.f_high_3db_hz - metrics.f_low_3db_hz;

        // 2. Кумулятивний пошук 99% OBW за стандартом ITU-R
        const double lower_threshold = p_total * 0.005;
        const double upper_threshold = p_total * 0.995;

        double running_sum = 0.0;
        size_t obw_low_idx = 0;
        size_t obw_high_idx = psd.size() - 1;
        bool low_found = false;

        for (size_t i = 0; i < psd.size(); ++i) {
            running_sum += psd[i];
            if (!low_found && running_sum >= lower_threshold) {
                obw_low_idx = i;
                low_found = true;
            }
            if (running_sum >= upper_threshold) {
                obw_high_idx = i;
                break;
            }
        }

        metrics.f_low_obw_hz = start_frequency_hz + static_cast<double>(obw_low_idx) * bin_resolution_hz;
        metrics.f_high_obw_hz = start_frequency_hz + static_cast<double>(obw_high_idx) * bin_resolution_hz;
        metrics.bw_obw99_hz = metrics.f_high_obw_hz - metrics.f_low_obw_hz;

        return metrics;
    }
};

int main() {
    constexpr size_t fft_bins = 512;
    std::vector<double> psd(fft_bins);
    constexpr double f_start = 100.0e6; // 100 МГц несуча
    constexpr double df = 1000.0;        // 1 кГц/бін

    constexpr double center_bin = 250.0;
    constexpr double sigma_bin = 20.0;
    for (size_t i = 0; i < fft_bins; ++i) {
        const double diff = static_cast<double>(i) - center_bin;
        psd[i] = std::exp(-(diff * diff) / (2.0 * sigma_bin * sigma_bin));
    }

    if (const auto metrics = BandwidthEstimator::calculate(psd, f_start, df)) {
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "=== Результати аналізу (C++20) ===\n";
        std::cout << "Пікова частота сигналу: " << metrics->center_frequency_hz / 1e6 << " МГц\n";
        std::cout << "Смуга за рівнем -3 дБ:  " << metrics->bw_3db_hz / 1e3 << " кГц (від "
                  << metrics->f_low_3db_hz / 1e6 << " до " << metrics->f_high_3db_hz / 1e6 << " МГц)\n";
        std::cout << "Зайнята смуга 99% OBW:  " << metrics->bw_obw99_hz / 1e3 << " кГц (від "
                  << metrics->f_low_obw_hz / 1e6 << " до " << metrics->f_high_obw_hz / 1e6 << " МГц)\n";
    }
    return 0;
}
