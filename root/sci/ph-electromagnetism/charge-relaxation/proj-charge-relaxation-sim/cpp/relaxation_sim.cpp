//
// relaxation_sim.cpp — Програма чисельного моделювання релаксації заряду (Мова C++)
//

#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <iomanip>
#include <algorithm>

constexpr double EPS0 = 8.854187817e-12;

class ChargeRelaxationSolver1D {
public:
    ChargeRelaxationSolver1D(std::size_t grid_points, double domain_length)
        : n_points_(grid_points),
          dx_(domain_length / (grid_points - 1)),
          eps_(grid_points, EPS0),
          sigma_(grid_points, 0.0),
          rho_(grid_points, 0.0),
          potential_(grid_points, 0.0),
          j_current_(grid_points - 1, 0.0) {}

    void set_medium_properties(std::size_t start_idx, std::size_t end_idx, double rel_eps, double conductivity) {
        for (std::size_t i = start_idx; i <= std::min(end_idx, n_points_ - 1); ++i) {
            eps_[i] = rel_eps * EPS0;
            sigma_[i] = conductivity;
        }
    }

    void inject_charge(std::size_t index, double charge_density) {
        if (index < n_points_) {
            rho_[index] = charge_density;
        }
    }

    [[nodiscard]] double compute_safe_timestep(double safety_factor = 0.1) const {
        double min_tau = std::numeric_limits<double>::max();
        for (std::size_t i = 0; i < n_points_; ++i) {
            if (sigma_[i] > 0.0) {
                double tau = eps_[i] / sigma_[i];
                min_tau = std::min(min_tau, tau);
            }
        }
        return safety_factor * min_tau;
    }

    void solve_poisson(double v_left, double v_right, std::size_t max_iterations = 2500) {
        potential_.front() = v_left;
        potential_.back() = v_right;

        const double dx2 = dx_ * dx_;
        for (std::size_t iter = 0; iter < max_iterations; ++iter) {
            for (std::size_t i = 1; i < n_points_ - 1; ++i) {
                double eps_avg = 0.5 * (eps_[i] + eps_[i + 1]);
                potential_[i] = 0.5 * (potential_[i - 1] + potential_[i + 1] + (rho_[i] * dx2) / eps_avg);
            }
        }
    }

    void step_simulation(double dt) {
        // 1. Струм на межах осередків
        for (std::size_t i = 0; i < n_points_ - 1; ++i) {
            double sigma_edge = 0.5 * (sigma_[i] + sigma_[i + 1]);
            double e_field = (potential_[i] - potential_[i + 1]) / dx_;
            j_current_[i] = sigma_edge * e_field;
        }

        // 2. Оновлення густини об'ємного заряду
        for (std::size_t i = 1; i < n_points_ - 1; ++i) {
            double div_j = (j_current_[i] - j_current_[i - 1]) / dx_;
            rho_[i] -= dt * div_j;
        }
    }

    [[nodiscard]] double get_charge_density(std::size_t index) const { return rho_.at(index); }
    [[nodiscard]] double get_potential(std::size_t index) const { return potential_.at(index); }

private:
    std::size_t n_points_;
    double dx_;
    std::vector<double> eps_;
    std::vector<double> sigma_;
    std::vector<double> rho_;
    std::vector<double> potential_;
    std::vector<double> j_current_;
};

int main() {
    constexpr std::size_t N_POINTS = 101;
    constexpr double LENGTH = 0.01; // 1 см

    auto solver = std::make_unique<ChargeRelaxationSolver1D>(N_POINTS, LENGTH);

    // Середовище 1 (ліва половина): εr = 4, σ = 1 мкСм/м
    solver->set_medium_properties(0, N_POINTS / 2, 4.0, 1e-6);

    // Середовище 2 (права половина): εr = 10, σ = 10 мкСм/м
    solver->set_medium_properties(N_POINTS / 2 + 1, N_POINTS - 1, 10.0, 1e-5);

    // Початковий інжектований заряд у центрі лівої зони
    solver->inject_charge(25, 1e-4);

    const double dt = solver->compute_safe_timestep(0.1);

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Розрахунок розгортається з dt = " << dt << " с\n";
    std::cout << "Час (с)\t\tЗаряд вузол 25\tЗаряд межа (вузол 50)\n";

    for (std::size_t step = 0; step <= 100; ++step) {
        solver->solve_poisson(10.0, 0.0);

        if (step % 20 == 0) {
            double current_time = step * dt;
            std::cout << current_time << "\t"
                      << solver->get_charge_density(25) << "\t"
                      << solver->get_charge_density(50) << "\n";
        }

        solver->step_simulation(dt);
    }

    return 0;
}
