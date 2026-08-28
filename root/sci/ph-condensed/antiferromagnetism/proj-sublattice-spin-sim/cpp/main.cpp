// Simulation of 2D Antiferromagnetic Ising Model using Modern C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <numeric>

class AntiferromagneticIsing2D {
public:
    struct MagnetizationResult {
        double m_a;
        double m_b;
        double m_staggered;
        double m_net;
    };

    AntiferromagneticIsing2D(std::size_t size, double coupling_J, double ext_field)
        : L_(size), N_spins_(size * size), J_(coupling_J), H_(ext_field),
          spins_(size, std::vector<int>(size, 1)), rng_(1337)
    {
        init_checkerboard();
    }

    void set_temperature(double T) noexcept { temperature_ = T; }

    void init_checkerboard() {
        for (std::size_t i = 0; i < L_; ++i) {
            for (std::size_t j = 0; j < L_; ++j) {
                spins_[i][j] = ((i + j) % 2 == 0) ? 1 : -1;
            }
        }
    }

    void monte_carlo_sweep() {
        std::uniform_int_distribution<std::size_t> dist_coord(0, L_ - 1);
        std::uniform_real_distribution<double> dist_prob(0.0, 1.0);

        for (std::size_t step = 0; step < N_spins_; ++step) {
            std::size_t r = dist_coord(rng_);
            std::size_t c = dist_coord(rng_);

            int s = spins_[r][c];
            int top    = spins_[(r + L_ - 1) % L_][c];
            int bottom = spins_[(r + 1) % L_][c];
            int left   = spins_[r][(c + L_ - 1) % L_];
            int right  = spins_[r][(c + 1) % L_];

            int neighbor_sum = top + bottom + left + right;
            double dE = 2.0 * s * (J_ * neighbor_sum + H_);

            if (dE <= 0.0 || dist_prob(rng_) < std::exp(-dE / temperature_)) {
                spins_[r][c] = -s;
            }
        }
    }

    [[nodiscard]] MagnetizationResult measure() const noexcept {
        double sum_a = 0.0;
        double sum_b = 0.0;

        for (std::size_t i = 0; i < L_; ++i) {
            for (std::size_t j = 0; j < L_; ++j) {
                if ((i + j) % 2 == 0) {
                    sum_a += spins_[i][j];
                } else {
                    sum_b += spins_[i][j];
                }
            }
        }

        double m_a = sum_a / (N_spins_ / 2.0);
        double m_b = sum_b / (N_spins_ / 2.0);
        return {
            .m_a = m_a,
            .m_b = m_b,
            .m_staggered = std::abs(m_a - m_b) / 2.0,
            .m_net = std::abs(sum_a + sum_b) / static_cast<double>(N_spins_)
        };
    }

private:
    std::size_t L_;
    std::size_t N_spins_;
    double J_;
    double H_;
    double temperature_{1.0};
    std::vector<std::vector<int>> spins_;
    mutable std::mt19937 rng_;
};

int main() {
    constexpr std::size_t L = 40;
    constexpr double J = -1.0; // Antiferromagnetic coupling (J < 0)
    constexpr double H = 0.0;
    constexpr int therm_sweeps = 1000;
    constexpr int mc_sweeps = 5000;

    AntiferromagneticIsing2D model(L, J, H);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Temp\tM_A\tM_B\tM_staggered\tM_net\n";
    std::cout << "---------------------------------------------------\n";

    for (double T = 0.4; T <= 4.0; T += 0.2) {
        model.set_temperature(T);
        model.init_checkerboard();

        // Thermalization sweeps
        for (int s = 0; s < therm_sweeps; ++s) {
            model.monte_carlo_sweep();
        }

        // Sampling sweeps
        double acc_ma = 0.0, acc_mb = 0.0, acc_mstag = 0.0, acc_mnet = 0.0;
        for (int s = 0; s < mc_sweeps; ++s) {
            model.monte_carlo_sweep();
            auto res = model.measure();
            acc_ma += res.m_a;
            acc_mb += res.m_b;
            acc_mstag += res.m_staggered;
            acc_mnet += res.m_net;
        }

        std::cout << T << "\t"
                  << (acc_ma / mc_sweeps) << "\t"
                  << (acc_mb / mc_sweeps) << "\t"
                  << (acc_mstag / mc_sweeps) << "\t\t"
                  << (acc_mnet / mc_sweeps) << "\n";
    }

    return 0;
}
