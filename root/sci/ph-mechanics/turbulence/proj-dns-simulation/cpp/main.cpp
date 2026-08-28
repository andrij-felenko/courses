// DNS 2D Turbulence Spectral Solver (C++20, RAII, Modern Idioms)
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span >
#include <memory>

using dcomplex = std::complex<double>;

class TurbulenceSolver2D {
public:
    TurbulenceSolver2D(std::size_t grid_size, double viscosity, double time_step)
        : N_(grid_size),
          L_(2.0 * std::numbers::pi),
          nu_(viscosity),
          dt_(time_step),
          omega_(grid_size * grid_size, 0.0),
          omega_hat_(grid_size * grid_size, dcomplex{0.0, 0.0}) {
        init_vortex_field();
    }

    void step() {
        const double k_max_trunc = (2.0 / 3.0) * (static_cast<double>(N_) / 2.0);

        for (std::size_t ky = 0; ky < N_; ++ky) {
            int iky = (ky <= N_ / 2) ? static_cast<int>(ky) : static_cast<int>(ky) - static_cast<int>(N_);
            for (std::size_t kx = 0; kx < N_; ++kx) {
                int ikx = (kx <= N_ / 2) ? static_cast<int>(kx) : static_cast<int>(kx) - static_cast<int>(N_);
                double k2 = ikx * ikx + iky * iky;
                std::size_t idx = ky * N_ + kx;

                // 2/3 Rule De-aliasing & Exact Viscous Integrating Factor
                if (std::sqrt(k2) > k_max_trunc) {
                    omega_hat_[idx] = dcomplex{0.0, 0.0};
                } else {
                    double decay = std::exp(-nu_ * k2 * dt_);
                    omega_hat_[idx] *= decay;
                }
            }
        }
    }

    [[nodiscard]] double enstrophy() const noexcept {
        double sum = 0.0;
        for (double val : omega_) {
            sum += val * val;
        }
        return 0.5 * sum / static_cast<double>(omega_.size());
    }

    [[nodiscard]] std::size_t grid_size() const noexcept { return N_; }

private:
    void init_vortex_field() {
        for (std::size_t y = 0; y < N_; ++y) {
            double py = y * L_ / static_cast<double>(N_);
            for (std::size_t x = 0; x < N_; ++x) {
                double px = x * L_ / static_cast<double>(N_);
                omega_[y * N_ + x] = std::sin(4.0 * px) * std::cos(4.0 * py) - std::cos(2.0 * px) * std::sin(2.0 * py);
            }
        }
        dft_2d_transform(omega_, omega_hat_, true);
    }

    void dft_2d_transform(std::span<const double> in, std::span<dcomplex> out, bool forward) const {
        const double sign = forward ? -1.0 : 1.0;
        const double norm = forward ? 1.0 : (1.0 / static_cast<double>(N_ * N_));

        for (std::size_t ky = 0; ky < N_; ++ky) {
            for (std::size_t kx = 0; kx < N_; ++kx) {
                dcomplex sum{0.0, 0.0};
                for (std::size_t y = 0; y < N_; ++y) {
                    for (std::size_t x = 0; x < N_; ++x) {
                        double angle = sign * 2.0 * std::numbers::pi * 
                            (static_cast<double>(kx * x + ky * y)) / static_cast<double>(N_);
                        sum += in[y * N_ + x] * std::polar(1.0, angle);
                    }
                }
                out[ky * N_ + kx] = sum * norm;
            }
        }
    }

    std::size_t N_;
    double L_;
    double nu_;
    double dt_;
    std::vector<double> omega_;
    std::vector<dcomplex> omega_hat_;
};

int main() {
    constexpr std::size_t N = 32;
    TurbulenceSolver2D solver(N, 0.001, 0.01);

    std::cout << "Розпочато C++20 DNS моделювання 2D турбулентності (N=" << N << ")...\n";

    for (int step = 0; step <= 100; step += 20) {
        std::cout << "Крок " << step << " | Енстрофія потоку: " << solver.enstrophy() << '\n';
        for (int sub = 0; sub < 20; ++sub) {
            solver.step();
        }
    }

    return 0;
}
