#include <iostream>
#include <cmath>
#include <numbers>
#include <optional>
#include <iomanip>

namespace antenna {

constexpr double speed_of_light = 299792458.0;
constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;

enum class Type { Dipole, Monopole, Loop };

struct Materials {
    static constexpr double Copper = 5.8e7;
    static constexpr double Aluminum = 3.5e7;
};

struct Parameters {
    Type type{Type::Dipole};
    double length_m{1.0};
    double wire_radius_m{0.001};
    double conductivity{Materials::Copper};
    int loop_turns{1};
};

struct PerformanceResult {
    double wavelength_m;
    double skin_depth_m;
    double r_rad_ohm;
    double r_loss_ohm;
    double efficiency_linear;
    double efficiency_db;
};

class Calculator {
public:
    [[nodiscard]] static std::optional<PerformanceResult> compute(
        double freq_hz, const Parameters& params) noexcept 
    {
        if (freq_hz <= 0.0 || params.length_m <= 0.0 || params.wire_radius_m <= 0.0) {
            return std::nullopt;
        }

        const double lambda = speed_of_light / freq_hz;
        const double delta = 1.0 / std::sqrt(std::numbers::pi * freq_hz * mu_0 * params.conductivity);
        const double l_rel = params.length_m / lambda;

        double r_rad = 0.0;

        switch (params.type) {
            case Type::Dipole:
                if (l_rel < 0.1) {
                    r_rad = 20.0 * std::numbers::pi * std::numbers::pi * l_rel * l_rel;
                } else if (std::abs(l_rel - 0.5) < 0.05) {
                    r_rad = 73.13;
                } else {
                    r_rad = 20.0 * std::numbers::pi * std::numbers::pi * l_rel * l_rel * (1.0 + 0.3 * l_rel);
                }
                break;

            case Type::Monopole:
                if (std::abs(l_rel - 0.25) < 0.025) {
                    r_rad = 36.56;
                } else {
                    r_rad = 10.0 * std::numbers::pi * std::numbers::pi * (4.0 * l_rel * l_rel);
                }
                break;

            case Type::Loop: {
                const double r_loop = params.length_m / (2.0 * std::numbers::pi);
                const double area = std::numbers::pi * r_loop * r_loop;
                const double n = static_cast<double>(params.loop_turns);
                r_rad = 31200.0 * n * n * (area * area) / (lambda * lambda * lambda * lambda);
                break;
            }
        }

        const double r_loss = params.length_m / 
            (2.0 * std::numbers::pi * params.wire_radius_m * params.conductivity * delta);

        const double eff = r_rad / (r_rad + r_loss);

        return PerformanceResult{
            .wavelength_m = lambda,
            .skin_depth_m = delta,
            .r_rad_ohm = r_rad,
            .r_loss_ohm = r_loss,
            .efficiency_linear = eff,
            .efficiency_db = 10.0 * std::log10(eff)
        };
    }
};

} // namespace antenna

int main() {
    constexpr double freq = 144.0e6; // 144 МГц

    const antenna::Parameters dipole{
        .type = antenna::Type::Dipole,
        .length_m = 1.02,
        .wire_radius_m = 0.001,
        .conductivity = antenna::Materials::Copper
    };

    if (const auto res = antenna::Calculator::compute(freq, dipole); res.has_value()) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Аналіз дипольної антени (f = " << freq / 1e6 << " МГц) ===\n";
        std::cout << "Довжина хвилі λ:    " << res->wavelength_m << " м\n";
        std::cout << "Скін-шар δ:         " << res->skin_depth_m * 1e6 << " мкм\n";
        std::cout << "Опір випромінювання R_рад: " << res->r_rad_ohm << " Ом\n";
        std::cout << "Опір втрат R_втрат:        " << std::setprecision(4) << res->r_loss_ohm << " Ом\n";
        std::cout << "ККД антени η:              " << std::setprecision(2) << res->efficiency_linear * 100.0 
                  << "% (" << res->efficiency_db << " дБ)\n";
    }

    return 0;
}
