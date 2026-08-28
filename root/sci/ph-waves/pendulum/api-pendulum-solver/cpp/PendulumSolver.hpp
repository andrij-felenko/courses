// PendulumSolver.hpp - Ідіоматична обгортка C++20 з використанням std::expected
#ifndef PENDULUM_SOLVER_HPP
#define PENDULUM_SOLVER_HPP

#include <cmath>
#include <numbers>
#include <expected>
#include <utility>
#include "PendulumTypes.hpp"

namespace physics {

class PendulumEngine {
public:
    explicit PendulumEngine(Config config) noexcept : config_{config} {}

    [[nodiscard]] std::expected<State, Status>
    initialize(double theta0_rad, double omega0_rad_s = 0.0) noexcept {
        if (config_.length <= 0.0 || config_.mass <= 0.0 || config_.gravity < 0.0) {
            return std::unexpected(Status::InvalidParameter);
        }

        current_state_.theta = theta0_rad;
        current_state_.omega = omega0_rad_s;
        current_state_.alpha = compute_alpha(theta0_rad, omega0_rad_s);
        current_state_.time = 0.0;
        current_state_.step_count = 0;

        initial_energy_ = compute_total_energy(current_state_);
        return current_state_;
    }

    [[nodiscard]] std::expected<State, Status>
    step(SolverMode mode, double dt) noexcept {
        if (dt <= 0.0) {
            return std::unexpected(Status::InvalidParameter);
        }

        if (mode == SolverMode::RK4) {
            step_rk4(dt);
        } else if (mode == SolverMode::Verlet) {
            step_verlet(dt);
        } else {
            return std::unexpected(Status::UnsupportedMode);
        }

        current_state_.time += dt;
        current_state_.step_count++;
        current_state_.alpha = compute_alpha(current_state_.theta, current_state_.omega);

        if (std::isnan(current_state_.theta) || std::isinf(current_state_.theta)) {
            return std::unexpected(Status::Divergence);
        }

        return current_state_;
    }

    [[nodiscard]] Metrics metrics() const noexcept {
        Metrics m{};
        double e_kin = 0.5 * config_.mass * config_.length * config_.length * current_state_.omega * current_state_.omega;
        double e_pot = config_.mass * config_.gravity * config_.length * (1.0 - std::cos(current_state_.theta));
        m.kinetic_energy = e_kin;
        m.potential_energy = e_pot;
        m.total_energy = e_kin + e_pot;
        m.initial_energy = initial_energy_;
        m.energy_drift_pct = (initial_energy_ > 1e-12) 
            ? std::abs(m.total_energy - initial_energy_) / initial_energy_ * 100.0 
            : 0.0;
        return m;
    }

    [[nodiscard]] double theoretical_period(double theta0_deg) const noexcept {
        double rad0 = theta0_deg * (std::numbers::pi / 180.0);
        double t0 = 2.0 * std::numbers::pi * std::sqrt(config_.length / config_.gravity);
        double k = std::sin(rad0 / 2.0);
        double k2 = k * k;
        return t0 * (1.0 + 0.25 * k2 + (9.0 / 64.0) * k2 * k2);
    }

private:
    [[nodiscard]] double compute_alpha(double th, double om) const noexcept {
        double damping_torque = config_.damping * om;
        double gravity_torque = config_.mass * config_.gravity * config_.length * std::sin(th);
        double eff_inertia = (config_.inertia > 0.0) ? config_.inertia : (config_.mass * config_.length * config_.length);
        return -(gravity_torque + damping_torque) / eff_inertia;
    }

    [[nodiscard]] double compute_total_energy(const State& s) const noexcept {
        double e_kin = 0.5 * config_.mass * config_.length * config_.length * s.omega * s.omega;
        double e_pot = config_.mass * config_.gravity * config_.length * (1.0 - std::cos(s.theta));
        return e_kin + e_pot;
    }

    void step_rk4(double dt) noexcept {
        auto deriv = [this](double th, double om) {
            return std::pair{om, compute_alpha(th, om)};
        };

        auto [k1_th, k1_om] = deriv(current_state_.theta, current_state_.omega);
        auto [k2_th, k2_om] = deriv(current_state_.theta + 0.5 * dt * k1_th, current_state_.omega + 0.5 * dt * k1_om);
        auto [k3_th, k3_om] = deriv(current_state_.theta + 0.5 * dt * k2_th, current_state_.omega + 0.5 * dt * k2_om);
        auto [k4_th, k4_om] = deriv(current_state_.theta + dt * k3_th, current_state_.omega + dt * k3_om);

        current_state_.theta += (dt / 6.0) * (k1_th + 2.0 * k2_th + 2.0 * k3_th + k4_th);
        current_state_.omega += (dt / 6.0) * (k1_om + 2.0 * k2_om + 2.0 * k3_om + k4_om);
    }

    void step_verlet(double dt) noexcept {
        double a_curr = compute_alpha(current_state_.theta, current_state_.omega);
        current_state_.theta += current_state_.omega * dt + 0.5 * a_curr * dt * dt;
        double a_next = compute_alpha(current_state_.theta, current_state_.omega);
        current_state_.omega += 0.5 * (a_curr + a_next) * dt;
    }

    Config config_;
    State current_state_{};
    double initial_energy_{0.0};
};

} // namespace physics

#endif // PENDULUM_SOLVER_HPP
