#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <utility>
#include <queue>
#include <memory>

struct Point {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr bool operator==(const Point& other) const noexcept {
        return std::abs(x - other.x) < 1e-12 && std::abs(y - other.y) < 1e-12;
    }
};

/* Обчислення квадрата відстані від точки P до відрізка AB */
[[nodiscard]] inline double pointToSegmentDistSq(const Point& p, const Point& a, const Point& b) noexcept {
    const double vx = b.x - a.x;
    const double vy = b.y - a.y;
    const double wx = p.x - a.x;
    const double wy = p.y - a.y;

    const double segLenSq = vx * vx + vy * vy;
    if (segLenSq < 1e-12) {
        return wx * wx + wy * wy;
    }

    const double t = (wx * vx + wy * vy) / segLenSq;
    if (t <= 0.0) {
        return wx * wx + wy * wy;
    }
    if (t >= 1.0) {
        const double bx = p.x - b.x;
        const double by = p.y - b.y;
        return bx * bx + by * by;
    }

    const double cross = wx * vy - wy * vx;
    return (cross * cross) / segLenSq;
}
