// pendulum_sim.cpp - Ідіоматична реалізація на C++20 з RAII та шаблонами
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <array>

namespace physics {

struct PendulumParams {
    double length{1.0};       // L (м)
    double gravity{9.80665};  // g (м/с²)
    double dt{0.001};         // крок часу (с)
};

struct State {
    double theta{0.0};  // кут (рад)
    double omega{0.0};  // кутова швидкість (рад/с)
    double time{0.0};   // час (с)
};

class PendulumSimulator {
public:
    explicit PendulumSimulator(PendulumParams params) : params_{params} {}

    [[nodiscard]] State step_rk4(State s) const noexcept {
        auto auto_deriv = [this](double th, double om) noexcept {
            return std::pair{om, -(params_.gravity / params_.length) * std::sin(th)};
        };

        auto [k1_th, k1_om] = auto_deriv(s.theta, s.omega);
        auto [k2_th, k2_om] = auto_deriv(s.theta + 0.5 * params_.dt * k1_th,
                                         s.omega + 0.5 * params_.dt * k1_om);
        auto [k3_th, k3_om] = auto_deriv(s.theta + 0.5 * params_.dt * k2_th,
                                         s.omega + 0.5 * params_.dt * k2_om);
        auto [k4_th, k4_om] = auto_deriv(s.theta + params_.dt * k3_th,
                                         s.omega + params_.dt * k3_om);

        s.theta += (params_.dt / 6.0) * (k1_th + 2.0 * k2_th + 2.0 * k3_th + k4_th);
        s.omega += (params_.dt / 6.0) * (k1_om + 2.0 * k2_om + 2.0 * k3_om + k4_om);
        s.time += params_.dt;
        return s;
    }

    [[nodiscard]] double measure_period(double initial_deg) const {
        const double init_rad = initial_deg * (std::numbers::pi / 180.0);
        State state{.theta = init_rad, .omega = 0.0, .time = 0.0};

        std::vector<double> peak_times;
        double prev_th = state.theta;
        double prev_prev_th = state.theta;

        constexpr double max_sim_time = 30.0;
        while (state.time < max_sim_time && peak_times.size() < 2) {
            state = step_rk4(state);

            if (prev_th > 0.0 && prev_th >= prev_prev_th && prev_th >= state.theta) {
                peak_times.push_back(state.time - params_.dt);
            }
            prev_prev_th = prev_th;
            prev_th = state.theta;
        }

        if (peak_times.size() == 2) {
            return peak_times[1] - peak_times[0];
        }
        return 0.0;
    }

    [[nodiscard]] static constexpr double theoretical_period(double L, double g, double deg0) noexcept {
        const double rad0 = deg0 * (std::numbers::pi / 180.0);
        const double t0 = 2.0 * std::numbers::pi * std::sqrt(L / g);
        const double k = std::sin(rad0 / 2.0);
        const double k2 = k * k;
        const double k4 = k2 * k2;
        const double k6 = k4 * k2;

        return t0 * (1.0 + 0.25 * k2 + (9.0 / 64.0) * k4 + (225.0 / 2304.0) * k6);
    }

private:
    PendulumParams params_;
};

} // namespace physics

int main() {
    using namespace physics;
    PendulumParams params{.length = 1.0, .gravity = 9.80665, .dt = 0.0005};
    PendulumSimulator sim{params};

    constexpr std::array test_angles{5.0, 30.0, 60.0, 90.0, 120.0, 150.0};

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "=== МОДЕЛЮВАННЯ МАЯТНИКА (C++20 RK4) ===\n";
    std::cout << "Кут (°) | Симуляція (с) | Еліптична теорія (с) | Похибка (%)\n";
    std::cout << "-----------------------------------------------------------\n";

    for (double deg : test_angles) {
        double t_sim = sim.measure_period(deg);
        double t_theory = PendulumSimulator::theoretical_period(params.length, params.gravity, deg);
        double error_pct = std::abs(t_sim - t_theory) / t_theory * 100.0;

        std::cout << "  " << std::setw(5) << deg << " |   "
                  << std::setw(8) << t_sim << "    |      "
                  << std::setw(8) << t_theory << "        |  "
                  << std::setw(6) << error_pct << "%\n";
    }

    return 0;
}
