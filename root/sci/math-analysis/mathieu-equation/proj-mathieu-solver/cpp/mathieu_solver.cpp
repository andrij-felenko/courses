// mathieu_solver.cpp — Обчислення діаграми стійкості рівняння Матьє мовою C++20
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <numbers>
#include <iomanip>

struct State {
    double y{0.0};
    double v{0.0};
};

struct MathieuResult {
    double a{0.0};
    double q{0.0};
    std::array<std::array<double, 2>, 2> monodromy{};
    double trace{0.0};
    bool is_stable{false};
    double floquet_exponent{0.0};
};

class MathieuSolver {
public:
    explicit MathieuSolver(int integration_steps = 1000)
        : steps_(integration_steps) {}

    [[nodiscard]] MathieuResult analyze(double a, double q) const {
        const State s1_final = integrate_period({1.0, 0.0}, a, q);
        const State s2_final = integrate_period({0.0, 1.0}, a, q);

        MathieuResult res;
        res.a = a;
        res.q = q;
        res.monodromy = {{{s1_final.y, s2_final.y}, {s1_final.v, s2_final.v}}};
        res.trace = s1_final.y + s2_final.v;

        const double half_trace = res.trace / 2.0;
        if (std::abs(half_trace) <= 1.000000001) {
            res.is_stable = true;
            res.floquet_exponent = 0.0;
        } else {
            res.is_stable = false;
            res.floquet_exponent = (1.0 / std::numbers::pi) * std::acosh(std::abs(half_trace));
        }
        return res;
    }

    [[nodiscard]] std::vector<std::vector<bool>> compute_stability_grid(
        double q_min, double q_max, int q_res,
        double a_min, double a_max, int a_res) const 
    {
        std::vector<std::vector<bool>> grid(a_res, std::vector<bool>(q_res));
        const double dq = (q_max - q_min) / (q_res - 1);
        const double da = (a_max - a_min) / (a_res - 1);

        for (int i = 0; i < a_res; ++i) {
            const double a = a_min + i * da;
            for (int j = 0; j < q_res; ++j) {
                const double q = q_min + j * dq;
                grid[i][j] = analyze(a, q).is_stable;
            }
        }
        return grid;
    }

private:
    int steps_;

    [[nodiscard]] static constexpr State rhs(State s, double z, double a, double q) noexcept {
        return { s.v, -(a - 2.0 * q * std::cos(2.0 * z)) * s.y };
    }

    [[nodiscard]] State rk4_step(State s, double z, double dz, double a, double q) const noexcept {
        const State k1 = rhs(s, z, a, q);
        const State k2 = rhs({s.y + 0.5 * dz * k1.y, s.v + 0.5 * dz * k1.v}, z + 0.5 * dz, a, q);
        const State k3 = rhs({s.y + 0.5 * dz * k2.y, s.v + 0.5 * dz * k2.v}, z + 0.5 * dz, a, q);
        const State k4 = rhs({s.y + dz * k3.y, s.v + dz * k3.v}, z + dz, a, q);

        return {
            s.y + (dz / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y),
            s.v + (dz / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.y)
        };
    }

    [[nodiscard]] State integrate_period(State init, double a, double q) const noexcept {
        const double dz = std::numbers::pi / steps_;
        State current = init;
        double z = 0.0;
        for (int i = 0; i < steps_; ++i) {
            current = rk4_step(current, z, dz, a, q);
            z += dz;
        }
        return current;
    }
};

int main() {
    MathieuSolver solver(1000);

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "Аналіз стійкості точок простору параметрів Матьє (C++20):\n";
    std::cout << "--------------------------------------------------------\n";

    const std::vector<std::pair<double, double>> points = {
        {0.2, 0.1}, {1.0, 0.4}, {4.0, 0.5}, {4.0, 1.2}
    };

    for (const auto& [a, q] : points) {
        const auto r = solver.analyze(a, q);
        std::cout << "Точка (q=" << r.q << ", a=" << r.a << "): Tr(M)=" << r.trace
                  << " | " << (r.is_stable ? "СТІЙКА   " : "НЕСТІЙКА ")
                  << " | μ = " << r.floquet_exponent << '\n';
    }

    return 0;
}
