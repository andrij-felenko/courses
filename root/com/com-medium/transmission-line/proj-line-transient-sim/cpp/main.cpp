#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <expected>
#include <string>
#include <algorithm>

struct TransmissionLineConfig {
    double characteristic_impedance{50.0}; // Ом
    double phase_velocity{2.0e8};          // м/с
    double line_length{10.0};              // м
    double resistance_per_m{0.02};         // Ом/м
    double conductance_per_m{0.0};         // См/м
    double load_impedance{100.0};          // Ом
    double source_resistance{50.0};        // Ом
};

class TimeDomainReflectometerSim {
public:
    explicit TimeDomainReflectometerSim(TransmissionLineConfig cfg, std::size_t spatial_nodes = 200)
        : config_(cfg), nodes_count_(spatial_nodes) {}

    [[nodiscard]] std::expected<std::vector<double>, std::string> execute(std::size_t total_time_steps) const {
        if (nodes_count_ < 3) {
            return std::unexpected("Кількість вузлів сітки повинна бути не менше 3");
        }

        const double dz = config_.line_length / static_cast<double>(nodes_count_ - 1);
        const double l0 = config_.characteristic_impedance / config_.phase_velocity;
        const double c0 = 1.0 / (config_.characteristic_impedance * config_.phase_velocity);
        const double dt = 0.9 * (dz / config_.phase_velocity); // Умова Куранта

        std::vector<double> voltage(nodes_count_, 0.0);
        std::vector<double> current(nodes_count_ - 1, 0.0);
        std::vector<double> input_voltage_waveform(total_time_steps, 0.0);

        const double c_i1 = (1.0 - (config_.resistance_per_m * dt / (2.0 * l0))) / (1.0 + (config_.resistance_per_m * dt / (2.0 * l0)));
        const double c_i2 = (dt / (l0 * dz)) / (1.0 + (config_.resistance_per_m * dt / (2.0 * l0)));

        const double c_v1 = (1.0 - (config_.conductance_per_m * dt / (2.0 * c0))) / (1.0 + (config_.conductance_per_m * dt / (2.0 * c0)));
        const double c_v2 = (dt / (c0 * dz)) / (1.0 + (config_.conductance_per_m * dt / (2.0 * c0)));

        for (std::size_t t = 0; t < total_time_steps; ++t) {
            // Фронт напруги джерела 1.0 В з наростанням за 10 кроків
            const double e_src = (t < 10) ? (static_cast<double>(t) / 10.0) : 1.0;

            // Оновлення струмів
            for (std::size_t i = 0; i < nodes_count_ - 1; ++i) {
                const double dV = voltage[i + 1] - voltage[i];
                current[i] = c_i1 * current[i] - c_i2 * dV;
            }

            // Оновлення напруг у внутрішніх вузлах
            for (std::size_t i = 1; i < nodes_count_ - 1; ++i) {
                const double dI = current[i] - current[i - 1];
                voltage[i] = c_v1 * voltage[i] - c_v2 * dI;
            }

            // Вхідна гранична умова з урахуванням опору джерела
            const double i_src = (e_src - voltage[0]) / config_.source_resistance;
            voltage[0] += (2.0 * dt / (c0 * dz)) * (i_src - current[0]);

            // Вихідна гранична умова навантаження
            if (config_.load_impedance > 1e6) {
                voltage[nodes_count_ - 1] += (2.0 * dt / (c0 * dz)) * current[nodes_count_ - 2];
            } else if (config_.load_impedance < 1e-3) {
                voltage[nodes_count_ - 1] = 0.0;
            } else {
                voltage[nodes_count_ - 1] = current[nodes_count_ - 2] * config_.load_impedance;
            }

            input_voltage_waveform[t] = voltage[0];
        }

        return input_voltage_waveform;
    }

private:
    TransmissionLineConfig config_;
    std::size_t nodes_count_;
};

int main() {
    TransmissionLineConfig config{
        .characteristic_impedance = 50.0,
        .phase_velocity = 2.0e8,
        .line_length = 10.0,
        .resistance_per_m = 0.02,
        .conductance_per_m = 0.0,
        .load_impedance = 100.0,
        .source_resistance = 50.0
    };

    TimeDomainReflectometerSim simulator(config, 200);
    auto simulation_result = simulator.execute(600);

    if (simulation_result) {
        std::cout << "=== Симуляція TDR (C++23 реалізація) ===\n";
        std::cout << "Крок 50  (падаюча хвиля V_in): " << (*simulation_result)[50] << " В\n";
        std::cout << "Крок 250 (відбита хвиля V_ref): " << (*simulation_result)[250] << " В\n";
    } else {
        std::cerr << "Помилка виконання симуляції: " << simulation_result.error() << '\n';
    }

    return 0;
}
