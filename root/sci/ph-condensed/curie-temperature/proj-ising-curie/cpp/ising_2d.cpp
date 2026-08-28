/*
 * ising_2d.cpp — Об'єктно-орієнтована високопродуктивна симуляція (C++17)
 * Використовує std::vector, швидкий випадковий генератор std::mt19937_64 та RAII.
 */

#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <cstdint>
#include <array>

class IsingLattice2D {
private:
    int L_;
    int N_;
    double J_;
    std::vector<int8_t> spin_;
    std::mt19937_64 rng_;
    std::uniform_real_distribution<double> dist_real_{0.0, 1.0};
    std::uniform_int_distribution<int> dist_coord_;
    std::array<double, 9> boltzmann_lut_{};

    [[nodiscard]] inline int pbc(int coord) const noexcept {
        if (coord < 0) return coord + L_;
        if (coord >= L_) return coord - L_;
        return coord;
    }

    [[nodiscard]] inline int idx(int r, int c) const noexcept {
        return r * L_ + c;
    }

public:
    explicit IsingLattice2D(int L, double J = 1.0)
        : L_(L), N_(L * L), J_(J), spin_(L * L),
          rng_(std::random_device{}()), dist_coord_(0, L - 1) {
        randomize();
    }

    void randomize() {
        std::uniform_int_distribution<int> dist_spin(0, 1);
        for (int i = 0; i < N_; ++i) {
            spin_[i] = dist_spin(rng_) ? 1 : -1;
        }
    }

    void set_temperature(double T) noexcept {
        // Заповнення таблиці Больцмана для dE = 2 * J * s * sum (dE може бути 4 або 8)
        boltzmann_lut_[4] = std::exp(-4.0 * J_ / T);
        boltzmann_lut_[8] = std::exp(-8.0 * J_ / T);
    }

    void monte_carlo_step() noexcept {
        for (int i = 0; i < N_; ++i) {
            int r = dist_coord_(rng_);
            int c = dist_coord_(rng_);
            int s = spin_[idx(r, c)];

            int sum_neighbors = spin_[idx(pbc(r - 1), c)] +
                                spin_[idx(pbc(r + 1), c)] +
                                spin_[idx(r, pbc(c - 1))] +
                                spin_[idx(r, pbc(c + 1))];
            int dE = 2 * s * sum_neighbors;

            if (dE <= 0 || dist_real_(rng_) < boltzmann_lut_[dE]) {
                spin_[idx(r, c)] = static_cast<int8_t>(-s);
            }
        }
    }

    [[nodiscard]] double total_magnetization() const noexcept {
        int64_t sum = 0;
        for (int i = 0; i < N_; ++i) {
            sum += spin_[i];
        }
        return static_cast<double>(sum);
    }

    [[nodiscard]] double total_energy() const noexcept {
        double energy = 0.0;
        for (int r = 0; r < L_; ++r) {
            for (int c = 0; c < L_; ++c) {
                int s = spin_[idx(r, c)];
                int sum_neighbors = spin_[idx(pbc(r + 1), c)] + spin_[idx(r, pbc(c + 1))];
                energy -= J_ * s * sum_neighbors;
            }
        }
        return energy;
    }

    [[nodiscard]] int size() const noexcept { return N_; }
};

struct ThermodynamicStats {
    double avg_m;
    double susceptibility;
    double heat_capacity;
};

ThermodynamicStats run_temperature_point(IsingLattice2D& lattice, double T, int thermal_mcs, int sample_mcs) {
    lattice.randomize();
    lattice.set_temperature(T);

    // 1. Термалізація
    for (int mcs = 0; mcs < thermal_mcs; ++mcs) {
        lattice.monte_carlo_step();
    }

    // 2. Збір статистичних даних
    double sum_m = 0.0, sum_m2 = 0.0;
    double sum_e = 0.0, sum_e2 = 0.0;
    const double n_spins = static_cast<double>(lattice.size());

    for (int mcs = 0; mcs < sample_mcs; ++mcs) {
        lattice.monte_carlo_step();

        double m_val = std::abs(lattice.total_magnetization()) / n_spins;
        double e_val = lattice.total_energy() / n_spins;

        sum_m += m_val;
        sum_m2 += m_val * m_val;
        sum_e += e_val;
        sum_e2 += e_val * e_val;
    }

    double avg_m = sum_m / sample_mcs;
    double avg_m2 = sum_m2 / sample_mcs;
    double avg_e = sum_e / sample_mcs;
    double avg_e2 = sum_e2 / sample_mcs;

    double chi = (n_spins / T) * (avg_m2 - avg_m * avg_m);
    double cp = (n_spins / (T * T)) * (avg_e2 - avg_e * avg_e);

    return {avg_m, chi, cp};
}

int main() {
    constexpr int grid_l = 32;
    IsingLattice2D lattice(grid_l);

    std::cout << "===============================================================\n"
              << " 2D Ising Monte Carlo Simulation (Modern C++17)\n"
              << " Lattice: " << grid_l << "x" << grid_l << " (" << lattice.size() << " spins)\n"
              << " Analytical Tc = " << 2.0 / std::log(1.0 + std::sqrt(2.0)) << " J/kB\n"
              << "===============================================================\n\n";

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "  Temp(T) |   <|M|>   |  Chi (Susc)  |   Cp (Heat)  | Notes\n";
    std::cout << "---------------------------------------------------------------\n";

    for (double T = 1.2; T <= 3.41; T += 0.1) {
        auto [m, chi, cp] = run_temperature_point(lattice, T, 3000, 3000);

        std::cout << "  " << std::setw(6) << T << "  |  "
                  << std::setw(8) << m << " |  "
                  << std::setw(11) << chi << " |  "
                  << std::setw(11) << cp << " | ";

        if (std::abs(T - 2.27) < 0.05) {
            std::cout << "<-- Critical Curie Point Tc";
        }
        std::cout << "\n";
    }

    return 0;
}
