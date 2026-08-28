#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct RcsjSimulator {
    double i_ac{0.5};
    double omega{0.6};
    double beta_c{25.0};
    double h{0.02};

    [[nodiscard]] std::pair<double, double> derivatives(double tau, double phi, double v, double i_dc) const noexcept {
        const double gamma = 1.0 / std::sqrt(beta_c);
        return { v, i_dc + i_ac * std::sin(omega * tau) - std::sin(phi) - gamma * v };
    }

    [[nodiscard]] double compute_average_voltage(double i_dc) const {
        const double period = 2.0 * std::numbers::pi / omega;
        const int steps_per_period = static_cast[int](period / h);
        const int transient_steps = steps_per_period * 200;
        const int eval_steps = steps_per_period * 500;

        double tau = 0.0, phi = 0.0, v = 0.0;

        auto rk4_step = [&](double current_i_dc) {
            auto [k1_phi, k1_v] = derivatives(tau, phi, v, current_i_dc);
            auto [k2_phi, k2_v] = derivatives(tau + 0.5 * h, phi + 0.5 * h * k1_phi, v + 0.5 * h * k1_v, current_i_dc);
            auto [k3_phi, k3_v] = derivatives(tau + 0.5 * h, phi + 0.5 * h * k2_phi, v + 0.5 * h * k2_v, current_i_dc);
            auto [k4_phi, k4_v] = derivatives(tau + h, phi + h * k3_phi, v + h * k3_v, current_i_dc);

            phi += (h / 6.0) * (k1_phi + 2.0 * k2_phi + 2.0 * k3_phi + k4_phi);
            v += (h / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v);
            tau += h;
        };

        for (int k = 0; k < transient_steps; ++k) {
            rk4_step(i_dc);
        }

        double v_sum = 0.0;
        for (int k = 0; k < eval_steps; ++k) {
            rk4_step(i_dc);
            v_sum += v;
        }

        return v_sum / eval_steps;
    }
};

int main() {
    RcsjSimulator sim;
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "i_dc\t<v>\tStep index n\n";
    
    for (double i_dc = 0.0; i_dc <= 2.5; i_dc += 0.05) {
        double v_avg = sim.compute_average_voltage(i_dc);
        double step_n = v_avg / sim.omega;
        std::cout << i_dc << "\t" << v_avg << "\t" << step_n << "\n";
    }
    return 0;
}
