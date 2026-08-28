#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <array>

struct CircuitParams {
    double v_cc{0.18};      // Напруга джерела живлення (В)
    double r_l{2.0};        // Опір активних втрат (Ом)
    double l_ind{1.0e-6};   // Індуктивність контуру (Гн)
    double c_cap{100.0e-12};// Паралельна ємність (Ф)
};

struct DiodeParams {
    double v_p{0.07};   // Напруга піку (В)
    double i_p{0.005};  // Струм піку (А)
    double v_v{0.35};   // Напруга долини (В)
    double i_v{0.0005}; // Струм долини (А)
    double alpha{10.0}; // Градієнт експоненти (1/В)
};

struct State {
    double v{0.01};
    double i_l{0.001};

    [[nodiscard]] constexpr State operator+(const State& rhs) const noexcept {
        return {v + rhs.v, i_l + rhs.i_l};
    }
    [[nodiscard]] constexpr State operator*(double scalar) const noexcept {
        return {v * scalar, i_l * scalar};
    }
};

class TunnelDiodeOscillator {
public:
    explicit TunnelDiodeOscillator(CircuitParams cp = {}, DiodeParams dp = {})
        : c_params_{cp}, d_params_{dp} {}

    [[nodiscard]] double diode_current(double v) const noexcept {
        if (v < 0.0) {
            return -d_params_.i_p * (std::abs(v) / d_params_.v_p);
        }
        const double i_tunnel = d_params_.i_p * (v / d_params_.v_p) * 
                                std::exp(1.0 - v / d_params_.v_p);
        const double i_diff = (v > d_params_.v_v) 
            ? d_params_.i_v * std::exp(d_params_.alpha * (v - d_params_.v_v)) 
            : 0.0;
        return i_tunnel + i_diff;
    }

    [[nodiscard]] State derivatives(State s) const noexcept {
        return {
            (s.i_l - diode_current(s.v)) / c_params_.c_cap,
            (c_params_.v_cc - s.v - c_params_.r_l * s.i_l) / c_params_.l_ind
        };
    }

    [[nodiscard]] std::vector<State> run_simulation(double dt, std::size_t steps) const {
        std::vector<State> history;
        history.reserve(steps);

        State current_state{0.01, 0.001};

        for (std::size_t step = 0; step < steps; ++step) {
            history.push_back(current_state);

            const State k1 = derivatives(current_state);
            const State k2 = derivatives(current_state + k1 * (0.5 * dt));
            const State k3 = derivatives(current_state + k2 * (0.5 * dt));
            const State k4 = derivatives(current_state + k3 * dt);

            current_state = current_state + (k1 + k2 * 2.0 + k3 * 2.0 + k4) * (dt / 6.0);
        }
        return history;
    }

private:
    CircuitParams c_params_;
    DiodeParams d_params_;
};

int main() {
    constexpr double dt = 1.0e-11;
    constexpr std::size_t steps = 20000;

    const TunnelDiodeOscillator simulator;
    const auto results = simulator.run_simulation(dt, steps);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Час (нс)\tНапруга (мВ)\tСтрум (мА)\n";
    for (std::size_t i = 0; i < results.size(); i += 2000) {
        std::cout << (i * dt * 1.0e9) << "\t\t"
                  << (results[i].v * 1000.0) << "\t\t"
                  << (results[i].i_l * 1000.0) << "\n";
    }
    return 0;
}
