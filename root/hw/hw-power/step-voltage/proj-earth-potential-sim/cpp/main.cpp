#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <iomanip>

struct Electrode {
    double x{0.0};
    double y{0.0};
    double z{0.5};       // глибина занурення (м)
    double current{0.0}; // струм витоку (А)
};

struct SafetyReport {
    double max_v_step_volts{0.0};
    double foot_resistance_ohms{0.0};
    double total_circuit_ohms{0.0};
    double body_current_mA{0.0};
    double limit_current_mA{0.0};
    bool is_safe{false};
};

class GroundPotentialSimulator {
private:
    double rho_{100.0};         // питомий опір ґрунту (Ом·м)
    double body_resistance_{1000.0}; // опір тіла людини (Ом)
    double step_distance_{0.8}; // довжина кроку (м)
    std::vector<Electrode> electrodes_;

public:
    explicit GroundPotentialSimulator(double soil_resistivity, 
                                      double body_resistance = 1000.0, 
                                      double step_distance = 0.8)
        : rho_(soil_resistivity), body_resistance_(body_resistance), step_distance_(step_distance) {}

    void add_electrode(double x, double y, double z, double current) {
        electrodes_.push_back(Electrode{x, y, z, current});
    }

    [[nodiscard]] double potential_at(double x, double y) const noexcept {
        double v_total = 0.0;
        for (const auto& el : electrodes_) {
            const double dx = x - el.x;
            const double dy = y - el.y;
            double r = std::sqrt(dx * dx + dy * dy + el.z * el.z);
            if (r < 0.01) {
                r = 0.01; // захист від ділення на нуль
            }
            v_total += (rho_ * el.current) / (2.0 * std::numbers::pi * r);
        }
        return v_total;
    }

    [[nodiscard]] std::pair<double, double> max_step_voltage_at(double x, double y, int angles_count = 16) const noexcept {
        const double v_center = potential_at(x, y);
        double max_v_step = 0.0;
        double best_angle = 0.0;

        for (int i = 0; i < angles_count; ++i) {
            const double angle = 2.0 * std::numbers::pi * i / angles_count;
            const double nx = x + step_distance_ * std::cos(angle);
            const double ny = y + step_distance_ * std::sin(angle);
            const double v_next = potential_at(nx, ny);
            const double v_step = std::abs(v_center - v_next);
            if (v_step > max_v_step) {
                max_v_step = v_step;
                best_angle = angle;
            }
        }
        return {max_v_step, best_angle};
    }

    [[nodiscard]] double calculate_foot_resistance(double foot_radius = 0.08) const noexcept {
        return rho_ / (4.0 * foot_radius);
    }

    [[nodiscard]] SafetyReport evaluate_safety(double max_v_step, double fault_duration_sec) const noexcept {
        const double R_f = calculate_foot_resistance();
        const double R_total = body_resistance_ + 2.0 * R_f;
        const double I_body_mA = (max_v_step / R_total) * 1000.0;
        const double I_limit_mA = 116.0 / std::sqrt(fault_duration_sec);

        return SafetyReport{
            .max_v_step_volts = max_v_step,
            .foot_resistance_ohms = R_f,
            .total_circuit_ohms = R_total,
            .body_current_mA = I_body_mA,
            .limit_current_mA = I_limit_mA,
            .is_safe = (I_body_mA <= I_limit_mA)
        };
    }
};

int main() {
    GroundPotentialSimulator sim(100.0); // Ґрунт 100 Ом·м

    // Система з 4 стержнів 10х10 м
    sim.add_electrode(0.0, 0.0, 0.5, 250.0);
    sim.add_electrode(10.0, 0.0, 0.5, 250.0);
    sim.add_electrode(0.0, 10.0, 0.5, 250.0);
    sim.add_electrode(10.0, 10.0, 0.5, 250.0);

    std::cout << "=== Сітка потенціалів ґрунту (C++20 Simulation) ===\n";

    double overall_max_step = 0.0;
    std::pair<double, double> critical_point{0.0, 0.0};

    for (int ix = -20; ix <= 220; ix += 5) {
        const double x = ix / 10.0;
        for (int iy = -20; iy <= 220; iy += 5) {
            const double y = iy / 10.0;
            auto [v_step, angle] = sim.max_step_voltage_at(x, y);
            if (v_step > overall_max_step) {
                overall_max_step = v_step;
                critical_point = {x, y};
            }
        }
    }

    const auto report = sim.evaluate_safety(overall_max_step, 0.5);

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Найкритичніша точка: (" << critical_point.first << ", " << critical_point.second << ") м\n";
    std::cout << "Максимальна крокова напруга: " << report.max_v_step_volts << " В\n";
    std::cout << "Опір кола кроку: " << report.total_circuit_ohms << " Ом\n";
    std::cout << "Струм крізь тіло: " << report.body_current_mA << " мА\n";
    std::cout << "Граничний струм (0.5 с): " << report.limit_current_mA << " мА\n";
    std::cout << "Статус безпеки: " << (report.is_safe ? "БЕЗПЕЧНО" : "НЕБЕЗПЕЧНО (Потрібен контур вирівнювання!)") << "\n";

    return 0;
}
