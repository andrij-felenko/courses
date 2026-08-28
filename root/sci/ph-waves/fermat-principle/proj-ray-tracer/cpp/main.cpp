#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

struct Vector2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] Vector2D operator+(const Vector2D& other) const { return {x + other.x, y + other.y}; }
    [[nodiscard]] Vector2D operator*(double scalar) const { return {x * scalar, y * scalar}; }
};

struct RayState {
    Vector2D pos; // (x, y) - вектор координати
    Vector2D p;   // (px, py) - канонічний оптичний імпульс
};

class GRINMedium {
public:
    GRINMedium(double n0, double dn, double y0)
        : n0_(n0), dn_(dn), y0_(y0) {}

    [[nodiscard]] double index(const Vector2D& pos) const {
        double y = std::max(0.0, pos.y);
        return n0_ + dn_ * (1.0 - std::exp(-y / y0_));
    }

    [[nodiscard]] Vector2D gradient(const Vector2D& pos) const {
        double y = std::max(0.0, pos.y);
        return {0.0, (dn_ / y0_) * std::exp(-y / y0_)};
    }

private:
    double n0_;
    double dn_;
    double y0_;
};

class RayTracer {
public:
    explicit RayTracer(GRINMedium medium) : medium_(std::move(medium)) {}

    [[nodiscard]] RayState derivatives(const RayState& state) const {
        double n = medium_.index(state.pos);
        Vector2D grad = medium_.gradient(state.pos);

        return {
            .pos = {state.p.x / n, state.p.y / n},
            .p   = grad
        };
    }

    [[nodiscard]] RayState rk4Step(const RayState& state, double ds) const {
        RayState k1 = derivatives(state);

        RayState s_k2{
            .pos = state.pos + k1.pos * (0.5 * ds),
            .p   = state.p   + k1.p   * (0.5 * ds)
        };
        RayState k2 = derivatives(s_k2);

        RayState s_k3{
            .pos = state.pos + k2.pos * (0.5 * ds),
            .p   = state.p   + k2.p   * (0.5 * ds)
        };
        RayState k3 = derivatives(s_k3);

        RayState s_k4{
            .pos = state.pos + k3.pos * ds,
            .p   = state.p   + k3.p   * ds
        };
        RayState k4 = derivatives(s_k4);

        return {
            .pos = state.pos + (k1.pos + k2.pos * 2.0 + k3.pos * 2.0 + k4.pos) * (ds / 6.0),
            .p   = state.p   + (k1.p   + k2.p   * 2.0 + k3.p   * 2.0 + k4.p)   * (ds / 6.0)
        };
    }

    std::vector<RayState> trace(RayState start, double ds, double maxDistance) const {
        std::vector<RayState> path;
        path.reserve(static_cast<size_t>(maxDistance / ds));

        RayState current = start;
        for (double s = 0.0; s < maxDistance; s += ds) {
            path.push_back(current);
            if (current.pos.y <= 0.0 && current.p.y < 0.0) {
                current.p.y = -current.p.y; // Дзеркальне відбиття від поверхні
            }
            current = rk4Step(current, ds);
        }
        return path;
    }

private:
    GRINMedium medium_;
};

int main() {
    GRINMedium atmosphere(1.00026, 0.00030, 1.5);
    RayTracer tracer(atmosphere);

    double startY = 1.2;
    double angleRad = -1.5 * (M_PI / 180.0);
    double nStart = atmosphere.index({0.0, startY});

    RayState initial{
        .pos = {0.0, startY},
        .p   = {nStart * std::cos(angleRad), nStart * std::sin(angleRad)}
    };

    double ds = 0.1;
    auto trajectory = tracer.trace(initial, ds, 150.0);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "# Trajectory points (x, y):\n";
    for (size_t i = 0; i < trajectory.size(); i += 50) {
        std::cout << "Step " << i << ": x = " << trajectory[i].pos.x
                  << " m, y = " << trajectory[i].pos.y << " m\n";
    }

    return 0;
}
