// thermal_expansion_sim.cpp — Моделювання теплового розширення 1D кристала (C++20)
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <numbers>

class CrystalSimulator {
public:
    struct Config {
        std::size_t num_atoms{50};
        double dt{0.002};
        std::size_t total_steps{200000};
        std::size_t thermalization_steps{50000};
        double mass{1.0};
        double epsilon{1.0};
        double sigma{1.0};
        double gamma{1.0};
    };

    explicit CrystalSimulator(Config cfg) 
        : cfg_(cfg),
          r0_(std::pow(2.0, 1.0 / 6.0) * cfg_.sigma),
          positions_(cfg_.num_atoms),
          velocities_(cfg_.num_atoms, 0.0),
          forces_(cfg_.num_atoms, 0.0),
          gen_(12345)
    {
        for (std::size_t i = 0; i < cfg_.num_atoms; ++i) {
            positions_[i] = i * r0_;
        }
    }

    double run_temperature(double target_temp) {
        std::normal_distribution<double> gaussian{0.0, 1.0};
        double noise_std = std::sqrt(2.0 * cfg_.gamma * cfg_.mass * target_temp / cfg_.dt);

        compute_forces();

        double sum_length = 0.0;
        std::size_t count = 0;

        for (std::size_t step = 0; step < cfg_.total_steps; ++step) {
            for (std::size_t i = 0; i < cfg_.num_atoms; ++i) {
                double R_i = noise_std * gaussian(gen_);
                velocities_[i] += 0.5 * cfg_.dt * (forces_[i] - cfg_.gamma * velocities_[i] + R_i) / cfg_.mass;
                positions_[i] += cfg_.dt * velocities_[i];
            }

            compute_forces();

            for (std::size_t i = 0; i < cfg_.num_atoms; ++i) {
                double R_i = noise_std * gaussian(gen_);
                velocities_[i] += 0.5 * cfg_.dt * (forces_[i] - cfg_.gamma * velocities_[i] + R_i) / cfg_.mass;
            }

            if (step >= cfg_.thermalization_steps) {
                double current_len = positions_.back() - positions_.front();
                sum_length += current_len;
                count++;
            }
        }

        return sum_length / static_cast<double>(count);
    }

    [[nodiscard]] double initial_length() const noexcept {
        return (cfg_.num_atoms - 1) * r0_;
    }

private:
    void compute_forces() {
        std::fill(forces_.begin(), forces_.end(), 0.0);
        for (std::size_t i = 0; i < cfg_.num_atoms - 1; ++i) {
            double r = positions_[i+1] - positions_[i];
            if (r < 0.1) r = 0.1;
            double sr = cfg_.sigma / r;
            double sr6 = std::pow(sr, 6);
            double sr12 = sr6 * sr6;
            double force = (24.0 * cfg_.epsilon / r) * (2.0 * sr12 - sr6);
            forces_[i] -= force;
            forces_[i+1] += force;
        }
    }

    Config cfg_;
    double r0_;
    std::vector<double> positions_;
    std::vector<double> velocities_;
    std::vector<double> forces_;
    std::mt19937 gen_;
};

int main() {
    CrystalSimulator::Config cfg;
    CrystalSimulator sim(cfg);
    double L0 = sim.initial_length();

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Т, К (безрозмірні) | Середня довжина | ΔL / L₀ (%)\n";
    std::cout << "-----------------------------------------------\n";

    const std::vector<double> temperatures{0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30};
    for (double T : temperatures) {
        double avg_l = sim.run_temperature(T);
        double pct = ((avg_l - L0) / L0) * 100.0;
        std::cout << "      " << T << "        |    " << avg_l << "     |   +" << pct << " %\n";
    }

    return 0;
}
