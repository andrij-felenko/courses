// Haynes-Shockley 1D Drift-Diffusion Simulator (C++20)
// Об'єктно-орієнтований розв'язувач із використанням RAII та std::vector

#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <algorithm>
#include <numbers>

struct SimParams {
    double length_cm{1.0};
    std::size_t num_points{500};
    double E_field{20.0};       // В/см
    double mu_p{1900.0};        // см²/В·с
    double D_p{49.0};           // см²/с
    double tau_p{50e-6};        // с
    double total_time_s{200e-6}; // с
};

class HaynesShockleySolver {
public:
    explicit HaynesShockleySolver(SimParams params)
        : p_{params},
          dx_{p_.length_cm / static_cast<double>(p_.num_points - 1)},
          v_drift_{p_.mu_p * p_.E_field},
          u_curr_(p_.num_points, 0.0),
          u_next_(p_.num_points, 0.0)
    {
        calculate_timestep();
        initialize_packet(0.1, 0.01, 1e12);
    }

    void solve() {
        const std::size_t num_steps = static_cast<std::size_t>(p_.total_time_s / dt_);
        const std::size_t print_interval = num_steps / 4;

        std::cout << "--- Початок симуляції Гейнса-Шоклі (C++20) ---\n";
        std::cout << "Параметри: L = " << p_.length_cm << " см, E = " << p_.E_field << " В/см\n";
        std::cout << "Сітка: " << p_.num_points << " вузлів, dx = " 
                  << std::scientific << dx_ << " см, dt = " << dt_ << " с\n\n";

        for (std::size_t step = 0; step <= num_steps; ++step) {
            double t = static_cast<double>(step) * dt_;

            if (step % print_interval == 0 || step == num_steps) {
                report_status(t);
            }

            // Крок оновлення FDTD
            for (std::size_t i = 1; i < p_.num_points - 1; ++i) {
                double diff = p_.D_p * (u_curr_[i+1] - 2.0 * u_curr_[i] + u_curr_[i-1]) / (dx_ * dx_);
                double adv = v_drift_ * (u_curr_[i] - u_curr_[i-1]) / dx_;
                double recomp = u_curr_[i] / p_.tau_p;

                u_next_[i] = u_curr_[i] + dt_ * (diff - adv - recomp);
            }

            // Граничні умови
            u_next_.front() = 0.0;
            u_next_.back() = 0.0;

            u_curr_.swap(u_next_);
        }
    }

private:
    void calculate_timestep() {
        double dt_diff = (dx_ * dx_) / (2.0 * p_.D_p);
        double dt_adv = (v_drift_ > 0.0) ? (dx_ / v_drift_) : 1e9;
        dt_ = 0.4 * std::min(dt_diff, dt_adv);
    }

    void initialize_packet(double x_inject, double sigma_0, double N0) {
        for (std::size_t i = 0; i < p_.num_points; ++i) {
            double x = static_cast<double>(i) * dx_;
            double arg = (x - x_inject) / sigma_0;
            u_curr_[i] = (N0 / (std::sqrt(2.0 * std::numbers::pi) * sigma_0)) * std::exp(-0.5 * arg * arg);
        }
    }

    void report_status(double t) const {
        auto max_it = std::max_element(u_curr_.begin(), u_curr_.end());
        std::size_t idx = static_cast<std::size_t>(std::distance(u_curr_.begin(), max_it));
        double x_peak = static_cast<double>(idx) * dx_;
        double total_charge = std::accumulate(u_curr_.begin(), u_curr_.end(), 0.0) * dx_;

        std::cout << "t = " << std::setw(6) << std::fixed << std::setprecision(2) << t * 1e6 << " мкс | "
                  << "x_peak = " << std::setw(5) << std::setprecision(3) << x_peak << " см | "
                  << "Max conc = " << std::scientific << std::setprecision(2) << *max_it << " cm⁻³ | "
                  << "Total = " << total_charge << "\n";
    }

    SimParams p_;
    double dx_;
    double v_drift_;
    double dt_{0.0};
    std::vector<double> u_curr_;
    std::vector<double> u_next_;
};

int main() {
    SimParams params;
    HaynesShockleySolver solver(params);
    solver.solve();
    return 0;
}
