#include <iostream>
#include <vector>
#include <optional>
#include <span>
#include <cmath>
#include <numeric>
#include <algorithm>

class DtofProcessor {
public:
    static constexpr double SPEED_OF_LIGHT_M_S = 299792458.0;

    struct Result {
        double distance_m{0.0};
        double confidence{0.0};
        double exact_time_ps{0.0};
    };

    explicit DtofProcessor(double bin_width_ps, uint32_t total_cycles) noexcept
        : bin_width_ps_{bin_width_ps}, total_cycles_{total_cycles} {}

    [[nodiscard]] std::optional<Result> process(std::span<const uint32_t> raw_hist) const {
        if (raw_hist.empty() || total_cycles_ == 0) {
            return std::nullopt;
        }

        std::vector<double> corr_hist(raw_hist.size());
        uint32_t cumulative_events = 0;

        // 1. Статистична пуассонівська корекція нагромадження (Coates pile-up correction)
        for (size_t i = 0; i < raw_hist.size(); ++i) {
            const auto available_cycles = static_cast<int64_t>(total_cycles_) - cumulative_events;
            if (available_cycles <= static_cast<int64_t>(raw_hist[i]) || available_cycles <= 0) {
                corr_hist[i] = static_cast<double>(raw_hist[i]);
            } else {
                double p = static_cast<double>(raw_hist[i]) / static_cast<double>(available_cycles);
                p = std::clamp(p, 0.0, 0.999);
                corr_hist[i] = -static_cast<double>(total_cycles_) * std::log(1.0 - p);
            }
            cumulative_events += raw_hist[i];
        }

        // 2. Оцінка рівня сонячного фону за крайніми бінами
        const size_t edge_bins = std::min<size_t>(8, raw_hist.size() / 4);
        double noise_sum = 0.0;
        size_t noise_count = 0;

        for (size_t i = 0; i < edge_bins; ++i) {
            noise_sum += corr_hist[i];
            noise_count++;
        }
        for (size_t i = raw_hist.size() - edge_bins; i < raw_hist.size(); ++i) {
            noise_sum += corr_hist[i];
            noise_count++;
        }
        const double noise_floor = (noise_count > 0) ? (noise_sum / static_cast<double>(noise_count)) : 0.0;

        // 3. Віднімання фону та пошук вершини піка
        for (auto& val : corr_hist) {
            val = std::max(0.0, val - noise_floor);
        }

        const auto max_it = std::max_element(corr_hist.begin(), corr_hist.end());
        const size_t peak_idx = std::distance(corr_hist.begin(), max_it);
        const double max_signal = *max_it;

        const double min_threshold = std::max(10.0, std::sqrt(noise_floor + 1.0) * 3.5);
        if (max_signal < min_threshold || peak_idx == 0 || peak_idx >= corr_hist.size() - 1) {
            return std::nullopt;
        }

        // 4. Суб-біновий розрахунок центроїда (центр мас 3 точок)
        const double w_left   = corr_hist[peak_idx - 1];
        const double w_center = corr_hist[peak_idx];
        const double w_right  = corr_hist[peak_idx + 1];
        const double weight_sum = w_left + w_center + w_right;

        if (weight_sum <= 0.0) {
            return std::nullopt;
        }

        const double sub_bin_offset = (w_right - w_left) / weight_sum;
        const double exact_bin = static_cast<double>(peak_idx) + sub_bin_offset;
        const double tof_seconds = exact_bin * (bin_width_ps_ * 1e-12);

        return Result{
            .distance_m = (SPEED_OF_LIGHT_M_S * tof_seconds) / 2.0,
            .confidence = max_signal / (noise_floor + 1.0),
            .exact_time_ps = exact_bin * bin_width_ps_
        };
    }

private:
    double bin_width_ps_{50.0};
    uint32_t total_cycles_{100000};
};
