// rikitake_sim.cpp - Ідіоматична C++ реалізація чисельного симулятора динамо Рікітаке
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <string>
#include <stdexcept>

struct RikitakeState {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

struct RikitakeParams {
    double mu{1.0};
    double a{5.0};
};

class RikitakeDynamoSimulator {
public:
    explicit RikitakeDynamoSimulator(RikitakeParams params, RikitakeState initial_state)
        : params_(params), current_state_(initial_state) {}

    [[nodiscard]] static RikitakeState derivatives(const RikitakeState& s, const RikitakeParams& p) noexcept {
        return RikitakeState{
            -p.mu * s.x + s.y * s.z,
            -p.mu * s.y + (s.z - p.a) * s.x,
            1.0 - s.x * s.y
        };
    }

    void step(double dt) noexcept {
        const auto k1 = derivatives(current_state_, params_);
        
        const RikitakeState s2{
            current_state_.x + 0.5 * dt * k1.x,
            current_state_.y + 0.5 * dt * k1.y,
            current_state_.z + 0.5 * dt * k1.z
        };
        const auto k2 = derivatives(s2, params_);

        const RikitakeState s3{
            current_state_.x + 0.5 * dt * k2.x,
            current_state_.y + 0.5 * dt * k2.y,
            current_state_.z + 0.5 * dt * k2.z
        };
        const auto k3 = derivatives(s3, params_);

        const RikitakeState s4{
            current_state_.x + dt * k3.x,
            current_state_.y + dt * k3.y,
            current_state_.z + dt * k3.z
        };
        const auto k4 = derivatives(s4, params_);

        current_state_.x += (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
        current_state_.y += (dt / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y);
        current_state_.z += (dt / 6.0) * (k1.z + 2.0 * k2.z + 2.0 * k3.z + k4.z);
    }

    void run_simulation(double t_max, double dt, const std::string& output_filename) {
        std::ofstream out_file(output_filename);
        if (!out_file.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл для запису: " + output_filename);
        }

        out_file << "time,x,y,z,is_reversal\n";

        const std::size_t total_steps = static_cast<std::size_t>(t_max / dt);
        double last_x = current_state_.x;
        double last_reversal_t = 0.0;
        std::size_t reversals = 0;

        for (std::size_t i = 0; i < total_steps; ++i) {
            const double t = i * dt;
            step(dt);

            const bool is_reversal = (last_x > 0.0 && current_state_.x < 0.0) ||
                                     (last_x < 0.0 && current_state_.x > 0.0);
            
            if (is_reversal) {
                ++reversals;
                const double interval = t - last_reversal_t;
                std::cout << "Інверсія #" << reversals << " на t=" << t 
                          << " (інтервал = " << interval << ")\n";
                last_reversal_t = t;
            }
            last_x = current_state_.x;

            out_file << t << "," << current_state_.x << "," 
                     << current_state_.y << "," << current_state_.z << "," 
                     << (is_reversal ? 1 : 0) << "\n";
        }

        std::cout << "Усього інверсій: " << reversals << ". Файл збережено: " << output_filename << "\n";
    }

    [[nodiscard]] RikitakeState get_state() const noexcept { return current_state_; }

private:
    RikitakeParams params_;
    RikitakeState current_state_;
};

int main() {
    try {
        const RikitakeParams params{1.0, 5.0};
        const RikitakeState init_state{0.1, 0.8, 2.0};
        
        RikitakeDynamoSimulator sim(params, init_state);
        sim.run_simulation(500.0, 0.01, "rikitake_cpp_trajectory.csv");
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
