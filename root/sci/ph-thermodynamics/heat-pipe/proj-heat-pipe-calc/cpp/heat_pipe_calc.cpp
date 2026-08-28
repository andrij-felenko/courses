// heat_pipe_calc.cpp — Ідіоматична реалізація мовою C++ (C++20)
#include <iostream>
#include <cmath>
#include <string_view>
#include <numbers>
#include <expected>
#include <iomanip>

namespace thermal {

struct FluidProps {
    std::string_view name;
    double temp_c;            // °C
    double density_l;         // кг/м³
    double density_v;         // кг/м³
    double h_fg;              // Дж/кг
    double surface_tension;   // Н/м
    double viscosity_l;       // Па·с
    double k_fluid;           // Вт/(м·К)

    [[nodiscard]] constexpr double merit_number() const noexcept {
        return (density_l * surface_tension * h_fg) / viscosity_l;
    }
};

struct HeatPipeGeometry {
    double length_total;      // м
    double length_evap;       // м
    double length_cond;       // м
    double r_outer;           // м
    double r_inner;           // м
    double r_vapor;           // м
    double r_eff_pore;        // м
    double permeability;      // м²
    double porosity;          // 0..1
    double k_metal;           // Вт/(м·К)

    [[nodiscard]] constexpr double effective_length() const noexcept {
        return 0.5 * length_evap + (length_total - length_evap - length_cond) + 0.5 * length_cond;
    }

    [[nodiscard]] constexpr double wick_area() const noexcept {
        return std::numbers::pi * (r_inner * r_inner - r_vapor * r_vapor);
    }
};

struct AnalysisResult {
    double merit_number;
    double p_cap_max;
    double q_cap_limit;
    double q_boil_limit;
    double r_thermal_total;
};

enum class CalculationError {
    InvalidGeometry,
    NegativeAvailablePressure,
    ZeroViscosity
};

class HeatPipeAnalyzer {
public:
    [[nodiscard]] static std::expected<AnalysisResult, CalculationError> 
    analyze(const HeatPipeGeometry& hp, const FluidProps& fluid, double tilt_deg = 0.0) noexcept 
    {
        if (hp.r_outer <= hp.r_inner || hp.r_inner <= hp.r_vapor || fluid.viscosity_l <= 0.0) {
            return std::unexpected(CalculationError::InvalidGeometry);
        }

        AnalysisResult res{};
        res.merit_number = fluid.merit_number();
        res.p_cap_max = (2.0 * fluid.surface_tension) / hp.r_eff_pore;

        const double tilt_rad = tilt_deg * (std::numbers::pi / 180.0);
        const double p_grav = fluid.density_l * 9.81 * hp.length_total * std::sin(tilt_rad);
        const double available_dp = res.p_cap_max - p_grav;

        if (available_dp <= 0.0) {
            return std::unexpected(CalculationError::NegativeAvailablePressure);
        }

        const double l_eff = hp.effective_length();
        const double a_wick = hp.wick_area();

        // Капілярне обмеження
        res.q_cap_limit = available_dp * (fluid.density_l * hp.permeability * a_wick * fluid.h_fg) 
                          / (fluid.viscosity_l * l_eff);

        // Ефективна теплопровідність фітиля за Максвеллом
        const double km = hp.k_metal;
        const double kf = fluid.k_fluid;
        const double eps = hp.porosity;
        const double k_wick_eff = km * ((km + kf) - (1.0 - eps) * (km - kf)) 
                                  / ((km + kf) + (1.0 - eps) * (km - kf));

        // Кипійний ліміт
        const double t_sat_k = fluid.temp_c + 273.15;
        constexpr double r_b = 2.5e-6; // Радіус зародка бульбашки
        const double num = 4.0 * std::numbers::pi * hp.length_evap * k_wick_eff * fluid.surface_tension * t_sat_k;
        const double den = fluid.density_v * fluid.h_fg * r_b * std::log(hp.r_inner / hp.r_vapor);
        res.q_boil_limit = num / den;

        // Послідовний сумарний опір
        const double r_wall_evap = std::log(hp.r_outer / hp.r_inner) / (2.0 * std::numbers::pi * hp.length_evap * hp.k_metal);
        const double r_wick_evap = std::log(hp.r_inner / hp.r_vapor) / (2.0 * std::numbers::pi * hp.length_evap * k_wick_eff);
        const double r_wick_cond = std::log(hp.r_inner / hp.r_vapor) / (2.0 * std::numbers::pi * hp.length_cond * k_wick_eff);
        const double r_wall_cond = std::log(hp.r_outer / hp.r_inner) / (2.0 * std::numbers::pi * hp.length_cond * hp.k_metal);

        res.r_thermal_total = r_wall_evap + r_wick_evap + r_wick_cond + r_wall_cond;

        return res;
    }
};

} // namespace thermal

int main() {
    constexpr thermal::FluidProps water{
        .name = "Water (100 C)",
        .temp_c = 100.0,
        .density_l = 958.4,
        .density_v = 0.598,
        .h_fg = 2257000.0,
        .surface_tension = 0.0589,
        .viscosity_l = 0.000282,
        .k_fluid = 0.679
    };

    constexpr thermal::HeatPipeGeometry pipe{
        .length_total = 0.200,
        .length_evap = 0.050,
        .length_cond = 0.050,
        .r_outer = 0.0040,
        .r_inner = 0.0033,
        .r_vapor = 0.0025,
        .r_eff_pore = 15e-6,
        .permeability = 1.5e-11,
        .porosity = 0.55,
        .k_metal = 390.0
    };

    if (auto res = thermal::HeatPipeAnalyzer::analyze(pipe, water, 0.0); res.has_value()) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Аналіз теплової трубки (C++20) ===\n";
        std::cout << "Число Мерита:           " << std::scientific << res->merit_number << " Вт/м²\n";
        std::cout << std::fixed;
        std::cout << "Капілярний тиск:       " << res->p_cap_max << " Па\n";
        std::cout << "Капілярний ліміт:      " << res->q_cap_limit << " Вт\n";
        std::cout << "Кипійний ліміт:        " << res->q_boil_limit << " Вт\n";
        std::cout << "Сумарний тепловий опір: " << std::setprecision(4) << res->r_thermal_total << " °C/Вт\n";
    } else {
        std::cerr << "Помилка розрахунку теплової трубки!\n";
    }

    return 0;
}
