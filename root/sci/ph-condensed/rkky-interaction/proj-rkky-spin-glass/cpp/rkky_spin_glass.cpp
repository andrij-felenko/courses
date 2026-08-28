// rkky_spin_glass.cpp — Моделювання спінового скла РККЙ мовою C++17
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <numeric>
#include <iomanip>
#include <string>

struct SpinSite {
    double x{0.0};
    double y{0.0};
    int spin{1}; // +1 або -1
};

class RKKYSpinGlassSimulation {
private:
    int N_;
    double L_;
    double k_F_;
    double J0_;
    std::vector<SpinSite> sites_;
    std::vector<double> J_matrix_;
    std::mt19937 rng_{std::random_device{}()};

    static double rkky_function(double r, double k_F) {
        const double x = 2.0 * k_F * r;
        if (x < 0.05) return 0.0;
        return (x * std::cos(x) - std::sin(x)) / (x * x * x * x);
    }

public:
    RKKYSpinGlassSimulation(int N, double L, double k_F, double J0)
        : N_(N), L_(L), k_F_(k_F), J0_(J0), sites_(N), J_matrix_(N * N, 0.0) {
        
        std::uniform_real_distribution<double> dist_pos(0.0, L_);
        std::bernoulli_distribution dist_spin(0.5);

        for (auto& site : sites_) {
            site.x = dist_pos(rng_);
            site.y = dist_pos(rng_);
            site.spin = dist_spin(rng_) ? 1 : -1;
        }

        build_interaction_matrix();
    }

    void build_interaction_matrix() {
        int afm_count = 0;
        int fm_count = 0;

        for (int i = 0; i < N_; ++i) {
            for (int j = i + 1; j < N_; ++j) {
                const double dx = sites_[i].x - sites_[j].x;
                const double dy = sites_[i].y - sites_[j].y;
                const double r = std::hypot(dx, dy);

                const double J_val = J0_ * rkky_function(r, k_F_);
                J_matrix_[i * N_ + j] = J_val;
                J_matrix_[j * N_ + i] = J_val;

                if (J_val < 0) afm_count++;
                else if (J_val > 0) fm_count++;
            }
        }

        std::cout << "Побудовано матрицю РККЙ: FM зв'язків = " << fm_count 
                  << ", AFM зв'язків = " << afm_count << "\n\n";
    }

    double calculate_total_energy() const {
        double energy = 0.0;
        for (int i = 0; i < N_; ++i) {
            for (int j = i + 1; j < N_; ++j) {
                energy -= J_matrix_[i * N_ + j] * sites_[i].spin * sites_[j].spin;
            }
        }
        return energy;
    }

    void run_temperature_sweep(double T_start, double T_end, double T_step, int mc_steps) {
        std::uniform_int_distribution<int> dist_site(0, N_ - 1);
        std::uniform_real_distribution<double> dist_prob(0.0, 1.0);
        const double k_B = 0.08617; // меВ/K

        std::cout << std::setw(8) << "T (K)" 
                  << std::setw(18) << "Енергія (меВ)" 
                  << std::setw(22) << "Параметр q_EA"
                  << std::setw(22) << "Фазовий стан\n";
        std::cout << std::string(70, '-') << "\n";

        for (double T = T_start; T >= T_end; T -= T_step) {
            const double beta = 1.0 / (k_B * T);
            std::vector<double> spin_accum(N_, 0.0);
            int samples = 0;

            for (int step = 0; step < mc_steps; ++step) {
                const int idx = dist_site(rng_);

                double dE = 0.0;
                for (int j = 0; j < N_; ++j) {
                    if (idx != j) {
                        dE += 2.0 * J_matrix_[idx * N_ + j] * sites_[idx].spin * sites_[j].spin;
                    }
                }

                if (dE <= 0.0 || dist_prob(rng_) < std::exp(-dE * beta)) {
                    sites_[idx].spin = -sites_[idx].spin;
                }

                if (step >= mc_steps / 2) {
                    for (int i = 0; i < N_; ++i) {
                        spin_accum[i] += sites_[i].spin;
                    }
                    samples++;
                }
            }

            double q_ea = 0.0;
            for (int i = 0; i < N_; ++i) {
                const double avg_s = spin_accum[i] / samples;
                q_ea += avg_s * avg_s;
            }
            q_ea /= N_;

            std::string state = (q_ea < 0.15) ? "Парамагнетик" : 
                                (q_ea < 0.50) ? "Перехідний" : "Спінове скло";

            std::cout << std::fixed << std::setprecision(1) << std::setw(8) << T
                      << std::setprecision(2) << std::setw(18) << calculate_total_energy()
                      << std::setprecision(4) << std::setw(22) << q_ea
                      << std::setw(22) << state << "\n";
        }
    }
};

int main() {
    std::cout << "=== Спінтроніка: Моделювання РККЙ спінового скла (C++17) ===\n\n";

    RKKYSpinGlassSimulation sim(80, 50.0, 1.36, 10.0);
    sim.run_temperature_sweep(15.0, 0.5, 1.0, 3000);

    return 0;
}
