#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iomanip>

struct PlateSystem {
    double mass{0.5};          // кг
    double sigma_0{5.8e7};     // См/м при 20°C
    double alpha_temp{0.00393};// 1/K
    double c_heat{385.0};      // Дж/(кг·K)
    double thickness{0.005};   // м
    double length{0.15};       // м
    double width{0.10};        // м
    double b_field{0.8};       // Тл
    double field_length{0.10}; // м
    double c_geo{0.25};
    double k_air{0.01};
};

struct SimulationState {
    double time{0.0};
    double position{0.0};
    double velocity{0.0};
    double temperature{20.0};  // °C
    double force{0.0};
    double power_dissipated{0.0};
};

class EddyBrakeSimulator {
public:
    explicit EddyBrakeSimulator(PlateSystem sys) : sys_(sys) {}

    [[nodiscard]] double compute_active_area(double pos) const noexcept {
        const double entry = pos;
        const double exit_edge = pos - sys_.length;
        
        const double start_in = std::clamp(entry, 0.0, sys_.field_length);
        const double end_in = std::clamp(exit_edge, 0.0, sys_.field_length);
        
        const double active_len = std::max(0.0, start_in - end_in);
        return active_len * sys_.width;
    }

    [[nodiscard]] SimulationState step(const SimulationState& current, double dt) const noexcept {
        const double active_area = compute_active_area(current.position);
        
        // Термічна деградація електропровідності
        const double current_sigma = sys_.sigma_0 / (1.0 + sys_.alpha_temp * (current.temperature - 20.0));

        // Гальмівна сила Ленца
        const double f_eddy = sys_.c_geo * current_sigma * sys_.thickness * active_area * 
                             (sys_.b_field * sys_.b_field) * current.velocity;
        
        const double f_air = sys_.k_air * current.velocity * std::abs(current.velocity);
        const double total_force = -(f_eddy + f_air);
        const double accel = total_force / sys_.mass;

        const double power = f_eddy * current.velocity;
        const double dT = (power * dt) / (sys_.mass * sys_.c_heat);

        SimulationState next;
        next.time = current.time + dt;
        next.velocity = std::max(0.0, current.velocity + accel * dt);
        next.position = current.position + next.velocity * dt;
        next.temperature = current.temperature + dT;
        next.force = total_force;
        next.power_dissipated = power;
        return next;
    }

    [[nodiscard]] std::vector<SimulationState> run(SimulationState start, double dt, double max_time) const {
        std::vector<SimulationState> history;
        history.reserve(static_cast<size_t>(max_time / dt));

        SimulationState state = start;
        history.push_back(state);

        while (state.time < max_time && state.velocity > 1e-4) {
            state = step(state, dt);
            history.push_back(state);
        }
        return history;
    }

private:
    PlateSystem sys_;
};

int main() {
    PlateSystem copper{.mass = 0.5, .sigma_0 = 5.8e7, .alpha_temp = 0.00393, .c_heat = 385.0,
                        .thickness = 0.005, .length = 0.15, .width = 0.10, 
                        .b_field = 0.8, .field_length = 0.10, .c_geo = 0.25, .k_air = 0.01};

    EddyBrakeSimulator sim(copper);
    SimulationState initial{.time = 0.0, .position = -0.05, .velocity = 5.0, .temperature = 20.0};

    auto results = sim.run(initial, 0.0001, 0.2);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Час(с)\tПоз(м)\tШвидк(м/с)\tТемп(C)\tСила(Н)\tПотужність(Вт)\n";
    for (size_t i = 0; i < results.size(); i += 200) {
        const auto& s = results[i];
        std::cout << s.time << "\t" << s.position << "\t" << s.velocity << "\t"
                  << s.temperature << "\t" << s.force << "\t" << s.power_dissipated << "\n";
    }
    return 0;
}
