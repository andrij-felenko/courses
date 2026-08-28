#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <memory>

constexpr double PI = 3.14159265358979323846;

struct PointVortex {
    double x{0.0};
    double y{0.0};
    double gamma{1.0};
};

class DiscreteVortexSolver {
private:
    std::vector<PointVortex> vortices_;
    double core_eps_sq_{0.0001};

    [[nodiscard]] std::pair<std::vector<double>, std::vector<double>> 
    compute_velocities(const std::vector<PointVortex>& state) const {
        const size_t n = state.size();
        std::vector<double> vx(n, 0.0);
        std::vector<double> vy(n, 0.0);
        const double inv_2pi = 1.0 / (2.0 * PI);

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                if (i == j) continue;
                const double dx = state[i].x - state[j].x;
                const double dy = state[i].y - state[j].y;
                const double r2 = dx * dx + dy * dy + core_eps_sq_;
                const double factor = inv_2pi * state[j].gamma / r2;

                vx[i] += -dy * factor;
                vy[i] +=  dx * factor;
            }
        }
        return {vx, vy};
    }

public:
    DiscreteVortexSolver(std::vector<PointVortex> initial_vortices, double eps = 0.01)
        : vortices_(std::move(initial_vortices)), core_eps_sq_(eps * eps) {}

    void step_rk4(double dt) {
        const size_t n = vortices_.size();

        // K1
        auto [vx1, vy1] = compute_velocities(vortices_);

        // K2
        auto state2 = vortices_;
        for (size_t i = 0; i < n; ++i) {
            state2[i].x += 0.5 * dt * vx1[i];
            state2[i].y += 0.5 * dt * vy1[i];
        }
        auto [vx2, vy2] = compute_velocities(state2);

        // K3
        auto state3 = vortices_;
        for (size_t i = 0; i < n; ++i) {
            state3[i].x += 0.5 * dt * vx2[i];
            state3[i].y += 0.5 * dt * vy2[i];
        }
        auto [vx3, vy3] = compute_velocities(state3);

        // K4
        auto state4 = vortices_;
        for (size_t i = 0; i < n; ++i) {
            state4[i].x += dt * vx3[i];
            state4[i].y += dt * vy3[i];
        }
        auto [vx4, vy4] = compute_velocities(state4);

        // State update
        for (size_t i = 0; i < n; ++i) {
            vortices_[i].x += (dt / 6.0) * (vx1[i] + 2.0 * vx2[i] + 2.0 * vx3[i] + vx4[i]);
            vortices_[i].y += (dt / 6.0) * (vy1[i] + 2.0 * vy2[i] + 2.0 * vy3[i] + vy4[i]);
        }
    }

    [[nodiscard]] double compute_angular_momentum() const {
        double M = 0.0;
        for (const auto& v : vortices_) {
            M += v.gamma * (v.x * v.x + v.y * v.y);
        }
        return M;
    }

    [[nodiscard]] const std::vector<PointVortex>& vortices() const noexcept {
        return vortices_;
    }
};

int main() {
    std::vector<PointVortex> init_vortices = {
        {-1.0,  0.5,  1.0},
        {-1.0, -0.5, -1.0},
        { 0.0,  1.0,  1.0},
        { 0.0, -1.0, -1.0}
    };

    DiscreteVortexSolver solver(init_vortices, 0.01);
    const double dt = 0.01;
    const int total_steps = 1000;
    const double M0 = solver.compute_angular_momentum();

    std::cout << "=== Discrete Vortex Method Solver (C++17) ===\n";
    std::cout << "Initial Angular Momentum M0: " << std::fixed << std::setprecision(8) << M0 << "\n\n";

    for (int step = 0; step <= total_steps; ++step) {
        if (step % 200 == 0) {
            const double M_curr = solver.compute_angular_momentum();
            const auto& v = solver.vortices();
            std::cout << "Step " << std::setw(4) << step 
                      << " | t = " << std::setw(5) << std::setprecision(2) << step * dt
                      << " | V0(" << std::setprecision(3) << v[0].x << ", " << v[0].y << ")"
                      << " | V2(" << v[2].x << ", " << v[2].y << ")"
                      << " | M = " << std::setprecision(8) << M_curr 
                      << " (Err: " << std::scientific << std::setprecision(2) << std::abs(M_curr - M0) << ")\n";
        }
        solver.step_rk4(dt);
    }

    return 0;
}
