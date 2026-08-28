// 1D FDTD Simulation of Maxwell's Equations using Modern C++ (C++20)
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <memory>

class FdtdSolver1D {
public:
    struct Config {
        std::size_t grid_size{400};
        std::size_t time_steps{600};
        double dx{1e-3};           // 1 мм
        double courant_factor{0.99};
    };

    explicit FdtdSolver1D(Config config)
        : cfg_(config),
          c0_(1.0 / std::sqrt(eps0_ * mu0_)),
          dt_(cfg_.courant_factor * cfg_.dx / c0_),
          Ez_(cfg_.grid_size, 0.0),
          Hy_(cfg_.grid_size - 1, 0.0)
    {
        ce_ = dt_ / (eps0_ * cfg_.dx);
        ch_ = dt_ / (mu0_ * cfg_.dx);
        abc_coef_ = (c0_ * dt_ - cfg_.dx) / (c0_ * dt_ + cfg_.dx);
    }

    void run_simulation() {
        const std::size_t src_pos = cfg_.grid_size / 2;
        const double t0 = 40.0 * dt_;
        const double tau = 12.0 * dt_;

        for (std::size_t n = 0; n < cfg_.time_steps; ++n) {
            // 1. Оновлення магнітного поля Hy
            for (std::size_t i = 0; i < Hy_.size(); ++i) {
                Hy_[i] += ch_ * (Ez_[i + 1] - Ez_[i]);
            }

            const double ez_left_prev = Ez_[1];
            const double ez_right_prev = Ez_[cfg_.grid_size - 2];

            // 2. Оновлення електричного поля Ez
            for (std::size_t i = 1; i < cfg_.grid_size - 1; ++i) {
                Ez_[i] += ce_ * (Hy_[i] - Hy_[i - 1]);
            }

            // 3. Додавання м'якого джерела випромінювання (Gaussian pulse)
            const double current_time = static_cast<double>(n) * dt_;
            const double pulse = std::exp(-std::pow((current_time - t0) / tau, 2.0));
            Ez_[src_pos] += pulse;

            // 4. Застосування межевих умов Mur ABC
            Ez_[0] = ez_left_prev + abc_coef_ * (Ez_[1] - Ez_[0]);
            Ez_[cfg_.grid_size - 1] = ez_right_prev + abc_coef_ * (Ez_[cfg_.grid_size - 2] - Ez_[cfg_.grid_size - 1]);

            if (n % 100 == 0) {
                std::cout << "Крок " << n << " / " << cfg_.time_steps
                          << " | E_max = " << Ez_[src_pos] << "\n";
            }
        }
    }

    [[nodiscard]] const std::vector<double>& get_electric_field() const noexcept {
        return Ez_;
    }

private:
    static constexpr double eps0_{8.854187817e-12};
    static constexpr double mu0_{1.256637061e-6};

    Config cfg_;
    double c0_;
    double dt_;
    double ce_{0.0};
    double ch_{0.0};
    double abc_coef_{0.0};

    std::vector<double> Ez_;
    std::vector<double> Hy_;
};

int main() {
    FdtdSolver1D::Config config{.grid_size = 400, .time_steps = 600, .dx = 1e-3, .courant_factor = 0.99};
    FdtdSolver1D solver(config);
    solver.run_simulation();
    return 0;
}
