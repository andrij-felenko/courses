#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <format>
#include <expected>
#include <string_view>

namespace thermo {

struct PhasePoint {
    double temp_k{273.16};
    double press_pa{611.65};
};

struct ThermoParams {
    static constexpr double r_spec = 461.5;       // Дж/(кг·К)
    static constexpr double t_crit = 647.10;      // К
    static constexpr double p_crit = 22064000.0;  // Па
    static constexpr double l_0 = 3150000.0;      // Дж/кг
    static constexpr double v_liq = 0.001;        // м³/кг
};

class ClapeyronSolver {
public:
    static constexpr double latent_heat(double temp_k) noexcept {
        if (temp_k >= ThermoParams::t_crit) return 0.0;
        const double tau = 1.0 - (temp_k / ThermoParams::t_crit);
        return ThermoParams::l_0 * std::pow(tau, 0.38);
    }

    static double rhs(double temp_k, double press_pa) noexcept {
        if (temp_k >= ThermoParams::t_crit || press_pa <= 0.0) return 0.0;

        const double l_vap = latent_heat(temp_k);
        double z_factor = 1.0 - 0.05 * (press_pa / ThermoParams::p_crit);
        z_factor = std::max(z_factor, 0.5);

        const double v_gas = (z_factor * ThermoParams::r_spec * temp_k) / press_pa;
        const double delta_v = v_gas - ThermoParams::v_liq;
        if (delta_v <= 1e-9) return 0.0;

        return l_vap / (temp_k * delta_v);
    }

    static double antoine_water_pa(double temp_k) noexcept {
        const double temp_c = temp_k - 273.15;
        constexpr double a = 8.07131;
        constexpr double b = 1730.63;
        constexpr double c = 233.426;
        const double p_mm_hg = std::pow(10.0, a - (b / (c + temp_c)));
        return p_mm_hg * 133.322;
    }

    [[nodiscard]] static std::vector<PhasePoint> integrate(
        PhasePoint start, double end_temp_k, double dt_k) 
    {
        std::vector<PhasePoint> trajectory;
        trajectory.reserve(static_cast<size_t>((end_temp_k - start.temp_k) / dt_k) + 2);

        PhasePoint current = start;
        trajectory.push_back(current);

        while (current.temp_k < end_temp_k) {
            const double t = current.temp_k;
            const double p = current.press_pa;

            const double k1 = rhs(t, p);
            const double k2 = rhs(t + 0.5 * dt_k, p + 0.5 * dt_k * k1);
            const double k3 = rhs(t + 0.5 * dt_k, p + 0.5 * dt_k * k2);
            const double k4 = rhs(t + dt_k, p + dt_k * k3);

            current.temp_k += dt_k;
            current.press_pa += (dt_k / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
            trajectory.push_back(current);
        }

        return trajectory;
    }
};

} // namespace thermo

int main() {
    using namespace thermo;

    const PhasePoint initial{273.16, 611.65};
    const auto curve = ClapeyronSolver::integrate(initial, 373.15, 1.0);

    std::cout << std::left 
              << std::setw(8)  << "T (C)"
              << std::setw(20) << "P_Clapeyron (hPa)"
              << std::setw(18) << "P_Antoine (hPa)"
              << std::setw(12) << "Error (%)" << "\n";
    std::cout << std::string(58, '-') << "\n";

    for (const auto& pt : curve) {
        const double temp_c = pt.temp_k - 273.15;
        if (std::abs(std::remainder(temp_c, 10.0)) < 1e-3) {
            const double p_hpa = pt.press_pa / 100.0;
            const double p_ant_hpa = ClapeyronSolver::antoine_water_pa(pt.temp_k) / 100.0;
            const double err = std::abs(p_hpa - p_ant_hpa) / p_ant_hpa * 100.0;

            std::cout << std::fixed << std::setprecision(1)
                      << std::setw(8)  << temp_c
                      << std::setprecision(2)
                      << std::setw(20) << p_hpa
                      << std::setw(18) << p_ant_hpa
                      << std::setw(12) << err << "\n";
        }
    }

    return 0;
}
