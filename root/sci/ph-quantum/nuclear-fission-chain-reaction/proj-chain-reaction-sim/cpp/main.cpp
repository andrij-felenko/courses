#include <iostream>
#include <vector>
#include <array>
#include <numeric>
#include <iomanip>

constexpr std::size_t NUM_GROUPS = 6;

struct ReactorParams {
    std::array<double, NUM_GROUPS> beta{0.000215, 0.001424, 0.001274, 0.002568, 0.000748, 0.000273};
    std::array<double, NUM_GROUPS> lambda{0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01};
    double beta_total{0.0065};
    double l_star{1e-4};
};

struct ReactorState {
    double n{1.0};
    std::array<double, NUM_GROUPS> C{};

    ReactorState operator*(double factor) const {
        ReactorState res;
        res.n = n * factor;
        for (std::size_t i = 0; i < NUM_GROUPS; ++i) {
            res.C[i] = C[i] * factor;
        }
        return res;
    }

    ReactorState operator+(const ReactorState& rhs) const {
        ReactorState res;
        res.n = n + rhs.n;
        for (std::size_t i = 0; i < NUM_GROUPS; ++i) {
            res.C[i] = C[i] + rhs.C[i];
        }
        return res;
    }
};

class ReactorKineticsSimulator {
public:
    explicit ReactorKineticsSimulator(ReactorParams params) 
        : params_(std::move(params)) 
    {
        initialize_equilibrium();
    }

    void initialize_equilibrium() {
        state_.n = 1.0;
        for (std::size_t i = 0; i < NUM_GROUPS; ++i) {
            state_.C[i] = (params_.beta[i] / (params_.l_star * params_.lambda[i])) * state_.n;
        }
    }

    [[nodiscard]] ReactorState compute_derivatives(const ReactorState& s, double rho) const {
        ReactorState deriv;
        double sum_lambda_C = 0.0;
        for (std::size_t i = 0; i < NUM_GROUPS; ++i) {
            sum_lambda_C += params_.lambda[i] * s.C[i];
        }

        deriv.n = ((rho - params_.beta_total) / params_.l_star) * s.n + sum_lambda_C;
        for (std::size_t i = 0; i < NUM_GROUPS; ++i) {
            deriv.C[i] = (params_.beta[i] / params_.l_star) * s.n - params_.lambda[i] * s.C[i];
        }
        return deriv;
    }

    void step_rk4(double rho, double dt) {
        const auto k1 = compute_derivatives(state_, rho);
        const auto k2 = compute_derivatives(state_ + k1 * (0.5 * dt), rho);
        const auto k3 = compute_derivatives(state_ + k2 * (0.5 * dt), rho);
        const auto k4 = compute_derivatives(state_ + k3 * dt, rho);

        state_ = state_ + (k1 + k2 * 2.0 + k3 * 2.0 + k4) * (dt / 6.0);
    }

    [[nodiscard]] double power() const noexcept { return state_.n; }

private:
    ReactorParams params_;
    ReactorState state_;
};

int main() {
    ReactorParams params;
    ReactorKineticsSimulator simulator(params);

    const double dt = 0.001;
    const double t_max = 5.0;
    const double step_reactivity = 0.002; /* rho < beta */

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Час [с]\tПотужність n(t)\tПеріод T [с]\n";
    std::cout << "----------------------------------------\n";

    double prev_power = simulator.power();
    for (double t = 0.0; t <= t_max; t += dt) {
        if (static_cast<int>(t / dt) % 500 == 0) {
            double current_power = simulator.power();
            double dn_dt = (current_power - prev_power) / dt;
            double period = (dn_dt > 1e-9) ? (current_power / dn_dt) : 999.9;
            std::cout << std::setw(6) << t << "\t" 
                      << std::setw(10) << current_power << "\t" 
                      << std::setw(10) << period << "\n";
        }
        prev_power = simulator.power();
        simulator.step_rk4(step_reactivity, dt);
    }

    return 0;
}
