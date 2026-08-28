/**
 * @file helmholtz_dsp.hpp
 * @brief Ідіоматичний C++20 API заголовочний контракт для акустичного аналізу.
 */

#ifndef HELMHOLTZ_DSP_HPP
#define HELMHOLTZ_DSP_HPP

#include <complex>
#include <expected>
#include <numbers>
#include <span>
#include <vector>

namespace acoustic {

enum class ErrorCode {
    InvalidParameter,
    WavelengthViolation,
    ShortNeckViolation,
    NonlinearRegime
};

struct Config {
    double cavity_volume_m3{0.001};
    double neck_length_m{0.05};
    double neck_radius_m{0.01};
    double temperature_celsius{20.0};
    double static_pressure_pa{101325.0};
    bool is_flanged_inner{true};
    bool is_flanged_outer{false};
};

struct Metrics {
    double resonance_freq_hz{0.0};
    double effective_length_m{0.0};
    double acoustic_mass_kg_m4{0.0};
    double compliance_m5_N{0.0};
    double quality_factor_q{0.0};
    double max_valid_freq_hz{0.0};
};

class HelmholtzCalculator {
public:
    [[nodiscard]] static std::expected<Metrics, ErrorCode> compute_metrics(const Config& cfg) noexcept;
    [[nodiscard]] static std::expected<std::complex<double>, ErrorCode> compute_impedance(const Config& cfg, const Metrics& m, double freq_hz) noexcept;
    [[nodiscard]] static std::expected<double, ErrorCode> compute_absorption(const Config& cfg, const Metrics& m, double pipe_area_m2, double freq_hz) noexcept;
};

} // namespace acoustic

#endif // HELMHOLTZ_DSP_HPP
