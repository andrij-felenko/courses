#include <cmath>
#include <numbers>
#include <utility>

struct Vec2 {
    double x{0.0};
    double y{0.0};
};

struct AirfoilPanel {
    Vec2 p1;
    Vec2 p2;
    Vec2 cp;
    Vec2 normal;
    Vec2 tangent;
    double length{0.0};
};

// Обчислення швидкості, індукованої панеллю одиничної циркуляції
[[nodiscard]] std::pair<double, double> compute_induced_velocity(
    const AirfoilPanel& panel, double x, double y) noexcept {
    const double dx = x - panel.p1.x;
    const double dy = y - panel.p1.y;
    const double ct = panel.tangent.x;
    const double st = panel.tangent.y;

    const double x_loc = dx * ct + dy * st;
    const double y_loc = -dx * st + dy * ct;

    if (std::abs(y_loc) < 1e-9 && x_loc >= 0.0 && x_loc <= panel.length) {
        return {0.0, 0.0};
    }

    const double r1_sq = x_loc * x_loc + y_loc * y_loc;
    const double r2_sq = (x_loc - panel.length) * (x_loc - panel.length) + y_loc * y_loc;
    const double th1 = std::atan2(y_loc, x_loc);
    const double th2 = std::atan2(y_loc, x_loc - panel.length);

    const double u_loc = -(1.0 / (2.0 * std::numbers::pi)) * (th2 - th1);
    const double v_loc = (1.0 / (4.0 * std::numbers::pi)) * std::log(r2_sq / (r1_sq + 1e-15));

    return {u_loc * ct - v_loc * st, u_loc * st + v_loc * ct};
}
