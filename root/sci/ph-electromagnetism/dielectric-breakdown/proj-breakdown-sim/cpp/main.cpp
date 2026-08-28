#include <iostream>
#include <cmath>
#include <vector>
#include <iomanip>
#include <optional>

namespace Physics {

struct DielectricProperties {
    double electric_field_V_m{8.5e8};   // Напруженість поля [В/м]
    double thickness_m{100.0e-9};        // Товщина шару [м]
    double ambient_temp_K{300.0};        // Температура довкілля [К]
    double band_gap_eV{9.0};             // Ширина забороненої зони [еВ]
    double alpha_0_per_m{1.0e8};         // Коефіцієнт Таунсенда [1/м]
    double B_crit_V_m{3.0e9};            // Критичне поле іонізації [В/м]
    double base_sigma_Sm_m{1.0e-3};      // Базова провідність [См/м]
    double activation_energy_eV{0.6};    // Енергія активації [еВ]
    double heat_capacity_J_m3K{1.6e6};   // Теплоємність [Дж/(м³·К)]
    double heat_transfer_W_m2K{5000.0};  // Тепловідведення [Вт/(м²·К)]
};

struct SimulationState {
    double time_seconds{0.0};
    double electron_density_m3{1.0e10};
    double temperature_K{300.0};
    bool is_broken_down{false};
};

class BreakdownSimulator {
public:
    explicit BreakdownSimulator(DielectricProperties props)
        : props_(std::move(props)) {}

    [[nodiscard]] SimulationState run(double dt_seconds, double max_time_seconds) const {
        constexpr double k_B_eV = 8.617333e-5;
        constexpr double max_density_threshold = 1.0e24;
        
        SimulationState state{};
        state.temperature_K = props_.ambient_temp_K;

        while (state.time_seconds < max_time_seconds) {
            // 1. Обчислення коефіцієнта іонізації α(E)
            const double alpha = props_.alpha_0_per_m * std::exp(-props_.B_crit_V_m / props_.electric_field_V_m);
            constexpr double electron_mobility = 0.0020; // [м²/(В·с)]
            const double drift_velocity = electron_mobility * props_.electric_field_V_m;

            // 2. Оновлення концентрації носіїв (лавинна іонізація)
            const double dn_dt = alpha * drift_velocity * state.electron_density_m3;
            state.electron_density_m3 += dn_dt * dt_seconds;

            // 3. Тепловий баланс та саморозігрів
            const double sigma = props_.base_sigma_Sm_m * std::exp(-props_.activation_energy_eV / (k_B_eV * state.temperature_K));
            const double Q_generated = sigma * std::pow(props_.electric_field_V_m, 2);
            const double Q_dissipated = (props_.heat_transfer_W_m2K / props_.thickness_m) * (state.temperature_K - props_.ambient_temp_K);

            const double dT_dt = (Q_generated - Q_dissipated) / props_.heat_capacity_J_m3K;
            state.temperature_K += dT_dt * dt_seconds;

            // Перевірка умови пробою
            if (state.electron_density_m3 >= max_density_threshold || state.temperature_K >= props_.ambient_temp_K + 1000.0) {
                state.is_broken_down = true;
                break;
            }

            state.time_seconds += dt_seconds;
        }

        return state;
    }

private:
    DielectricProperties props_;
};

} // namespace Physics

int main() {
    using namespace Physics;

    DielectricProperties sio2_film{};
    sio2_film.electric_field_V_m = 8.7e8; // Поле 8.7 МВ/см

    BreakdownSimulator simulator(sio2_film);
    const auto result = simulator.run(1.0e-13, 1.0e-8);

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "=== Моделювання фізики пробою (C++17) ===\n";
    if (result.is_broken_down) {
        std::cout << "СТАТУС: Пробій зафіксовано!\n";
        std::cout << "Час пробою: " << result.time_seconds << " с (" << result.time_seconds * 1.0e12 << " пс)\n";
        std::cout << "Концентрація носіїв: " << result.electron_density_m3 << " м⁻³\n";
        std::cout << "Температура: " << std::fixed << std::setprecision(1) << result.temperature_K << " K\n";
    } else {
        std::cout << "СТАТУС: Діелектрик зберіг ізоляційні властивості.\n";
    }

    return 0;
}
