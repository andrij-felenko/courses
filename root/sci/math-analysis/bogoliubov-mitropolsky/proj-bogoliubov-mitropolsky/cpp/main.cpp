#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <iomanip>

struct State2D {
    double x{0.0};
    double v{0.0};
};

struct SimPoint {
    double t{0.0};
    double x_exact{0.0};
    double x_bm1{0.0};
    double x_bm2{0.0};
    double err_bm1{0.0};
    double err_bm2{0.0};
};

class VanDerPolSolver {
public:
    explicit VanDerPolSolver(double eps) : eps_{eps} {}

    [[nodiscard]] State2D derivatives(State2D s) const noexcept {
        return {s.v, -s.x + eps_ * (1.0 - s.x * s.x) * s.v};
    }

    [[nodiscard]] State2D rk4Step(State2D s, double h) const noexcept {
        const auto k1 = derivatives(s);
        const auto k2 = derivatives({s.x + 0.5 * h * k1.x, s.v + 0.5 * h * k1.v});
        const auto k3 = derivatives({s.x + 0.5 * h * k2.x, s.v + 0.5 * h * k2.v});
        const auto k4 = derivatives({s.x + h * k3.x, s.v + h * k3.v});

        return {
            s.x + (h / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x),
            s.v + (h / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v)
        };
    }

    [[nodiscard]] double bm1Solution(double a0, double psi0, double t) const noexcept {
        const double a_t = 2.0 * a0 / std::sqrt(a0 * a0 + (4.0 - a0 * a0) * std::exp(-eps_ * t));
        return a_t * std::cos(t + psi0);
    }

    [[nodiscard]] double bm2Solution(double a0, double psi0, double t) const noexcept {
        const double a_t = 2.0 * a0 / std::sqrt(a0 * a0 + (4.0 - a0 * a0) * std::exp(-eps_ * t));
        const double psi_t = psi0 - (eps_ * eps_ / 16.0) * t;
        const double theta = t + psi_t;
        const double u1 = - (std::pow(a_t, 3) / 32.0) * std::sin(3.0 * theta);
        return a_t * std::cos(theta) + eps_ * u1;
    }

    [[nodiscard]] std::vector<SimPoint> simulate(double a0, double psi0, double tMax, double h) const {
        const size_t steps = static_cast<size_t>(tMax / h);
        std::vector<SimPoint> history;
        history.reserve(steps);

        State2D state{a0 * std::cos(psi0), -a0 * std::sin(psi0)};

        for (size_t i = 0; i < steps; ++i) {
            const double t = i * h;
            const double x1 = bm1Solution(a0, psi0, t);
            const double x2 = bm2Solution(a0, psi0, t);

            const double e1 = std::abs(state.x - x1);
            const double e2 = std::abs(state.x - x2);

            history.push_back({t, state.x, x1, x2, e1, e2});
            state = rk4Step(state, h);
        }

        return history;
    }

private:
    double eps_;
};

int main() {
    constexpr double eps = 0.1;
    constexpr double tMax = 100.0;
    constexpr double h = 0.01;

    VanDerPolSolver solver(eps);
    const auto results = solver.simulate(1.0, 0.0, tMax, h);

    double maxErr1 = 0.0;
    double maxErr2 = 0.0;

    for (const auto& pt : results) {
        maxErr1 = std::max(maxErr1, pt.err_bm1);
        maxErr2 = std::max(maxErr2, pt.err_bm2);
    }

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "=== Результати C++20 моделювання для eps = " << eps << " ===\n";
    std::cout << "Максимальна похибка BM-1 (O(eps)):   " << maxErr1 << "\n";
    std::cout << "Максимальна похибка BM-2 (O(eps^2)): " << maxErr2 << "\n";
    std::cout << "Коефіцієнт покращення точності:       " << maxErr1 / maxErr2 << "x\n";

    return 0;
}
