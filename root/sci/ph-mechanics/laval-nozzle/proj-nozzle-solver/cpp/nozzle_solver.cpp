// nozzle_solver.cpp — Ідіоматична реалізація розрахунку сопла Лаваля мовою C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <iomanip>
#include <span>

namespace GasDynamics {

struct GasProperties {
    double gamma{1.4};       // Показник адіабати
    double R{287.05};        // Газова стала, Дж/(кг·К)
    double P0{1e6};          // Повний тиск, Па
    double T0{300.0};        // Повна температура, К
    double P_amb{101325.0};  // Протитиск, Па
};

struct FlowState {
    double x{0.0};
    double area{0.0};
    double mach{0.0};
    double pressure{0.0};
    double temperature{0.0};
    double density{0.0};
    double velocity{0.0};
    bool has_shock{false};
};

class LavalNozzleSolver {
public:
    explicit LavalNozzleSolver(GasProperties props) : props_(props) {}

    [[nodiscard]] double areaRatioFromMach(double M) const noexcept {
        if (M <= 0.0) return 1e9;
        const double g_term = (2.0 / (props_.gamma + 1.0)) * (1.0 + 0.5 * (props_.gamma - 1.0) * M * M);
        const double exp_val = (props_.gamma + 1.0) / (2.0 * (props_.gamma - 1.0));
        return (1.0 / M) * std::pow(g_term, exp_val);
    }

    [[nodiscard]] double solveMach(double area_ratio, bool is_supersonic) const {
        if (std::abs(area_ratio - 1.0) < 1e-6) return 1.0;
        
        double M = is_supersonic ? 2.5 : 0.2;
        constexpr double epsilon = 1e-8;
        constexpr int max_iter = 100;

        for (int iter = 0; iter < max_iter; ++iter) {
            const double current_AR = areaRatioFromMach(M);
            const double dAR_dM = current_AR * (M * M - 1.0) / (M * (1.0 + 0.5 * (props_.gamma - 1.0) * M * M));
            const double f = current_AR - area_ratio;
            
            if (std::abs(f) < epsilon) break;
            M -= f / dAR_dM;
            
            if (!is_supersonic && M >= 1.0) M = 0.9999;
            if (is_supersonic && M <= 1.0) M = 1.0001;
        }
        return M;
    }

    [[nodiscard]] FlowState computeState(double x, double area, double mach) const {
        FlowState state;
        state.x = x;
        state.area = area;
        state.mach = mach;

        const double temp_ratio = 1.0 / (1.0 + 0.5 * (props_.gamma - 1.0) * mach * mach);
        const double press_ratio = std::pow(temp_ratio, props_.gamma / (props_.gamma - 1.0));

        state.temperature = props_.T0 * temp_ratio;
        state.pressure = props_.P0 * press_ratio;
        state.density = state.pressure / (props_.R * state.temperature);
        const double speed_of_sound = std::sqrt(props_.gamma * props_.R * state.temperature);
        state.velocity = mach * speed_of_sound;

        return state;
    }

    [[nodiscard]] std::optional<std::vector<FlowState>> solve(
        std::span<const double> x_mesh, 
        std::span<const double> area_mesh, 
        size_t throat_index) const 
    {
        if (x_mesh.size() != area_mesh.size() || throat_index >= x_mesh.size()) {
            return std::nullopt;
        }

        std::vector<FlowState> result;
        result.reserve(x_mesh.size());
        const double area_throat = area_mesh[throat_index];

        for (size_t i = 0; i < x_mesh.size(); ++i) {
            const double AR = area_mesh[i] / area_throat;
            const bool is_supersonic = (i > throat_index);
            const double mach = solveMach(AR, is_supersonic);
            result.push_back(computeState(x_mesh[i], area_mesh[i], mach));
        }

        return result;
    }

private:
    GasProperties props_;
};

} // namespace GasDynamics

int main() {
    using namespace GasDynamics;

    const GasProperties air{.gamma = 1.4, .R = 287.05, .P0 = 1.0e6, .T0 = 300.0, .P_amb = 101325.0};
    const LavalNozzleSolver solver(air);

    const std::vector<double> x_mesh{0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0};
    const std::vector<double> area_mesh{0.02, 0.015, 0.012, 0.01, 0.011, 0.014, 0.018, 0.023, 0.029, 0.035, 0.04};
    constexpr size_t throat_index = 3;

    if (const auto solution = solver.solve(x_mesh, area_mesh, throat_index)) {
        std::cout << "--- РОЗРАХУНОК СОПЛА ЛАВАЛЯ (C++) ---\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "x(m)\tArea(m2)\tMach\tP(kPa)\tT(K)\tVel(m/s)\n";
        for (const auto& pt : *solution) {
            std::cout << pt.x << "\t" << pt.area << "\t\t" << pt.mach << "\t" 
                      << pt.pressure / 1000.0 << "\t" << pt.temperature << "\t" << pt.velocity << "\n";
        }
    }
    return 0;
}
