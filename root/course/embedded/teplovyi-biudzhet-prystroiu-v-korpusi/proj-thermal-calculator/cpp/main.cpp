#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>
#include <expected>
#include <numbers>

namespace thermal {

inline constexpr double kStefanBoltzmann = 5.670374419e-8;
inline constexpr double kAirConductivity = 0.0262;

enum class Material {
    PlasticABS,
    AluminumAnodized,
    AluminumRaw
};

enum class SolverError {
    InvalidGeometry,
    InvalidPower,
    NonConvergence
};

struct Enclosure {
    double length_m{0.120};
    double width_m{0.080};
    double height_m{0.050};
    double wall_thick_m{0.003};
    Material material{Material::PlasticABS};
    double ambient_temp_c{35.0};
    double solar_flux_w_m2{0.0};

    [[nodiscard]] constexpr double top_bottom_area() const noexcept {
        return length_m * width_m;
    }

    [[nodiscard]] constexpr double vertical_area() const noexcept {
        return 2.0 * (length_m + width_m) * height_m;
    }

    [[nodiscard]] constexpr double total_surface_area() const noexcept {
        return 2.0 * top_bottom_area() + vertical_area();
    }

    [[nodiscard]] constexpr double thermal_conductivity() const noexcept {
        switch (material) {
            case Material::AluminumAnodized:
            case Material::AluminumRaw:
                return 160.0;
            case Material::PlasticABS:
            default:
                return 0.20;
        }
    }

    [[nodiscard]] constexpr double emissivity() const noexcept {
        switch (material) {
            case Material::AluminumAnodized: return 0.88;
            case Material::AluminumRaw:      return 0.08;
            case Material::PlasticABS:
            default:                         return 0.92;
        }
    }
};

struct Component {
    double power_watts{3.5};
    double r_th_jc{4.0};
    double contact_area_m2{0.020 * 0.020};
    bool   has_gap_pad{false};
    double gap_thick_m{0.0015};
    double gap_k{3.0};
    double max_allowed_tj_c{105.0};
};

struct SimulationResult {
    double junction_temp_c{0.0};
    double case_temp_c{0.0};
    double inner_air_temp_c{0.0};
    double inner_wall_temp_c{0.0};
    double outer_wall_temp_c{0.0};
    double h_convection{0.0};
    double h_radiation{0.0};
    double r_th_external{0.0};
    double thermal_margin_c{0.0};
    bool   is_safe{false};
};

class ThermalSolver {
public:
    [[nodiscard]] static std::expected<SimulationResult, SolverError>
    calculate(const Enclosure& enc, const Component& comp) noexcept {
        if (enc.length_m <= 0.0 || enc.width_m <= 0.0 || enc.height_m <= 0.0) {
            return std::unexpected(SolverError::InvalidGeometry);
        }
        if (comp.power_watts < 0.0) {
            return std::unexpected(SolverError::InvalidPower);
        }

        const double a_total = enc.total_surface_area();
        const double k_wall = enc.thermal_conductivity();
        const double eps_wall = enc.emissivity();
        const double r_th_wall = enc.wall_thick_m / (k_wall * a_total);

        double r_th_bridge = 0.0;
        if (comp.has_gap_pad && comp.contact_area_m2 > 0.0 && comp.gap_k > 0.0) {
            r_th_bridge = comp.gap_thick_m / (comp.gap_k * comp.contact_area_m2) + 0.35;
        } else {
            // Тепловіддача через внутрішній застійний шар з урахуванням площі розтікання плати (~0.016 м²)
            constexpr double kEffectivePcbArea = 0.016;
            r_th_bridge = 0.010 / (kAirConductivity * kEffectivePcbArea);
        }

        const double p_solar = enc.solar_flux_w_m2 * (enc.top_bottom_area() + 0.5 * enc.vertical_area()) * 0.7;
        const double p_total_ext = comp.power_watts + p_solar;

        double t_wall_out = enc.ambient_temp_c + 5.0;
        const double t_amb_k = enc.ambient_temp_c + 273.15;
        double h_c = 5.0;
        double h_r = 5.0;

        for (int iter = 0; iter < 100; ++iter) {
            double delta_t = std::abs(t_wall_out - enc.ambient_temp_c);
            if (delta_t < 0.1) delta_t = 0.1;

            h_c = 1.42 * std::pow(delta_t / enc.height_m, 0.25);
            if (h_c < 2.0) h_c = 2.0;

            const double t_wall_k = t_wall_out + 273.15;
            const double t_mean_k = 0.5 * (t_wall_k + t_amb_k);
            h_r = 4.0 * eps_wall * kStefanBoltzmann * std::pow(t_mean_k, 3.0);

            const double h_ext = h_c + h_r;
            const double r_ext = 1.0 / (h_ext * a_total);

            const double next_t_wall = enc.ambient_temp_c + p_total_ext * r_ext;
            if (std::abs(next_t_wall - t_wall_out) < 0.005) {
                t_wall_out = next_t_wall;
                break;
            }
            t_wall_out = 0.7 * t_wall_out + 0.3 * next_t_wall;
        }

        const double delta_t_wall = comp.power_watts * r_th_wall;
        const double t_wall_in    = t_wall_out + delta_t_wall;
        const double t_case       = t_wall_in + comp.power_watts * r_th_bridge;
        const double t_junction   = t_case + comp.power_watts * comp.r_th_jc;
        const double t_air_in     = 0.5 * (t_case + t_wall_in);

        SimulationResult res{};
        res.outer_wall_temp_c = t_wall_out;
        res.inner_wall_temp_c = t_wall_in;
        res.inner_air_temp_c  = t_air_in;
        res.case_temp_c       = t_case;
        res.junction_temp_c   = t_junction;
        res.h_convection      = h_c;
        res.h_radiation       = h_r;
        res.r_th_external     = 1.0 / ((h_c + h_r) * a_total);
        res.thermal_margin_c  = comp.max_allowed_tj_c - t_junction;
        res.is_safe           = (res.thermal_margin_c >= 0.0);

        return res;
    }
};

void display_result(std::string_view label, const SimulationResult& res) noexcept {
    std::cout << "========================================================\n"
              << "СЦЕНАРІЙ: " << label << '\n'
              << "========================================================\n"
              << std::fixed << std::setprecision(2)
              << "Зовнішня стінка корпусу: " << std::setw(6) << res.outer_wall_temp_c << " °C\n"
              << "Внутрішня стінка корпусу: " << std::setw(6) << res.inner_wall_temp_c << " °C\n"
              << "Повітря всередині боксу: " << std::setw(6) << res.inner_air_temp_c << " °C\n"
              << "Корпус чіпа (T_case):    " << std::setw(6) << res.case_temp_c << " °C\n"
              << "Кристал чіпа (T_junction):" << std::setw(6) << res.junction_temp_c << " °C\n"
              << "--------------------------------------------------------\n"
              << "Коефіцієнт конвекції:    " << std::setw(6) << res.h_convection << " Вт/(м²·К)\n"
              << "Коефіцієнт радіації:     " << std::setw(6) << res.h_radiation << " Вт/(м²·К)\n"
              << "Зовнішній опір корпусу:  " << std::setw(6) << res.r_th_external << " °C/Вт\n"
              << "Запас до перегріву:      " << std::setw(6) << res.thermal_margin_c
              << " °C -> " << (res.is_safe ? "[OK - БЕЗПЕЧНО]" : "[ПЕРЕГРІВ!]") << "\n"
              << "========================================================\n\n";
}

} // namespace thermal

int main() {
    using namespace thermal;

    Enclosure enc{
        .length_m = 0.120,
        .width_m = 0.080,
        .height_m = 0.050,
        .wall_thick_m = 0.003,
        .material = Material::PlasticABS,
        .ambient_temp_c = 35.0,
        .solar_flux_w_m2 = 0.0
    };

    Component comp{
        .power_watts = 3.5,
        .r_th_jc = 4.0,
        .contact_area_m2 = 0.020 * 0.020,
        .has_gap_pad = false,
        .gap_thick_m = 0.0015,
        .gap_k = 3.0,
        .max_allowed_tj_c = 105.0
    };

    if (auto res1 = ThermalSolver::calculate(enc, comp)) {
        display_result("Пластиковий герметичний бокс IP67 (без термомосту)", *res1);
    }

    enc.material = Material::AluminumAnodized;
    comp.has_gap_pad = true;

    if (auto res2 = ThermalSolver::calculate(enc, comp)) {
        display_result("Алюмінієвий корпус з анодуванням + Gap Pad (3 Вт/м·К)", *res2);
    }

    return 0;
}
