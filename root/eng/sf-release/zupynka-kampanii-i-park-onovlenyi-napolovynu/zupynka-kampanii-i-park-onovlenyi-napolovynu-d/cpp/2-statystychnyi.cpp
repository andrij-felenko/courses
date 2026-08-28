#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <span>
#include <expected>
#include <string_view>

namespace mixed_fleet::telemetry {

struct StatisticalVerdict {
    double u_statistic{0.0};
    double z_score{0.0};
    double p_value{1.0};
    bool is_significant_regression{false};
};

class CanaryAnomalyEvaluator {
public:
    static std::expected<StatisticalVerdict, std::string_view>
    evaluateCohorts(std::span<const double> baseline,
                    std::span<const double> canary,
                    double p_threshold = 0.01) noexcept {
        if (baseline.empty() || canary.empty()) {
            return std::unexpected("Cohorts must contain at least one latency sample");
        }

        struct SampleNode {
            double latency_ms;
            bool is_canary;
            double assigned_rank{0.0};
        };

        std::vector<SampleNode> data;
        data.reserve(baseline.size() + canary.size());

        for (double val : baseline) data.push_back({val, false, 0.0});
        for (double val : canary)   data.push_back({val, true, 0.0});

        std::sort(data.begin(), data.end(), [](const auto& a, const auto& b) noexcept {
            return a.latency_ms < b.latency_ms;
        });

        // Обчислення зв'язаних рангів
        size_t start_idx = 0;
        const size_t total_count = data.size();
        while (start_idx < total_count) {
            size_t end_idx = start_idx;
            while (end_idx + 1 < total_count && data[end_idx + 1].latency_ms == data[start_idx].latency_ms) {
                ++end_idx;
            }
            const double tie_rank = 1.0 + static_cast<double>(start_idx + end_idx) / 2.0;
            for (size_t k = start_idx; k <= end_idx; ++k) {
                data[k].assigned_rank = tie_rank;
            }
            start_idx = end_idx + 1;
        }

        double sum_r1 = 0.0;
        for (const auto& node : data) {
            if (!node.is_canary) sum_r1 += node.assigned_rank;
        }

        const double n1 = static_cast<double>(baseline.size());
        const double n2 = static_cast<double>(canary.size());

        const double u1 = n1 * n2 + (n1 * (n1 + 1.0)) / 2.0 - sum_r1;
        const double u2 = n1 * n2 - u1;
        const double u_stat = std::min(u1, u2);

        const double mean_u = (n1 * n2) / 2.0;
        const double std_u = std::sqrt((n1 * n2 * (n1 + n2 + 1.0)) / 12.0);

        StatisticalVerdict verdict;
        verdict.u_statistic = u_stat;
        verdict.z_score = (std_u > 1e-7) ? (u_stat - mean_u) / std_u : 0.0;
        verdict.p_value = std::erfc(std::abs(verdict.z_score) / std::sqrt(2.0));
        verdict.is_significant_regression = (verdict.p_value < p_threshold && verdict.z_score < 0.0);

        return verdict;
    }
};

} // namespace mixed_fleet::telemetry
