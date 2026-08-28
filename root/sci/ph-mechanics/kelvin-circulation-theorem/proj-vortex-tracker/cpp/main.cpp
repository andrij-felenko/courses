#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>

struct Vector2D {
    double x{0.0};
    double y{0.0};
};

class CirculationTracker {
public:
    static constexpr double PI = 3.14159265358979323846;

    static Vector2D velocity_field(double x, double y, double t) noexcept {
        return {
            -std::sin(PI * x) * std::cos(PI * y) * std::exp(-0.01 * t),
             std::cos(PI * x) * std::sin(PI * y) * std::exp(-0.01 * t)
        };
    }

    static Vector2D advance_rk4(Vector2D r, double t, double dt) noexcept {
        auto k1 = velocity_field(r.x, r.y, t);
        auto k2 = velocity_field(r.x + 0.5 * dt * k1.x, r.y + 0.5 * dt * k1.y, t + 0.5 * dt);
        auto k3 = velocity_field(r.x + 0.5 * dt * k2.x, r.y + 0.5 * dt * k2.y, t + 0.5 * dt);
        auto k4 = velocity_field(r.x + dt * k3.x, r.y + dt * k3.y, t + dt);

        return {
            r.x + (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x),
            r.y + (dt / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y)
        };
    }

    static double compute_circulation(std::span<const Vector2D> contour, double t) noexcept {
        double gamma = 0.0;
        const size_t n = contour.size();
        for (size_t i = 0; i < n; ++i) {
            size_t prev = (i == 0) ? n - 1 : i - 1;
            size_t next = (i + 1 == n) ? 0 : i + 1;

            double dx = 0.5 * (contour[next].x - contour[prev].x);
            double dy = 0.5 * (contour[next].y - contour[prev].y);

            auto u = velocity_field(contour[i].x, contour[i].y, t);
            gamma += u.x * dx + u.y * dy;
        }
        return gamma;
    }
};

int main() {
    constexpr size_t N = 100;
    constexpr double dt = 0.01;
    constexpr int steps = 500;

    std::vector<Vector2D> contour(N);
    constexpr double R = 0.25;
    for (size_t i = 0; i < N; ++i) {
        double theta = 2.0 * CirculationTracker::PI * i / N;
        contour[i] = {0.5 + R * std::cos(theta), 0.5 + R * std::sin(theta)};
    }

    double t = 0.0;
    const double gamma_initial = CirculationTracker::compute_circulation(contour, t);

    std::cout << std::fixed << std::setprecision(8);
    std::cout << "t = " << std::setw(5) << t << " | Gamma = " << gamma_initial << "\n";

    for (int step = 1; step <= steps; ++step) {
        for (auto& particle : contour) {
            particle = CirculationTracker::advance_rk4(particle, t, dt);
        }
        t += dt;

        if (step % 100 == 0) {
            double gamma_current = CirculationTracker::compute_circulation(contour, t);
            double rel_error = std::abs(gamma_current - gamma_initial) / gamma_initial;
            std::cout << "t = " << std::setw(5) << t 
                      << " | Gamma = " << gamma_current 
                      << " | Rel Error = " << std::scientific << std::setprecision(2) << rel_error 
                      << std::fixed << std::setprecision(8) << "\n";
        }
    }
    return 0;
}
