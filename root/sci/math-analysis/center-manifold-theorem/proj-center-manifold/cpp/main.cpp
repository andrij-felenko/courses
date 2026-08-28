#include <iostream>
#include <vector>
#include <cmath>
#include <expected>
#include <format>
#include <span>

namespace CM {

struct System2D {
    double gamma{10.0};
    double f20{0.5}, f11{1.0}, f02{-0.2}, f30{-1.2};
    double g20{2.0}, g11{-0.5}, g02{0.1};
};

struct Manifold2D {
    double h2{0.0};
    double h3{0.0};

    [[nodiscard]] constexpr double evaluate(double x) const noexcept {
        return h2 * x * x + h3 * x * x * x;
    }
};

enum class ReductionError {
    InvalidDampingFactor,
    DivergentTrajectory
};

// Обчислення многовиду з обробкою помилок через std::expected (C++23)
[[nodiscard]] std::expected<Manifold2D, ReductionError> compute_manifold(const System2D& sys) noexcept {
    if (sys.gamma <= 0.0) {
        return std::unexpected(ReductionError::InvalidDampingFactor);
    }

    Manifold2D mf;
    mf.h2 = sys.g20 / sys.gamma;
    mf.h3 = (sys.g11 * mf.h2 + 2.0 * mf.h2 * sys.f20) / sys.gamma;
    return mf;
}

class SystemSolver {
public:
    explicit SystemSolver(System2D sys) : sys_{sys} {
        auto res = compute_manifold(sys_);
        if (res) {
            manifold_ = *res;
        } else {
            throw std::invalid_argument("Некоректний коефіцієнт згасання gamma");
        }
    }

    [[nodiscard]] std::pair<double, double> full_rhs(double x, double y) const noexcept {
        double dxdt = sys_.f20 * x * x + sys_.f11 * x * y + sys_.f02 * y * y + sys_.f30 * x * x * x;
        double dydt = -sys_.gamma * y + sys_.g20 * x * x + sys_.g11 * x * y + sys_.g02 * y * y;
        return {dxdt, dydt};
    }

    [[nodiscard]] double reduced_rhs(double x) const noexcept {
        double yh = manifold_.evaluate(x);
        return sys_.f20 * x * x + sys_.f11 * x * yh + sys_.f02 * yh * yh + sys_.f30 * x * x * x;
    }

    void step_full_rk4(double& x, double& y, double dt) const noexcept {
        auto [k1x, k1y] = full_rhs(x, y);
        auto [k2x, k2y] = full_rhs(x + 0.5 * dt * k1x, y + 0.5 * dt * k1y);
        auto [k3x, k3y] = full_rhs(x + 0.5 * dt * k2x, y + 0.5 * dt * k2y);
        auto [k4x, k4y] = full_rhs(x + dt * k3x, y + dt * k3y);

        x += (dt / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x);
        y += (dt / 6.0) * (k1y + 2.0 * k2y + 2.0 * k3y + k4y);
    }

    void step_reduced_rk4(double& x, double dt) const noexcept {
        double k1 = reduced_rhs(x);
        double k2 = reduced_rhs(x + 0.5 * dt * k1);
        double k3 = reduced_rhs(x + 0.5 * dt * k2);
        double k4 = reduced_rhs(x + dt * k3);

        x += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
    }

    [[nodiscard]] const Manifold2D& manifold() const noexcept { return manifold_; }

private:
    System2D sys_;
    Manifold2D manifold_;
};

} // namespace CM

int main() {
    CM::System2D sys{.gamma = 10.0};
    CM::SystemSolver solver(sys);

    std::cout << "=== C++20/23 Обчислення центрального многовиду ===\n";
    std::cout << std::format("h2 = {:.6f}, h3 = {:.6f}\n\n", 
                             solver.manifold().h2, solver.manifold().h3);

    double x_full = 0.4, y_full = 0.8;
    double x_red = 0.4;
    double t = 0.0;
    constexpr double dt = 0.01;
    constexpr int steps = 100;

    std::cout << std::format("{:<6} {:<12} {:<12} {:<12} {:<12}\n", 
                             "t", "x_full", "y_full", "x_red", "Error");
    std::cout << "---------------------------------------------------------\n";

    for (int i = 0; i <= steps; ++i) {
        if (i % 10 == 0) {
            double err = std::abs(x_full - x_red);
            std::cout << std::format("{:<6.2f} {:<12.6f} {:<12.6f} {:<12.6f} {:<12.6e}\n", 
                                     t, x_full, y_full, x_red, err);
        }
        solver.step_full_rk4(x_full, y_full, dt);
        solver.step_reduced_rk4(x_red, dt);
        t += dt;
    }

    return 0;
}
