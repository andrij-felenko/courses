#include <vector>
#include <span>
#include <utility>
#include <cmath>

struct Point {
    double x{0.0};
    double y{0.0};
};

[[nodiscard]] inline double calcDistSq(const Point& p, const Point& a, const Point& b) noexcept {
    const double vx = b.x - a.x, vy = b.y - a.y;
    const double wx = p.x - a.x, wy = p.y - a.y;
    const double segSq = vx * vx + vy * vy;
    if (segSq < 1e-12) return wx * wx + wy * wy;

    const double t = (wx * vx + wy * vy) / segSq;
    if (t <= 0.0) return wx * wx + wy * wy;
    if (t >= 1.0) {
        const double bx = p.x - b.x, by = p.y - b.y;
        return bx * bx + by * by;
    }
    const double cross = wx * vy - wy * vx;
    return (cross * cross) / segSq;
}

/* Ітеративний Дуглас-Пекер із поверненням нового вектора точок */
[[nodiscard]] std::vector<Point> simplifyDouglasPeucker(std::span<const Point> points, double eps) {
    const size_t n = points.size();
    if (n <= 2) {
        return std::vector<Point>(points.begin(), points.end());
    }

    const double epsSq = eps * eps;
    std::vector<bool> keep(n, false);
    keep[0] = true;
    keep[n - 1] = true;

    std::vector<std::pair<size_t, size_t>> stack;
    stack.reserve(64);
    stack.emplace_back(0, n - 1);

    while (!stack.empty()) {
        const auto [start, end] = stack.back();
        stack.pop_back();

        if (end <= start + 1) continue;

        double maxDistSq = 0.0;
        size_t maxIdx = start;
        const Point& a = points[start];
        const Point& b = points[end];

        for (size_t i = start + 1; i < end; ++i) {
            const double dSq = calcDistSq(points[i], a, b);
            if (dSq > maxDistSq) {
                maxDistSq = dSq;
                maxIdx = i;
            }
        }

        if (maxDistSq > epsSq) {
            keep[maxIdx] = true;
            stack.emplace_back(start, maxIdx);
            stack.emplace_back(maxIdx, end);
        }
    }

    std::vector<Point> result;
    result.reserve(n / 4);
    for (size_t i = 0; i < n; ++i) {
        if (keep[i]) {
            result.push_back(points[i]);
        }
    }
    return result;
}
