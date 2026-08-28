#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>

namespace sse_sim {

// Фізичні константи
constexpr double HBAR = 1.0545718e-34;
constexpr double E_CHARGE = 1.6021766e-19;
constexpr double KB = 1.380649e-23;
constexpr double PI = 3.14159265358979323846;

// Конфігураційна структура для матеріалів
struct MaterialProperties {
    double Ms{1.4e5};           // А/м
    double lambda_mp{500e-9};   // м
    double g_mix{1.2e19};       // м^-2
    double rho_pt{20e-8};      // Ом·м
    double lambda_sd{1.5e-9};   // м
    double theta_sh{0.08};      // безрозмірний
    double length{5.0e-3};      // м
};

struct SimulationResult {
    double thickness_nm;
    double voltage_uv;
};

class SpinSeebeckSimulator {
public:
    explicit SpinSeebeckSimulator(MaterialProperties props) : props_(std::move(props)) {}

    [[nodiscard]] double compute_spin_current(double grad_T) const noexcept {
        return (props_.g_mix * KB * props_.lambda_mp / (2.0 * PI * props_.Ms)) * grad_T;
    }

    [[nodiscard]] std::vector<SimulationResult> run(double grad_T, std::span<const double> thicknesses_nm) const {
        const double Js_z = compute_spin_current(grad_T);
        const double prefactor = props_.length * props_.theta_sh * props_.rho_pt * props_.lambda_sd * (2.0 * E_CHARGE / HBAR);

        std::vector<SimulationResult> results;
        results.reserve(thicknesses_nm.size());

        for (const double d_nm : thicknesses_nm) {
            const double d_m = d_nm * 1e-9;
            const double x = d_m / (2.0 * props_.lambda_sd);
            
            // Чисельно стійке обчислення геометричного фактора
            const double F_factor = (x < 1e-4) ? (1.0 / (2.0 * props_.lambda_sd)) : (std::tanh(x) / d_m);
            const double v_volts = prefactor * Js_z * F_factor;
            results.push_back({d_nm, v_volts * 1e6});
        }
        return results;
    }

private:
    MaterialProperties props_;
};

} // namespace sse_sim

int main() {
    using namespace sse_sim;

    SpinSeebeckSimulator simulator(MaterialProperties{});
    constexpr double grad_T = 1.0e6; // 1 К/мкм
    const std::vector<double> thicknesses = {0.5, 1.0, 1.5, 3.0, 4.5, 6.0, 10.0};

    const auto results = simulator.run(grad_T, thicknesses);

    std::cout << "=== C++20 Симулятор спінового ефекту Зеєбека ===\n";
    std::cout << "Градієнт температури ∇T = " << grad_T << " К/м\n\n";
    std::cout << std::left << std::setw(12) << "d_Pt (нм)" << " | " << std::setw(15) << "V_ISHE (мкВ)" << "\n";
    std::cout << "-----------------------------------\n";

    for (const auto& [d_nm, v_uv] : results) {
        std::cout << std::left << std::setw(12) << std::fixed << std::setprecision(1) << d_nm
                  << " | " << std::setw(15) << std::setprecision(4) << v_uv << "\n";
    }

    return 0;
}
