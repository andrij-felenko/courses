#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <array>
#include <numeric>
#include <iomanip>

class IsingSimulation {
public:
    IsingSimulation(std::size_t lattice_size, double J_coupling, double temperature)
        : L_(lattice_size), N_(lattice_size * lattice_size), J_(J_coupling), T_(temperature),
          beta_(1.0 / temperature), rng_(std::random_device{}()), dist_unif_(0.0, 1.0),
          dist_grid_(0, lattice_size - 1), spins_(N_, 1) {
        
        precompute_lookup_table();
        initialize_lattice();
    }

    void run_sweep() {
        for (std::size_t i = 0; i < N_; ++i) {
            std::size_t r = dist_grid_(rng_);
            std::size_t c = dist_grid_(rng_);
            
            int s = spin_at(r, c);
            int sum_nn = spin_at(prev(r), c) + spin_at(next(r), c) +
                         spin_at(r, prev(c)) + spin_at(r, next(c));
            
            int dE = 2 * static_cast<int>(J_) * s * sum_nn;
            int idx = (dE / 4) + 2;

            if (dE <= 0 || dist_unif_(rng_) < exp_table_[idx]) {
                set_spin_at(r, c, -s);
                total_energy_ += dE;
                total_magnetization_ += (-2 * s);
            }
        }
    }

    [[nodiscard]] double mean_magnetization() const noexcept {
        return std::abs(static_cast<double>(total_magnetization_)) / static_cast<double>(N_);
    }

    [[nodiscard]] double mean_energy() const noexcept {
        return static_cast<double>(total_energy_) / static_cast<double>(N_);
    }

private:
    std::size_t L_;
    std::size_t N_;
    double J_;
    double T_;
    double beta_;

    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_unif_;
    std::uniform_int_distribution<std::size_t> dist_grid_;

    std::vector<int> spins_;
    std::array<double, 5> exp_table_{};
    long long total_energy_{0};
    long long total_magnetization_{0};

    [[nodiscard]] inline std::size_t next(std::size_t idx) const noexcept {
        return (idx + 1 == L_) ? 0 : idx + 1;
    }

    [[nodiscard]] inline std::size_t prev(std::size_t idx) const noexcept {
        return (idx == 0) ? L_ - 1 : idx - 1;
    }

    [[nodiscard]] inline int spin_at(std::size_t r, std::size_t c) const noexcept {
        return spins_[r * L_ + c];
    }

    inline void set_spin_at(std::size_t r, std::size_t c, int val) noexcept {
        spins_[r * L_ + c] = val;
    }

    void precompute_lookup_table() {
        for (int k = -2; k <= 2; ++k) {
            double dE = 4.0 * J_ * k;
            exp_table_[k + 2] = (dE <= 0) ? 1.0 : std::exp(-beta_ * dE);
        }
    }

    void initialize_lattice() {
        std::bernoulli_distribution dist_spin(0.5);
        total_magnetization_ = 0;

        for (std::size_t r = 0; r < L_; ++r) {
            for (std::size_t c = 0; c < L_; ++c) {
                int val = dist_spin(rng_) ? 1 : -1;
                set_spin_at(r, c, val);
                total_magnetization_ += val;
            }
        }

        total_energy_ = 0;
        for (std::size_t r = 0; r < L_; ++r) {
            for (std::size_t c = 0; c < L_; ++c) {
                int s = spin_at(r, c);
                int sum_nn = spin_at(next(r), c) + spin_at(r, next(c));
                total_energy_ -= static_cast<long long>(J_) * s * sum_nn;
            }
        }
    }
};

int main() {
    constexpr std::size_t lattice_size = 64;
    constexpr double temp_crit = 2.269185;

    IsingSimulation sim(lattice_size, 1.0, temp_crit);

    // Thermalization phase (burn-in)
    constexpr std::size_t burn_in_sweeps = 10'000;
    for (std::size_t i = 0; i < burn_in_sweeps; ++i) {
        sim.run_sweep();
    }

    // Production measurement phase
    constexpr std::size_t sample_sweeps = 5'000;
    double sum_m = 0.0;
    double sum_m2 = 0.0;

    for (std::size_t s = 0; s < sample_sweeps; ++s) {
        sim.run_sweep();
        double m = sim.mean_magnetization();
        sum_m += m;
        sum_m2 += m * m;
    }

    double avg_m = sum_m / sample_sweeps;
    double avg_m2 = sum_m2 / sample_sweeps;
    double susceptibility = (avg_m2 - avg_m * avg_m) * (lattice_size * lattice_size) / temp_crit;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== 2D Ising Model Simulation (C++17) ===\n";
    std::cout << "Lattice Size: " << lattice_size << "x" << lattice_size << "\n";
    std::cout << "Temperature T: " << temp_crit << "\n";
    std::cout << "Mean Magnetization <|m|>: " << avg_m << "\n";
    std::cout << "Magnetic Susceptibility:   " << susceptibility << "\n";

    return 0;
}
