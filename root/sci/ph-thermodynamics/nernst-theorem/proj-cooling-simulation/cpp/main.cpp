#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <expected>
#include <string_view>

// Опис фізичних параметрів парамагнітної солі
struct CryogenicSalt {
    double g_factor{2.0};
    double debye_temperature{60.0};
    double internal_field{0.001}; // 1 мТл
    double max_field{1.5};         // 1.5 Тл
};

// Клас симулятора з використанням сучасних стандартів C++23
class AdiabaticDemagnetizationSimulator {
public:
    static constexpr double R_GAS = 8.314462618;
    static constexpr double MU_B = 9.274010078e-24;
    static constexpr double K_B = 1.380649e-23;

    explicit AdiabaticDemagnetizationSimulator(CryogenicSalt salt) : salt_(salt) {}

    [[nodiscard]] double calculate_spin_entropy(double temp, double field) const noexcept {
        if (temp <= 0.0) return 0.0;
        const double y = (salt_.g_factor * MU_B * field) / (2.0 * K_B * temp);
        if (y > 50.0) return 0.0;
        return R_GAS * (std::log(2.0 * std::cosh(y)) - y * std::tanh(y));
    }

    [[nodiscard]] double calculate_lattice_entropy(double temp) const noexcept {
        if (temp <= 0.0) return 0.0;
        const double ratio = temp / salt_.debye_temperature;
        return (4.0 / 5.0) * std::pow(std::numbers::pi, 4.0) * R_GAS * std::pow(ratio, 3.0);
    }

    [[nodiscard]] double calculate_total_entropy(double temp, double field) const noexcept {
        return calculate_spin_entropy(temp, field) + calculate_lattice_entropy(temp);
    }

    [[nodiscard]] std::expected<double, std::string_view> solve_adiabatic_step(
        double target_entropy, double target_field, double temp_min, double temp_max) const {
        if (temp_min >= temp_max) {
            return std::unexpected("Некоректні межі пошуку температури");
        }

        double low = temp_min;
        double high = temp_max;
        for (int i = 0; i < 60; ++i) {
            const double mid = 0.5 * (low + high);
            if (calculate_total_entropy(mid, target_field) < target_entropy) {
                low = mid;
            } else {
                high = mid;
            }
        }
        return 0.5 * (low + high);
    }

    struct SimulationStep {
        int cycle;
        double temp_start;
        double entropy_compressed;
        double temp_end;
    };

    [[nodiscard]] std::vector<SimulationStep> run_simulation(double initial_temp, int cycles) const {
        std::vector<SimulationStep> results;
        results.reserve(cycles);

        double current_temp = initial_temp;
        for (int i = 1; i <= cycles; ++i) {
            const double s_compressed = calculate_total_entropy(current_temp, salt_.max_field);
            auto temp_next = solve_adiabatic_step(s_compressed, salt_.internal_field, 1e-7, current_temp);

            if (!temp_next) break;

            results.push_back({i, current_temp, s_compressed, *temp_next});
            current_temp = *temp_next;
        }
        return results;
    }

private:
    CryogenicSalt salt_;
};

int main() {
    CryogenicSalt cmn_salt{.g_factor = 2.0, .debye_temperature = 60.0, .internal_field = 0.001, .max_field = 1.5};
    AdiabaticDemagnetizationSimulator sim(cmn_salt);

    const auto steps = sim.run_simulation(4.2, 6);

    std::cout << "=== Симуляція адіабатичного розмагнічування (C++23) ===\n";
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Крок | T_початкова (К) | S_магнітна (Дж/моль*К) | T_кінцева (К)\n";
    std::cout << "-------------------------------------------------------------\n";

    for (const auto& step : steps) {
        std::cout << std::setw(4) << step.cycle << " | "
                  << std::setw(15) << step.temp_start << " | "
                  << std::setw(22) << step.entropy_compressed << " | "
                  << std::setw(13) << step.temp_end << "\n";
    }

    std::cout << "-------------------------------------------------------------\n";
    if (!steps.empty()) {
        std::cout << "Досягнута температура: " << steps.back().temp_end << " К\n";
    }
    return 0;
}
