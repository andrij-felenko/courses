// spc_engine.hpp / spc_engine.cpp - C++20
#include <iostream>
#include <string_view>
#include <vector>
#include <span>
#include <cmath>
#include <expected>
#include <format>
#include <algorithm>

namespace spc {

enum class EvaluationError {
    InsufficientSamples,
    InvalidSpecificationLimits,
    NumericalInstability
};

struct ParameterSpec {
    std::string_view name;
    double golden_nominal;
    double lsl;
    double usl;

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return usl > lsl;
    }
};

struct CapabilityMetrics {
    double mean;
    double std_dev;
    double cp;
    double cpu;
    double cpl;
    double cpk;
    double golden_drift;
    bool is_capable;          // Cpk >= 1.33
    bool is_high_quality;     // Cpk >= 1.67
};

class StreamingAccumulator {
public:
    constexpr StreamingAccumulator() noexcept = default;

    void update(double x) noexcept {
        ++count_;
        double delta = x - mean_;
        mean_ += delta / static_cast<double>(count_);
        double delta2 = x - mean_;
        m2_ += delta * delta2;
        min_val_ = std::min(min_val_, x);
        max_val_ = std::max(max_val_, x);
    }

    template <typename Range>
    void update_batch(const Range& values) noexcept {
        for (double val : values) {
            update(val);
        }
    }

    [[nodiscard]] size_t count() const noexcept { return count_; }
    [[nodiscard]] double mean() const noexcept { return mean_; }
    [[nodiscard]] double min_value() const noexcept { return min_val_; }
    [[nodiscard]] double max_value() const noexcept { return max_val_; }

    [[nodiscard]] std::expected<double, EvaluationError> variance() const noexcept {
        if (count_ < 2) {
            return std::unexpected(EvaluationError::InsufficientSamples);
        }
        return m2_ / static_cast<double>(count_ - 1);
    }

private:
    size_t count_{0};
    double mean_{0.0};
    double m2_{0.0};
    double min_val_{std::numeric_limits<double>::infinity()};
    double max_val_{-std::numeric_limits<double>::infinity()};
};

[[nodiscard]] std::expected<CapabilityMetrics, EvaluationError>
analyze_capability(const StreamingAccumulator& acc, const ParameterSpec& spec) noexcept {
    if (acc.count() < 3) {
        return std::unexpected(EvaluationError::InsufficientSamples);
    }
    if (!spec.is_valid()) {
        return std::unexpected(EvaluationError::InvalidSpecificationLimits);
    }

    auto var_res = acc.variance();
    if (!var_res) {
        return std::unexpected(var_res.error());
    }

    double std_dev = std::sqrt(*var_res);
    if (std_dev < 1e-12) {
        std_dev = 1e-12;
    }

    double spec_width = spec.usl - spec.lsl;
    double cp = spec_width / (6.0 * std_dev);
    double cpu = (spec.usl - acc.mean()) / (3.0 * std_dev);
    double cpl = (acc.mean() - spec.lsl) / (3.0 * std_dev);
    double cpk = std::min(cpu, cpl);

    return CapabilityMetrics{
        .mean = acc.mean(),
        .std_dev = std_dev,
        .cp = cp,
        .cpu = cpu,
        .cpl = cpl,
        .cpk = cpk,
        .golden_drift = acc.mean() - spec.golden_nominal,
        .is_capable = (cpk >= 1.33),
        .is_high_quality = (cpk >= 1.67)
    };
}

void print_spc_report(const ParameterSpec& spec, const CapabilityMetrics& m, size_t sample_size) {
    std::cout << std::format("=== SPC АНАЛІЗ ПАРАМЕТРА: {} (N = {}) ===\n", spec.name, sample_size);
    std::cout << std::format("  Номінал Golden Sample: {:8.4f}\n", spec.golden_nominal);
    std::cout << std::format("  Межі специфікації     : [{:8.4f} ... {:8.4f}]\n", spec.lsl, spec.usl);
    std::cout << std::format("  Фактичне середнє (μ)  : {:8.4f} (Дрейф: {:+8.4f})\n", m.mean, m.golden_drift);
    std::cout << std::format("  Стандартне відхил. (σ): {:8.4f}\n", m.std_dev);
    std::cout << std::format("  Індекс придатності Cp : {:8.4f}\n", m.cp);
    std::cout << std::format("  Індекс придатності Cpk: {:8.4f} (Cpu: {:.3f}, Cpl: {:.3f})\n", m.cpk, m.cpu, m.cpl);
    
    std::string_view verdict = m.is_high_quality ? "ВІДПОВІДАЄ СЕРІЇ 5-SIGMA (Висока надійність)" :
                               m.is_capable      ? "ПРИДАТНО ДЛЯ МАСОВОГО ВИРОБНИЦТВА (Cpk >= 1.33)" :
                                                   "НЕПРИДАТНО / КРИТИЧНИЙ ДРЕЙФ (Потрібне 100% сортування)";
    std::cout << std::format("  Вердикт придатності   : {}\n\n", verdict);
}

} // namespace spc
