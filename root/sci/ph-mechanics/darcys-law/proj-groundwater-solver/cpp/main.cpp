// C++17/C++20 Idiomatic Groundwater Darcy Solver
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

class DarcySolver2D {
public:
    DarcySolver2D(std::size_t nx, std::size_t ny, double dx, double dy, double viscosity)
        : nx_(nx), ny_(ny), dx_(dx), dy_(dy), visco_(viscosity),
          p_(nx * ny, 0.0), k_(nx * ny, 1.0e-11),
          vx_(nx * ny, 0.0), vy_(nx * ny, 0.0) {}

    void set_clay_barrier(std::size_t x_min, std::size_t x_max,
                        std::size_t y_min, std::size_t y_max, double k_clay) {
        for (std::size_t i = x_min; i <= x_max; ++i) {
            for (std::size_t j = y_min; j <= y_max; ++j) {
                k_[at(i, j)] = k_clay;
            }
        }
    }

    void set_pressure_boundaries(double p_left, double p_right) {
        for (std::size_t j = 0; j < ny_; ++j) {
            p_[at(0, j)] = p_left;
            p_[at(nx_ - 1, j)] = p_right;
        }
    }

    bool solve(std::size_t max_iterations = 5000, double tolerance = 1.0e-5, double omega = 1.75) {
        for (std::size_t iter = 0; iter < max_iterations; ++iter) {
            double max_error = 0.0;

            for (std::size_t i = 1; i < nx_ - 1; ++i) {
                for (std::size_t j = 1; j < ny_ - 1; ++j) {
                    const double k_center = k_[at(i, j)];

                    // Гармонічне усереднення проникності на межах комірок
                    const double k_e = 2.0 * k_center * k_[at(i + 1, j)] / (k_center + k_[at(i + 1, j)]);
                    const double k_w = 2.0 * k_center * k_[at(i - 1, j)] / (k_center + k_[at(i - 1, j)]);
                    const double k_n = 2.0 * k_center * k_[at(i, j + 1)] / (k_center + k_[at(i, j + 1)]);
                    const double k_s = 2.0 * k_center * k_[at(i, j - 1)] / (k_center + k_[at(i, j - 1)]);

                    const double denom = k_e + k_w + k_n + k_s;
                    const double p_target = (k_e * p_[at(i + 1, j)] + k_w * p_[at(i - 1, j)] +
                                           k_n * p_[at(i, j + 1)] + k_s * p_[at(i, j - 1)]) / denom;

                    const double diff = std::abs(p_target - p_[at(i, j)]);
                    max_error = std::max(max_error, diff);

                    // SOR релаксація
                    p_[at(i, j)] += omega * (p_target - p_[at(i, j)]);
                }
            }

            if (max_error < tolerance) {
                compute_velocities();
                return true;
            }
        }
        compute_velocities();
        return false;
    }

    [[nodiscard]] double pressure(std::size_t i, std::size_t j) const { return p_[at(i, j)]; }
    [[nodiscard]] double velocity_x(std::size_t i, std::size_t j) const { return vx_[at(i, j)]; }
    [[nodiscard]] double velocity_y(std::size_t i, std::size_t j) const { return vy_[at(i, j)]; }

private:
    [[nodiscard]] inline std::size_t at(std::size_t i, std::size_t j) const noexcept {
        return i * ny_ + j;
    }

    void compute_velocities() {
        for (std::size_t i = 1; i < nx_ - 1; ++i) {
            for (std::size_t j = 1; j < ny_ - 1; ++j) {
                const double dp_dx = (p_[at(i + 1, j)] - p_[at(i - 1, j)]) / (2.0 * dx_);
                const double dp_dy = (p_[at(i, j + 1)] - p_[at(i, j - 1)]) / (2.0 * dy_);

                vx_[at(i, j)] = - (k_[at(i, j)] / visco_) * dp_dx;
                vy_[at(i, j)] = - (k_[at(i, j)] / visco_) * dp_dy;
            }
        }
    }

    std::size_t nx_, ny_;
    double dx_, dy_, visco_;
    std::vector<double> p_;
    std::vector<double> k_;
    std::vector<double> vx_;
    std::vector<double> vy_;
};

int main() {
    DarcySolver2D solver(50, 50, 1.0, 1.0, 1.0e-3);
    solver.set_pressure_boundaries(100000.0, 0.0);
    solver.set_clay_barrier(20, 30, 15, 35, 1.0e-15); // Бар'єр 1 мікродарсі

    if (solver.solve()) {
        std::cout << "Збіжність чисельного розв'язку успішно досягнута!\n";
    }

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Тиск у центрі (25, 25): " << solver.pressure(25, 25) << " Па\n";
    std::cout << "Швидкість Дарсі vx у піску (10, 25): " << solver.velocity_x(10, 25) << " м/с\n";
    std::cout << "Швидкість Дарсі vx у глині (25, 25): " << solver.velocity_x(25, 25) << " м/с\n";
    return 0;
}
