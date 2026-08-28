#include <vector>
#include <span>
#include <cmath>
#include <algorithm>
#include <stdexcept>

enum class JoinStyle {
    Miter,
    Bevel,
    Round
};

struct Vector2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& o) const noexcept {
        return {x + o.x, y + o.y};
    }
    [[nodiscard]] constexpr Vector2D operator*(double s) const noexcept {
        return {x * s, y * s};
    }
};

[[nodiscard]] std::vector<Vector2D> build_offset_contour(
    std::span<const Vector2D> points,
    double distance,
    JoinStyle style = JoinStyle::Miter,
    double miter_limit = 3.0)
{
    const size_t n = points.size();
    if (n < 3) {
        throw std::invalid_argument("Контур повинен містити щонайменше 3 вершини");
    }

    std::vector<Vector2D> normals;
    normals.reserve(n);

    for (size_t i = 0; i < n; ++i) {
        const size_t next = (i + 1) % n;
        const double dx = points[next].x - points[i].x;
        const double dy = points[next].y - points[i].y;
        const double len = std::hypot(dx, dy);
        normals.push_back((len > 1e-9) ? Vector2D{-dy / len, dx / len} : Vector2D{0.0, 0.0});
    }

    std::vector<Vector2D> result;
    result.reserve(n * 2);

    for (size_t i = 0; i < n; ++i) {
        const size_t prev = (i + n - 1) % n;
        const Vector2D n1 = normals[prev];
        const Vector2D n2 = normals[i];
        const Vector2D v = points[i];

        const double dot = n1.x * n2.x + n1.y * n2.y;
        const double cross = n1.x * n2.y - n1.y * n2.x;

        if (std::abs(cross) < 1e-7 && dot > 0.0) {
            result.push_back(v + n1 * distance);
            continue;
        }

        const bool is_convex = (cross > 0.0);

        if (!is_convex) {
            // Увігнутий кут
            const double denom = std::max(1.0 + dot, 1e-6);
            const double k = distance / denom;
            result.push_back(v + (n1 + n2) * k);
        } else {
            // Опуклий кут
            switch (style) {
                case JoinStyle::Miter: {
                    const double denom = 1.0 + dot;
                    const double miter_ratio = (denom > 1e-6) ? std::sqrt(2.0 / denom) : 1e9;
                    if (miter_ratio <= miter_limit) {
                        result.push_back(v + (n1 + n2) * (distance / denom));
                    } else {
                        result.push_back(v + n1 * distance);
                        result.push_back(v + n2 * distance);
                    }
                    break;
                }
                case JoinStyle::Bevel: {
                    result.push_back(v + n1 * distance);
                    result.push_back(v + n2 * distance);
                    break;
                }
                case JoinStyle::Round: {
                    // У спрощеному блоці фаска, повне скруглення описано в окремому модулі
                    result.push_back(v + n1 * distance);
                    result.push_back(v + n2 * distance);
                    break;
                }
            }
        }
    }

    return result;
}
