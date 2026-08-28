#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <stdexcept>

class QuantumHarmonicOscillator {
public:
    QuantumHarmonicOscillator(double grid_limit, std::size_t grid_points)
        : L_(grid_limit), N_(grid_points), h_((2.0 * grid_limit) / (grid_points - 1)) {
        if (grid_points < 10) {
            throw std::invalid_argument("Кількість вузлів сітки повинна бути не менше 10");
        }
        build_grid_and_matrix();
    }

    [[nodiscard]] double grid_step() const noexcept { return h_; }
    [[nodiscard]] const std::vector<double>& grid() const noexcept { return xi_; }

    [[nodiscard]] std::vector<double> compute_eigenvalues(std::size_t num_states) const {
        std::vector<double> eigenvalues(num_states, 0.0);

        for (std::size_t k = 0; k < num_states; ++k) {
            double low = 0.0;
            double high = static_cast<double>(k) + 2.5;

            for (int iter = 0; iter < 60; ++iter) {
                double mid = 0.5 * (low + high);
                std::size_t count = count_negative_eigenvalues(mid);

                if (count <= k) {
                    low = mid;
                } else {
                    high = mid;
                }
            }
            eigenvalues[k] = 0.5 * (low + high);
        }
        return eigenvalues;
    }

private:
    double L_;
    std::size_t N_;
    double h_;
    std::vector<double> xi_;
    std::vector<double> diag_;
    std::vector<double> off_diag_;

    void build_grid_and_matrix() {
        xi_.resize(N_);
        diag_.resize(N_);
        off_diag_.resize(N_ - 1);

        const double h2 = h_ * h_;
        const double off_val = -0.5 / h2;

        for (std::size_t i = 0; i < N_; ++i) {
            xi_[i] = -L_ + static_cast<double>(i) * h_;
            diag_[i] = (1.0 / h2) + 0.5 * (xi_[i] * xi_[i]);
            if (i < N_ - 1) {
                off_diag_[i] = off_val;
            }
        }
    }

    [[nodiscard]] std::size_t count_negative_eigenvalues(double lambda) const noexcept {
        std::size_t count = 0;
        double p = diag_[0] - lambda;
        if (p < 0.0) ++count;

        for (std::size_t i = 1; i < N_; ++i) {
            const double denom = (std::abs(p) < 1e-14) ? 1e-14 : p;
            p = (diag_[i] - lambda) - (off_diag_[i - 1] * off_diag_[i - 1]) / denom;
            if (p < 0.0) ++count;
        }
        return count;
    }
};

int main() {
    try {
        constexpr double L = 5.0;
        constexpr std::size_t N = 1000;

        QuantumHarmonicOscillator qho(L, N);
        const auto energies = qho.compute_eigenvalues(5);

        std::cout << std::fixed << std::setprecision(6);
        std::cout << "Результати C++ моделювання квантового осцилятора:\n";
        std::cout << "=================================================\n";

        for (std::size_t n = 0; n < energies.size(); ++n) {
            const double exact = static_cast<double>(n) + 0.5;
            const double error = std::abs(energies[n] - exact);
            std::cout << "n = " << n << " | E_calc = " << energies[n]
                      << " | E_exact = " << exact
                      << " | Error = " << std::scientific << std::setprecision(2) << error << "\n"
                      << std::fixed << std::setprecision(6);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
