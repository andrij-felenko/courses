#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <span>
#include <expected>
#include <string_view>

namespace mixed_fleet::telemetry {

struct KSResult {
    double d_statistic{0.0};
    double critical_threshold{0.0};
    bool distributions_differ{false};
};

class KolmogorovSmirnovComparator {
public:
    static std::expected<KSResult, std::string_view>
    compare(std::span<const double> cohort_a,
            std::span<const double> cohort_b,
            double c_alpha = 1.63) noexcept {
        if (cohort_a.empty() || cohort_b.empty()) {
            return std::unexpected("Cohorts cannot be empty for KS test");
        }

        std::vector<double> s1(cohort_a.begin(), cohort_a.end());
        std::vector<double> s2(cohort_b.begin(), cohort_b.end());

        std::sort(s1.begin(), s1.end());
        std::sort(s2.begin(), s2.end());

        size_t i = 0, j = 0;
        double d_max = 0.0;
        const double n1 = static_cast<double>(s1.size());
        const double n2 = static_cast<double>(s2.size());

        while (i < s1.size() && j < s2.size()) {
            const double v1 = s1[i];
            const double v2 = s2[j];

            if (v1 <= v2) {
                ++i;
            }
            if (v2 <= v1) {
                ++j;
            }

            const double fn1 = static_cast<double>(i) / n1;
            const double fn2 = static_cast<double>(j) / n2;
            d_max = std::max(d_max, std::abs(fn1 - fn2));
        }

        const double threshold = c_alpha * std::sqrt((n1 + n2) / (n1 * n2));

        return KSResult{
            .d_statistic = d_max,
            .critical_threshold = threshold,
            .distributions_differ = (d_max > threshold)
        };
    }
};

} // namespace mixed_fleet::telemetry
