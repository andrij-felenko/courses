#include <iostream>
#include <cmath>
#include <string_view>
#include <format>
#include <expected>

namespace power_electronics {

// Параметри силової схеми та контуру комутації
struct CommutationConfig {
    double supply_voltage_v{600.0};
    double load_current_a{150.0};
    double cap_farads{7.5e-6};
    double ind_henry{50.0e-6};
    double series_resistance_ohm{0.04};
    double base_thyristor_tq_s{20.0e-6};
    double junction_temp_c{85.0};
    double time_step_s{1e-8};
    double max_sim_time_s{200.0e-6};
};

// Результат моделювання
struct SimulationSummary {
    double circuit_turnoff_time_s{0.0};
    double actual_tq_s{0.0};
    double peak_resonant_current_a{0.0};
    double peak_capacitor_voltage_v{0.0};
    double max_reapplied_dvdt_v_per_us{0.0};
    double safety_factor{0.0};
    bool is_successful{false};
};

enum class CommutationError {
    InsufficientTurnOffTime,
    CurrentNotExtinguished,
    OvervoltageExceeded
};

enum class SwitchState {
    Conducting,
    ReverseBiased,
    FullyRecovered,
    CommutationFault
};

class McMurraySimulator {
public:
    explicit McMurraySimulator(CommutationConfig config) noexcept
        : cfg_(config) {}

    [[nodiscard]] std::expected<SimulationSummary, CommutationError> run() const noexcept {
        SimulationSummary summary{};
        summary.actual_tq_s = calculate_thermal_tq(cfg_.base_thyristor_tq_s, cfg_.junction_temp_c);

        double current_time = 0.0;
        double cap_voltage = cfg_.supply_voltage_v;
        double choke_current = 0.0;
        SwitchState state = SwitchState::Conducting;

        double reverse_start_time = 0.0;
        double reverse_end_time = 0.0;
        double prev_anode_voltage = 0.0;

        while (current_time < cfg_.max_sim_time_s) {
            // Диференціальні рівняння другого порядку (метод Ейлера-Крамера)
            const double di_dt = (cap_voltage - cfg_.series_resistance_ohm * choke_current) / cfg_.ind_henry;
            choke_current += di_dt * cfg_.time_step_s;
            cap_voltage -= (choke_current / cfg_.cap_farads) * cfg_.time_step_s;

            if (choke_current > summary.peak_resonant_current_a) {
                summary.peak_resonant_current_a = choke_current;
            }
            if (std::abs(cap_voltage) > summary.peak_capacitor_voltage_v) {
                summary.peak_capacitor_voltage_v = std::abs(cap_voltage);
            }

            double anode_voltage = 0.0;

            switch (state) {
            case SwitchState::Conducting:
                if (choke_current < cfg_.load_current_a) {
                    anode_voltage = 1.5;
                } else {
                    state = SwitchState::ReverseBiased;
                    reverse_start_time = current_time;
                    anode_voltage = -1.0;
                }
                break;

            case SwitchState::ReverseBiased:
                if (choke_current >= cfg_.load_current_a) {
                    anode_voltage = -1.0;
                } else {
                    reverse_end_time = current_time;
                    const double tc = reverse_end_time - reverse_start_time;
                    summary.circuit_turnoff_time_s = tc;
                    summary.safety_factor = tc / summary.actual_tq_s;

                    if (tc >= summary.actual_tq_s) {
                        state = SwitchState::FullyRecovered;
                    } else {
                        state = SwitchState::CommutationFault;
                    }
                    anode_voltage = 0.0;
                }
                break;

            case SwitchState::FullyRecovered: {
                anode_voltage = cfg_.supply_voltage_v - cap_voltage;
                const double dv_dt = (anode_voltage - prev_anode_voltage) / (cfg_.time_step_s * 1e6);
                if (dv_dt > summary.max_reapplied_dvdt_v_per_us) {
                    summary.max_reapplied_dvdt_v_per_us = dv_dt;
                }
                break;
            }

            case SwitchState::CommutationFault:
                return std::unexpected(CommutationError::InsufficientTurnOffTime);
            }

            prev_anode_voltage = anode_voltage;
            current_time += cfg_.time_step_s;
        }

        if (state == SwitchState::FullyRecovered && summary.circuit_turnoff_time_s >= summary.actual_tq_s) {
            summary.is_successful = true;
            return summary;
        }

        return std::unexpected(CommutationError::CurrentNotExtinguished);
    }

private:
    [[nodiscard]] static constexpr double calculate_thermal_tq(double base_tq, double temp_c) noexcept {
        constexpr double temp_coefficient = 0.008;
        if (temp_c <= 25.0) {
            return base_tq;
        }
        return base_tq * (1.0 + temp_coefficient * (temp_c - 25.0));
    }

    CommutationConfig cfg_;
};

} // namespace power_electronics

int main() {
    using namespace power_electronics;

    CommutationConfig config{
        .supply_voltage_v = 600.0,
        .load_current_a = 150.0,
        .cap_farads = 7.5e-6,
        .ind_henry = 50.0e-6,
        .series_resistance_ohm = 0.04,
        .base_thyristor_tq_s = 20.0e-6,
        .junction_temp_c = 85.0,
        .time_step_s = 1e-8,
        .max_sim_time_s = 200.0e-6
    };

    McMurraySimulator sim{config};
    const auto result = sim.run();

    if (result.has_value()) {
        const auto &s = result.value();
        std::cout << "=== Результати C++ симуляції комутатора ===\n";
        std::cout << "Температура кристала: " << config.junction_temp_c << " C\n";
        std::cout << "Скоригований tq: " << (s.actual_tq_s * 1e6) << " мкс\n";
        std::cout << "Час зворотного зміщення tc: " << (s.circuit_turnoff_time_s * 1e6) << " мкс\n";
        std::cout << "Коефіцієнт запасу надійності ks: " << s.safety_factor << "\n";
        std::cout << "Піковий струм коливального імпульсу: " << s.peak_resonant_current_a << " А\n";
        std::cout << "Швидкість наростання напруги dv/dt: " << s.max_reapplied_dvdt_v_per_us << " В/мкс\n";
        std::cout << "Статус: УСПІШНА КОМУТАЦІЯ\n";
    } else {
        std::cerr << "Помилка комутації! Недостатній час відновлення носіїв у базі.\n";
        return 1;
    }

    return 0;
}
