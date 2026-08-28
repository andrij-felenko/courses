#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>
#include <expected>
#include <string_view>

namespace flash_physics {

constexpr double EPS_0 = 8.854187817e-12;
constexpr double EPS_OX = 3.9;
constexpr double Q_ELEM = 1.602176634e-19;
constexpr double KB = 1.380649e-23;
constexpr double T_KELVIN = 300.0;

struct FlashCellParams {
    double t_ox_nm{8.0};           // Товщина тунельного SiO₂ (нм)
    double vth_erase_init{-2.5};    // Початкова порогова напруга Erase (В)
    double vth_prog_init{6.0};      // Початкова порогова напруга Program (В)
    double s_subthreshold_0{0.080}; // Початковий підпороговий нахил (В/декада)
    double area_cell_um2{0.0025};   // Площа комірки (мкм²)
};

struct WearState {
    std::size_t n_pe{0};
    double n_ot_cm3{0.0};
    double n_it_cm2{0.0};
    double vth_erase{0.0};
    double vth_prog{0.0};
    double vth_window{0.0};
    double subthreshold_s{0.0};
    double rber{0.0};
};

enum class SimulationError {
    InvalidOxideThickness,
    InvalidCycleCount
};

class FlashWearSimulator {
public:
    explicit FlashWearSimulator(FlashCellParams params) : params_(params) {}

    [[nodiscard]] std::expected<WearState, SimulationError>
    simulate(std::size_t n_pe) const noexcept {
        if (params_.t_ox_nm <= 0.0) {
            return std::unexpected(SimulationError::InvalidOxideThickness);
        }

        WearState state;
        state.n_pe = n_pe;

        // 1. Кінетика дефектів за степеневим законом
        constexpr double a_ot = 1.2e15;
        constexpr double alpha_ot = 0.45;
        state.n_ot_cm3 = a_ot * std::pow(static_cast<double>(n_pe), alpha_ot);

        constexpr double a_it = 8.0e9;
        constexpr double alpha_it = 0.40;
        state.n_it_cm2 = a_it * std::pow(static_cast<double>(n_pe), alpha_it);

        // 2. Геометричні та електростатичні перетворення в системи SI
        const double t_ox_m = params_.t_ox_nm * 1.0e-9;
        const double c_ox = (EPS_OX * EPS_0) / t_ox_m;

        const double n_ot_m3 = state.n_ot_cm3 * 1.0e6;
        const double n_it_m2 = state.n_it_cm2 * 1.0e4;

        // 3. Зсув Vth унаслідок захопленого негативного заряду
        const double delta_vth_ot = (Q_ELEM * n_ot_m3 * t_ox_m * t_ox_m) / (2.0 * EPS_OX * EPS_0);
        const double delta_vth_it = (Q_ELEM * n_it_m2) / c_ox;

        state.vth_erase = params_.vth_erase_init + delta_vth_ot + delta_vth_it;
        
        constexpr double screening_factor = 0.35;
        state.vth_prog = params_.vth_prog_init - screening_factor * delta_vth_ot;
        state.vth_window = state.vth_prog - state.vth_erase;

        // 4. Зростання підпорогового нахилу S від поверхневих станів
        constexpr double thermal_voltage = (KB * T_KELVIN) / Q_ELEM;
        state.subthreshold_s = params_.s_subthreshold_0 + 
            std::log(10.0) * thermal_voltage * (Q_ELEM * n_it_m2 / c_ox);

        // 5. Розрахунок RBER
        const double read_ref = (params_.vth_prog_init + params_.vth_erase_init) / 2.0;
        const double sigma_vth = 0.15 + 0.05 * std::log10(static_cast<double>(n_pe) + 1.0);

        const double z_erase = (read_ref - state.vth_erase) / sigma_vth;
        const double z_prog = (state.vth_prog - read_ref) / sigma_vth;

        const double p_err_erase = 0.5 * std::erfc(z_erase / std::sqrt(2.0));
        const double p_err_prog = 0.5 * std::erfc(z_prog / std::sqrt(2.0));

        state.rber = 0.5 * (p_err_erase + p_err_prog);

        return state;
    }

    [[nodiscard]] std::vector<WearState>
    run_sweep(std::span<const std::size_t> cycle_points) const {
        std::vector<WearState> results;
        results.reserve(cycle_points.size());

        for (const auto n_pe : cycle_points) {
            if (auto res = simulate(n_pe); res.has_value()) {
                results.push_back(res.value());
            }
        }
        return results;
    }

private:
    FlashCellParams params_;
};

} // namespace flash_physics

int main() {
    using namespace flash_physics;

    FlashWearSimulator simulator{FlashCellParams{.t_ox_nm = 8.0}};
    const std::vector<std::size_t> cycles{1, 100, 1000, 3000, 10000, 50000, 100000};

    const auto results = simulator.run_sweep(cycles);

    std::cout << "=== СИМУЛЯЦІЯ ЗНОСУ FLASH (C++20 RAII API) ===\n";
    std::cout << std::left 
              << std::setw(8)  << "N_PE" << " | "
              << std::setw(11) << "N_ot (cm⁻³)" << " | "
              << std::setw(11) << "N_it (cm⁻²)" << " | "
              << std::setw(9)  << "V_ERS (V)" << " | "
              << std::setw(9)  << "V_PGM (V)" << " | "
              << std::setw(10) << "RBER" << "\n";
    std::cout << std::string(72, '-') << "\n";

    for (const auto& r : results) {
        std::cout << std::left 
                  << std::setw(8)  << r.n_pe << " | "
                  << std::scientific << std::setprecision(2)
                  << std::setw(11) << r.n_ot_cm3 << " | "
                  << std::setw(11) << r.n_it_cm2 << " | "
                  << std::fixed << std::setprecision(2)
                  << std::setw(9)  << r.vth_erase << " | "
                  << std::setw(9)  << r.vth_prog << " | "
                  << std::scientific << std::setprecision(2)
                  << std::setw(10) << r.rber << "\n";
    }

    return 0;
}
