// sound_speed.hpp - Idiomatic C++20 API
#pragma once

#include <cmath>
#include <expected>
#include <numbers>
#include <system_error>
#include <algorithm>

namespace acoustics {

enum class ErrorCode {
    InvalidParameter,
    TemperatureOutOfRange,
    PressureInvalid,
    PoissonRatioInvalid
};

struct AirConditions {
    double temperature_c{20.0};
    double relative_humidity_pct{50.0};
    double pressure_pa{101325.0};
};

struct WaterConditions {
    double temperature_c{15.0};
    double salinity_ppt{35.0};  // Standard ocean salinity 35 ppt
    double depth_m{0.0};
};

struct SolidMaterial {
    double young_modulus_pa;
    double poisson_ratio;
    double density_kg_m3;
};

struct WaveVelocities {
    double longitudinal_m_s{0.0};
    double transverse_m_s{0.0};
};

class SoundSpeedCalculator {
public:
    [[nodiscard]] static constexpr std::expected<double, ErrorCode> 
    calculate_air(const AirConditions& cond) noexcept {
        if (cond.temperature_c < -60.0 || cond.temperature_c > 80.0) {
            return std::unexpected(ErrorCode::TemperatureOutOfRange);
        }
        if (cond.pressure_pa <= 1000.0) {
            return std::unexpected(ErrorCode::PressureInvalid);
        }

        const double t = cond.temperature_c;
        const double rh = std::clamp(cond.relative_humidity_pct, 0.0, 100.0);
        
        // Antoine formula for vapor pressure
        const double p_sat = 610.78 * std::exp((17.27 * t) / (t + 237.3));
        const double p_v = (rh / 100.0) * p_sat;
        const double x_v = p_v / cond.pressure_pa;

        const double c_dry = 331.3 * std::sqrt(1.0 + t / 273.15);
        return c_dry * (1.0 + 0.16 * x_v);
    }

    [[nodiscard]] static constexpr std::expected<double, ErrorCode> 
    calculate_water(const WaterConditions& cond) noexcept {
        if (cond.temperature_c < -2.0 || cond.temperature_c > 40.0) {
            return std::unexpected(ErrorCode::TemperatureOutOfRange);
        }

        const double t = cond.temperature_c;
        const double s = cond.salinity_ppt;
        const double z = cond.depth_m;

        // Medwin oceanographic equation
        const double speed = 1449.2 + (4.6 * t) - (0.055 * t * t) + (0.00029 * t * t * t)
                            + (1.34 - 0.01 * t) * (s - 35.0) + (0.016 * z);
        return speed;
    }

    [[nodiscard]] static constexpr std::expected<WaveVelocities, ErrorCode> 
    calculate_solid(const SolidMaterial& mat) noexcept {
        if (mat.young_modulus_pa <= 0.0 || mat.density_kg_m3 <= 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }
        if (mat.poisson_ratio < 0.0 || mat.poisson_ratio >= 0.499) {
            return std::unexpected(ErrorCode::PoissonRatioInvalid);
        }

        const double e = mat.young_modulus_pa;
        const double nu = mat.poisson_ratio;
        const double rho = mat.density_kg_m3;

        const double c_L = std::sqrt((e * (1.0 - nu)) / (rho * (1.0 + nu) * (1.0 - 2.0 * nu)));
        const double c_S = std::sqrt(e / (2.0 * rho * (1.0 + nu)));

        return WaveVelocities{.longitudinal_m_s = c_L, .transverse_m_s = c_S};
    }
};

} // namespace acoustics
