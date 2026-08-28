#include <vector>
#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <numbers>
#include <algorithm>

namespace physics {

/* Виробничий RAII клас для 2D чисельного розв'язувача рівняння Пуассона */
class PoissonSolver2D {
public:
    struct ExecutionStats {
        std::size_t iterations_completed{0};
        double final_residual{0.0};
        bool is_converged{false};
    };

    PoissonSolver2D(std::size_t nx, std::size_t ny, double grid_spacing)
        : nx_(nx), ny_(ny), h_(grid_spacing),
          phi_(nx * ny, 0.0),
          rho_(nx * ny, 0.0),
          is_fixed_(nx * ny, false) {
        if (nx < 3 || ny < 3 || grid_spacing <= 0.0) {
            throw std::invalid_argument("Некоректні розміри сітки: потрібні nx, ny >= 3 та h > 0");
        }
    }

    /* Модифікатори та селектори вузлів сітки */
    [[nodiscard]] double& phi(std::size_t i, std::size_t j) { return phi_[i * ny_ + j]; }
    [[nodiscard]] double phi(std::size_t i, std::size_t j) const { return phi_[i * ny_ + j]; }

    [[nodiscard]] double& rho(std::size_t i, std::size_t j) { return rho_[i * ny_ + j]; }
    [[nodiscard]] double rho(std::size_t i, std::size_t j) const { return rho_[i * ny_ + j]; }

    /* Фіксація граничного вузла з умовою Діріхле */
    void set_dirichlet_node(std::size_t i, std::size_t j, double potential_volts) {
        std::size_t idx = i * ny_ + j;
        phi_[idx] = potential_volts;
        is_fixed_[idx] = true;
    }

    /* Фіксація зовнішнього периметра */
    void set_outer_boundaries(double v_top, double v_bot, double v_left, double v_right) {
        for (std::size_t i = 0; i < nx_; ++i) {
            set_dirichlet_node(i, 0, v_bot);
            set_dirichlet_node(i, ny_ - 1, v_top);
        }
        for (std::size_t j = 0; j < ny_; ++j) {
            set_dirichlet_node(0, j, v_left);
            set_dirichlet_node(nx_ - 1, j, v_right);
        }
    }

    /* Обчислення теоретично оптимального параметра релаксації SOR */
    [[nodiscard]] double get_optimal_omega() const noexcept {
        double min_dim = static_cast<double>(std::min(nx_, ny_));
        return 2.0 / (1.0 + std::sin(std::numbers::pi / min_dim));
    }

    /* Виконання чисельного розв'язку методом SOR */
    ExecutionStats solve(double tolerance = 1e-6, std::size_t max_iterations = 10000,
                         double permittivity = 8.8541878128e-12, double omega = 0.0) {
        if (omega <= 0.0 || omega >= 2.0) {
            omega = get_optimal_omega();
        }

        double h2 = h_ * h_;
        double current_residual = 0.0;

        for (std::size_t iter = 1; iter <= max_iterations; ++iter) {
            current_residual = 0.0;

            for (std::size_t i = 1; i < nx_ - 1; ++i) {
                for (std::size_t j = 1; j < ny_ - 1; ++j) {
                    std::size_t idx = i * ny_ + j;
                    if (is_fixed_[idx]) continue;

                    double phi_gs = 0.25 * (phi_[(i + 1) * ny_ + j] + phi_[(i - 1) * ny_ + j] +
                                            phi_[i * ny_ + (j + 1)] + phi_[i * ny_ + (j - 1)]) +
                                    0.25 * h2 * (rho_[idx] / permittivity);

                    double old_val = phi_[idx];
                    double new_val = (1.0 - omega) * old_val + omega * phi_gs;
                    phi_[idx] = new_val;

                    current_residual = std::max(current_residual, std::abs(new_val - old_val));
                }
            }

            if (current_residual < tolerance) {
                return ExecutionStats{iter, current_residual, true};
            }
        }
        return ExecutionStats{max_iterations, current_residual, false};
    }

private:
    std::size_t nx_;
    std::size_t ny_;
    double h_;
    std::vector<double> phi_;
    std::vector<double> rho_;
    std::vector<bool> is_fixed_;
};

} // namespace physics
