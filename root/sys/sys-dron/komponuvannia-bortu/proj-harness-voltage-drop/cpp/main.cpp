#include <iostream>
#include <format>
#include <numbers>
#include <cmath>
#include <expected>
#include <string_view>

namespace avionics::wiring {

enum class AwgGauge : int {
    Awg10 = 10, Awg12 = 12, Awg14 = 14, Awg16 = 16,
    Awg18 = 18, Awg20 = 20, Awg22 = 22, Awg24 = 24,
    Awg26 = 26, Awg28 = 28, Awg30 = 30
};

struct HarnessSpec {
    AwgGauge gauge{AwgGauge::Awg22};
    double length_m{0.30};
    double current_amps{2.5};
    double operating_temp_c{45.0};
    bool shared_ground{true};
    double bus_voltage_v{5.0};
};

struct HarnessAnalysis {
    double wire_area_mm2{0.0};
    double loop_res_ohm{0.0};
    double single_res_ohm{0.0};
    double total_voltage_drop_v{0.0};
    double voltage_drop_pct{0.0};
    double ground_shift_v{0.0};
    double thermal_power_w{0.0};
    bool is_thermal_safe{false};
    bool is_ground_shift_safe{false};
};

enum class AnalysisError {
    InvalidLength,
    InvalidCurrent,
    ZeroVoltage
};

class HarnessCalculator {
public:
    static constexpr double CopperRho20C = 1.724e-8;   // Ом·м
    static constexpr double TempCoeff = 0.00393;        // 1/°C
    static constexpr double MaxCurrentDensity = 15.0;   // А/мм²
    static constexpr double MaxGndShiftVoltage = 0.200; // 200 мВ для 3.3V логіки

    [[nodiscard]] static constexpr double calculate_cross_section(AwgGauge gauge) noexcept {
        const double n = static_cast<double>(gauge);
        const double diameter_mm = 0.127 * std::pow(92.0, (36.0 - n) / 39.0);
        const double radius_mm = diameter_mm / 2.0;
        return std::numbers::pi * radius_mm * radius_mm;
    }

    [[nodiscard]] static std::expected<HarnessAnalysis, AnalysisError>
    analyze(const HarnessSpec& spec) noexcept {
        if (spec.length_m <= 0.0) {
            return std::unexpected(AnalysisError::InvalidLength);
        }
        if (spec.current_amps < 0.0) {
            return std::unexpected(AnalysisError::InvalidCurrent);
        }

        HarnessAnalysis result{};
        result.wire_area_mm2 = calculate_cross_section(spec.gauge);
        const double area_m2 = result.wire_area_mm2 * 1.0e-6;

        const double delta_t = spec.operating_temp_c - 20.0;
        const double rho_t = CopperRho20C * (1.0 + TempCoeff * delta_t);

        result.single_res_ohm = rho_t * spec.length_m / area_m2;
        result.loop_res_ohm = 2.0 * result.single_res_ohm;

        result.total_voltage_drop_v = spec.current_amps * result.loop_res_ohm;
        result.voltage_drop_pct = (spec.bus_voltage_v > 0.0)
            ? (result.total_voltage_drop_v / spec.bus_voltage_v) * 100.0
            : 0.0;

        result.ground_shift_v = spec.current_amps * result.single_res_ohm;
        result.thermal_power_w = spec.current_amps * spec.current_amps * result.loop_res_ohm;

        const double density = spec.current_amps / result.wire_area_mm2;
        result.is_thermal_safe = (density <= MaxCurrentDensity);
        result.is_ground_shift_safe = (!spec.shared_ground) || (result.ground_shift_v < MaxGndShiftVoltage);

        return result;
    }
};

} // namespace avionics::wiring
