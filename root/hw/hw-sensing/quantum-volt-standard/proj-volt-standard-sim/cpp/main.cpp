#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct JosephsonParams {
    double beta_c{0.2};      // Parameter Stewart-McCumber
    double omega_rf{1.0};    // Normalized RF frequency
    double i_rf{1.2};        // RF current amplitude
    double dt{0.05};         // Integration time step
    int trans_steps{4000};   // Transient relaxation steps
    int avg_steps{10000};    // Averaging steps
};

struct PhaseState {
    double phi{0.0};
    double v{0.0};
};

class JosephsonSimulator {
public:
    explicit JosephsonSimulator(JosephsonParams params) : params_(params) {}

    [[nodiscard]] double simulate_average_voltage(double i_bias) {
        PhaseState state = current_state_;
        double t = 0.0;

        // Pass transient response using RK4
        for (int step = 0; step < params_.trans_steps; ++step) {
            state = rk4_step(state, t, i_bias);
            t += params_.dt;
        }

        // Accumulate average voltage
        double v_sum = 0.0;
        for (int step = 0; step < params_.avg_steps; ++step) {
            state = rk4_step(state, t, i_bias);
            v_sum += state.v;
            t += params_.dt;
        }

        current_state_ = state; // Preserve state for phase continuity
        return v_sum / params_.avg_steps;
    }

private:
    JosephsonParams params_;
    PhaseState current_state_{};

    [[nodiscard]] PhaseState derivatives(const PhaseState& s, double t, double i_bias) const noexcept {
        double i_total = i_bias + params_.i_rf * std::cos(params_.omega_rf * t);
        double dv_dt = (i_total - std::sin(s.phi) - s.v) / params_.beta_c;
        return PhaseState{ .phi = s.v, .v = dv_dt };
    }

    [[nodiscard]] PhaseState rk4_step(const PhaseState& s, double t, double i_bias) const noexcept {
        const double dt = params_.dt;
        
        auto k1 = derivatives(s, t, i_bias);
        auto k2 = derivatives(PhaseState{s.phi + 0.5 * dt * k1.phi, s.v + 0.5 * dt * k1.v}, t + 0.5 * dt, i_bias);
        auto k3 = derivatives(PhaseState{s.phi + 0.5 * dt * k2.phi, s.v + 0.5 * dt * k2.v}, t + 0.5 * dt, i_bias);
        auto k4 = derivatives(PhaseState{s.phi + dt * k3.phi, s.v + dt * k3.v}, t + dt, i_bias);

        return PhaseState{
            .phi = s.phi + (dt / 6.0) * (k1.phi + 2.0 * k2.phi + 2.0 * k3.phi + k4.phi),
            .v   = s.v   + (dt / 6.0) * (k1.v   + 2.0 * k2.v   + 2.0 * k3.v   + k4.v)
        };
    }
};

int main() {
    JosephsonParams params;
    JosephsonSimulator simulator(params);

    std::cout << "Simulating Shapiro steps for overdamped Josephson Junction (C++20)\n";
    std::cout << std::setw(10) << "i_bias" << std::setw(15) << "<v>" << std::setw(20) << "Step Index (n)" << '\n';
    std::cout << std::string(45, '-') << '\n';

    for (double i_bias = 0.0; i_bias <= 3.0; i_bias += 0.05) {
        double v_avg = simulator.simulate_average_voltage(i_bias);
        double step_n = v_avg / params.omega_rf;

        std::cout << std::fixed << std::setprecision(3)
                  << std::setw(10) << i_bias
                  << std::setw(15) << std::setprecision(5) << v_avg
                  << std::setw(20) << std::setprecision(2) << step_n << '\n';
    }

    return 0;
}
