#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <optional>
#include <expected>
#include <string_view>

struct PsdBreakpoint {
    double freq_hz{0.0};
    double psd_g2_hz{0.0};
};

struct StressLimits {
    double spec_low{0.0};
    double spec_high{0.0};
    double measured_lol{0.0};
    double measured_uol{0.0};
    double measured_ldl{0.0};
    double measured_udl{0.0};
};

struct MarginReport {
    double op_margin_low_pct{0.0};
    double op_margin_high_pct{0.0};
    double destruct_margin_low_pct{0.0};
    double destruct_margin_high_pct{0.0};
    bool is_qualified{false};
};

enum class AnalysisError {
    InsufficientData,
    InvalidFrequencyRange,
    InvalidSpecification
};

[[nodiscard]] std::expected<double, AnalysisError> calculate_g_rms(std::span<const PsdBreakpoint> pts) noexcept {
    if (pts.size() < 2) {
        return std::unexpected(AnalysisError::InsufficientData);
    }

    double total_area = 0.0;
    for (size_t i = 0; i < pts.size() - 1; ++i) {
        const auto& [f1, p1] = pts[i];
        const auto& [f2, p2] = pts[i + 1];

        if (f1 <= 0.0 || f2 <= f1 || p1 < 0.0 || p2 < 0.0) {
            return std::unexpected(AnalysisError::InvalidFrequencyRange);
        }

        if (std::abs(p1 - p2) < 1e-9) {
            total_area += p1 * (f2 - f1);
        } else {
            const double slope_db_oct = 10.0 * std::log10(p2 / p1) / (std::log2(f2 / f1));
            const double m = slope_db_oct / (10.0 * std::log10(2.0));

            if (std::abs(m + 1.0) < 1e-6) {
                total_area += p1 * f1 * std::log(f2 / f1);
            } else {
                total_area += (p2 * f2 - p1 * f1) / (m + 1.0);
            }
        }
    }
    return (total_area > 0.0) ? std::sqrt(total_area) : 0.0;
}

[[nodiscard]] std::expected<MarginReport, AnalysisError> evaluate_stress_margins(
    const StressLimits& limits, 
    double min_op_margin_pct, 
    double min_des_margin_pct) noexcept 
{
    const double spec_span = limits.spec_high - limits.spec_low;
    if (spec_span <= 0.0) {
        return std::unexpected(AnalysisError::InvalidSpecification);
    }

    MarginReport report;
    report.op_margin_low_pct = (limits.spec_low - limits.measured_lol) / spec_span * 100.0;
    report.op_margin_high_pct = (limits.measured_uol - limits.spec_high) / spec_span * 100.0;
    report.destruct_margin_low_pct = (limits.spec_low - limits.measured_ldl) / spec_span * 100.0;
    report.destruct_margin_high_pct = (limits.measured_udl - limits.spec_high) / spec_span * 100.0;

    report.is_qualified = (report.op_margin_low_pct >= min_op_margin_pct) &&
                          (report.op_margin_high_pct >= min_op_margin_pct) &&
                          (report.destruct_margin_low_pct >= min_des_margin_pct) &&
                          (report.destruct_margin_high_pct >= min_des_margin_pct);

    return report;
}
