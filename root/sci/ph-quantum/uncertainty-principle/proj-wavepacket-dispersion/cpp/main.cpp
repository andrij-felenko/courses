// cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>

class WavepacketSolver {
public:
    using Complex = std::complex<double>;

    struct StateStats {
        double norm{0.0};
        double mean_x{0.0};
        double sigma_x{0.0};
    };

    WavepacketSolver(int grid_size, double x_min, double x_max, double sigma0, double k0)
        : n_(grid_size), x_min_(x_min), x_max_(x_max), dx_((x_max - x_min) / (grid_size - 1)),
          psi_(grid_size) {
        init_gaussian(sigma0, k0);
    }

    StateStats stats() const {
        double norm = 0.0;
        double mean_x = 0.0;
        double var_x = 0.0;

        for (int i = 0; i < n_; ++i) {
            double prob = std::norm(psi_[i]);
            double x = x_min_ + i * dx_;
            norm += prob * dx_;
            mean_x += x * prob * dx_;
        }

        if (norm > 0.0) {
            mean_x /= norm;
            for (int i = 0; i < n_; ++i) {
                double prob = std::norm(psi_[i]);
                double x = x_min_ + i * dx_;
                var_x += (x - mean_x) * (x - mean_x) * prob * dx_;
            }
            var_x /= norm;
        }

        return {norm, mean_x, std::sqrt(var_x)};
    }

    void step_crank_nicolson(double dt, double hbar = 1.0, double mass = 1.0) {
        const double alpha = hbar * dt / (4.0 * mass * dx_ * dx_);
        const Complex diag_main = 1.0 + Complex(0, 2.0 * alpha);
        const Complex diag_off = Complex(0, -alpha);

        std::vector<Complex> rhs(n_, 0.0);
        for (int i = 1; i < n_ - 1; ++i) {
            rhs[i] = (1.0 - Complex(0, 2.0 * alpha)) * psi_[i]
                   + Complex(0, alpha) * (psi_[i - 1] + psi_[i + 1]);
        }

        // Застосування методу прогонки Томаса
        std::vector<Complex> c_prime(n_, 0.0);
        std::vector<Complex> d_prime(n_, 0.0);

        c_prime[0] = diag_off / diag_main;
        d_prime[0] = rhs[0] / diag_main;

        for (int i = 1; i < n_; ++i) {
            Complex denom = diag_main - diag_off * c_prime[i - 1];
            c_prime[i] = diag_off / denom;
            d_prime[i] = (rhs[i] - diag_off * d_prime[i - 1]) / denom;
        }

        psi_[n_ - 1] = d_prime[n_ - 1];
        for (int i = n_ - 2; i >= 0; --i) {
            psi_[i] = d_prime[i] - c_prime[i] * psi_[i + 1];
        }
    }

private:
    void init_gaussian(double sigma0, double k0) {
        const double norm_factor = 1.0 / std::pow(2.0 * std::numbers::pi * sigma0 * sigma0, 0.25);
        for (int i = 0; i < n_; ++i) {
            double x = x_min_ + i * dx_;
            psi_[i] = norm_factor * std::exp(-x * x / (4.0 * sigma0 * sigma0))
                    * std::exp(Complex(0, k0 * x));
        }
    }

    int n_;
    double x_min_, x_max_, dx_;
    std::vector<Complex> psi_;
};

int main() {
    WavepacketSolver solver(400, -20.0, 20.0, 1.0, 2.0);

    std::cout << "Крок\tНорма\t\tСереднє X\tШирина sigma(t)\n";
    for (int step = 0; step <= 200; ++step) {
        if (step % 40 == 0) {
            auto [norm, mean_x, sigma_x] = solver.stats();
            std::cout << step << "\t" << norm << "\t" << mean_x << "\t\t" << sigma_x << "\n";
        }
        solver.step_crank_nicolson(0.01);
    }
    return 0;
}
