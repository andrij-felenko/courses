// tdr_simulator.cpp — Ідіоматичний калькулятор імпедансу та TDR-симулятор мовою C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <format>
#include <expected>
#include <string_view>

namespace tline {

constexpr double c_speed = 299792458.0;
constexpr double epsilon_0 = 8.854187817e-12;
constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;

struct LineParameters {
    double z0;        // Ом
    double l0;        // Гн/м
    double c0;        // Ф/м
    double v_speed;   // м/с
    double delay_ps;  // пс/м
};

enum class LineError {
    InvalidGeometry,
    InvalidDielectric
};

class TransmissionLineCalculator {
public:
    static std::expected<LineParameters, LineError> coaxial(double d_inner, double d_outer, double er) noexcept {
        if (d_inner <= 0.0 || d_outer <= d_inner) {
            return std::unexpected(LineError::InvalidGeometry);
        }
        if (er < 1.0) {
            return std::unexpected(LineError::InvalidDielectric);
        }

        const double ratio = d_outer / d_inner;
        const double l0 = (mu_0 / (2.0 * std::numbers::pi)) * std::log(ratio);
        const double c0 = (2.0 * std::numbers::pi * epsilon_0 * er) / std::log(ratio);
        const double z0 = std::sqrt(l0 / c0);
        const double v = c_speed / std::sqrt(er);

        return LineParameters{
            .z0 = z0,
            .l0 = l0,
            .c0 = c0,
            .v_speed = v,
            .delay_ps = (1.0 / v) * 1e12
        };
    }

    static std::expected<LineParameters, LineError> microstrip(double width, double height, double thickness, double er) noexcept {
        if (width <= 0.0 || height <= 0.0) {
            return std::unexpected(LineError::InvalidGeometry);
        }
        if (er < 1.0) {
            return std::unexpected(LineError::InvalidDielectric);
        }

        const double e_eff = ((er + 1.0) / 2.0) + ((er - 1.0) / 2.0) * (1.0 / std::sqrt(1.0 + (12.0 * height / width)));
        const double z0 = (87.0 / std::sqrt(er + 1.41)) * std::log((5.98 * height) / (0.8 * width + thickness));
        const double v = c_speed / std::sqrt(e_eff);

        return LineParameters{
            .z0 = z0,
            .l0 = z0 / v,
            .c0 = 1.0 / (z0 * v),
            .v_speed = v,
            .delay_ps = (1.0 / v) * 1e12
        };
    }
};

struct TdrPoint {
    std::size_t segment_index;
    double impedance_ohm;
    double reflection_gamma;
    double measured_voltage;
};

class TdrSimulator {
public:
    static std::vector<TdrPoint> run(std::span<const double> impedance_profile, double step_voltage = 1.0) {
        std::vector<TdrPoint> results;
        if (impedance_profile.size() < 2) return results;

        results.reserve(impedance_profile.size() - 1);
        double v_forward = step_voltage;

        for (std::size_t i = 0; i < impedance_profile.size() - 1; ++i) {
            const double z_curr = impedance_profile[i];
            const double z_next = impedance_profile[i + 1];
            const double gamma = (z_next - z_curr) / (z_next + z_curr);
            const double v_refl = v_forward * gamma;

            results.push_back(TdrPoint{
                .segment_index = i + 1,
                .impedance_ohm = z_next,
                .reflection_gamma = gamma,
                .measured_voltage = step_voltage + v_refl
            });

            v_forward *= (1.0 + gamma);
        }

        return results;
    }
};

} // namespace tline

int main() {
    std::cout << "--- C++20 TDR & Transmission Line Engine ---\n";

    auto coax = tline::TransmissionLineCalculator::coaxial(0.9, 2.95, 2.25);
    if (coax) {
        std::cout << std::format("RG-58 Coax: Z0 = {:.1f} Ohm, L0 = {:.2f} nH/m, C0 = {:.2f} pF/m, delay = {:.0f} ps/m\n",
                                 coax->z0, coax->l0 * 1e9, coax->c0 * 1e12, coax->delay_ps);
    }

    auto mstrip = tline::TransmissionLineCalculator::microstrip(0.35, 0.20, 0.035, 4.2);
    if (mstrip) {
        std::cout << std::format("PCB Microstrip: Z0 = {:.1f} Ohm, L0 = {:.2f} nH/m, C0 = {:.2f} pF/m, delay = {:.0f} ps/m\n",
                                 mstrip->z0, mstrip->l0 * 1e9, mstrip->c0 * 1e12, mstrip->delay_ps);
    }

    const std::vector<double> profile = {50.0, 40.0, 65.0, 1000.0};
    const auto tdr_results = tline::TdrSimulator::run(profile, 1.0);

    std::cout << "\n=== TDR Response Trace ===\n";
    for (const auto& pt : tdr_results) {
        std::cout << std::format("Seg {}: Z = {:.1f} Ohm | Gamma = {:+.4f} | V_measured = {:.3f} V\n",
                                 pt.segment_index, pt.impedance_ohm, pt.reflection_gamma, pt.measured_voltage);
    }

    return 0;
}
