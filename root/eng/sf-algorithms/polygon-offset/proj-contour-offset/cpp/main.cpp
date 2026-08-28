#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <stdexcept>
#include <algorithm>

enum class JoinType {
    Miter,
    Bevel,
    Round
};

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Point2D operator+(const Point2D& o) const noexcept {
        return {x + o.x, y + o.y};
    }
    [[nodiscard]] constexpr Point2D operator-(const Point2D& o) const noexcept {
        return {x - o.x, y - o.y};
    }
    [[nodiscard]] constexpr Point2D operator*(double s) const noexcept {
        return {x * s, y * s};
    }
};

// Обчислення орієнтованої площі для перевірки напрямку обходу
[[nodiscard]] double compute_polygon_area(std::span<const Point2D> poly) noexcept {
    double area = 0.0;
    const size_t n = poly.size();
    for (size_t i = 0, j = n - 1; i < n; j = i++) {
        area += (poly[j].x * poly[i].y - poly[i].x * poly[j].y);
    }
    return area * 0.5;
}

// Побудова зміщеного контуру багатокутника на величину d
[[nodiscard]] std::vector<Point2D> offset_polygon(
    std::span<const Point2D> input,
    double distance,
    JoinType join = JoinType::Miter,
    double miter_limit = 3.0,
    int arc_steps = 6)
{
    const size_t n = input.size();
    if (n < 3) {
        throw std::invalid_argument("Многокутник повинен мати щонайменше 3 вершини");
    }

    const double area = compute_polygon_area(input);
    const bool is_ccw = (area > 0.0);
    const double d = is_ccw ? distance : -distance;

    std::vector<Point2D> normals;
    normals.reserve(n);

    for (size_t i = 0; i < n; ++i) {
        const size_t next = (i + 1) % n;
        const double dx = input[next].x - input[i].x;
        const double dy = input[next].y - input[i].y;
        const double len = std::hypot(dx, dy);
        if (len < 1e-9) {
            normals.push_back({0.0, 0.0});
        } else {
            normals.push_back({-dy / len, dx / len});
        }
    }

    std::vector<Point2D> result;
    result.reserve(n * 2);

    for (size_t i = 0; i < n; ++i) {
        const size_t prev = (i + n - 1) % n;
        const Point2D n1 = normals[prev];
        const Point2D n2 = normals[i];
        const Point2D v = input[i];

        const double dot = n1.x * n2.x + n1.y * n2.y;
        const double cross = n1.x * n2.y - n1.y * n2.x;

        if (std::abs(cross) < 1e-7 && dot > 0.0) {
            result.push_back(v + n1 * d);
            continue;
        }

        const bool is_convex = (cross > 0.0);

        if (!is_convex) {
            // Увігнутий кут: зміщені прямі перетинаються всередині
            const double denom = std::max(1.0 + dot, 1e-6);
            const double k = d / denom;
            result.push_back(v + (n1 + n2) * k);
        } else {
            // Опуклий кут: обробка стику
            switch (join) {
                case JoinType::Miter: {
                    const double denom = 1.0 + dot;
                    if (denom > 1e-6) {
                        const double miter_ratio = std::sqrt(2.0 / denom);
                        if (miter_ratio <= miter_limit) {
                            result.push_back(v + (n1 + n2) * (d / denom));
                            break;
                        }
                    }
                    // Якщо ліміт перевищено — створюємо фаску
                    result.push_back(v + n1 * d);
                    result.push_back(v + n2 * d);
                    break;
                }
                case JoinType::Bevel: {
                    result.push_back(v + n1 * d);
                    result.push_back(v + n2 * d);
                    break;
                }
                case JoinType::Round: {
                    double a1 = std::atan2(n1.y, n1.x);
                    double a2 = std::atan2(n2.y, n2.x);
                    if (a2 < a1) a2 += 2.0 * std::numbers::pi;
                    const int steps = std::max(arc_steps, 2);
                    for (int s = 0; s <= steps; ++s) {
                        const double t = static_cast<double>(s) / steps;
                        const double angle = a1 + t * (a2 - a1);
                        result.push_back(v + Point2D{std::cos(angle), std::sin(angle)} * d);
                    }
                    break;
                }
            }
        }
    }

    return result;
}
