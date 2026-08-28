#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <algorithm>

struct Vec2 {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vec2 operator+(const Vec2& other) const noexcept {
        return {x + other.x, y + other.y};
    }

    [[nodiscard]] constexpr Vec2 operator-(const Vec2& other) const noexcept {
        return {x - other.x, y - other.y};
    }

    [[nodiscard]] constexpr Vec2 operator-() const noexcept {
        return {-x, -y};
    }

    [[nodiscard]] constexpr double cross(const Vec2& other) const noexcept {
        return x * other.y - y * other.x;
    }
};

using Polygon = std::vector<Vec2>;

[[nodiscard]] size_t find_bottom_left(std::span<const Vec2> poly) noexcept {
    if (poly.empty()) return 0;
    size_t min_idx = 0;
    for (size_t i = 1; i < poly.size(); ++i) {
        if (poly[i].y < poly[min_idx].y ||
            (std::abs(poly[i].y - poly[min_idx].y) < 1e-9 && poly[i].x < poly[min_idx].x)) {
            min_idx = i;
        }
    }
    return min_idx;
}

[[nodiscard]] Polygon invert_and_reorder(std::span<const Vec2> poly) {
    Polygon result;
    result.reserve(poly.size());
    for (auto it = poly.rbegin(); it != poly.rend(); ++it) {
        result.push_back(-(*it));
    }
    return result;
}

[[nodiscard]] Polygon minkowski_sum_convex(std::span<const Vec2> poly_b, std::span<const Vec2> poly_a_neg) {
    if (poly_b.empty() || poly_a_neg.empty()) return {};

    Polygon result;
    result.reserve(poly_b.size() + poly_a_neg.size());

    size_t i = find_bottom_left(poly_b);
    size_t j = find_bottom_left(poly_a_neg);

    const size_t count_b = poly_b.size();
    const size_t count_a = poly_a_neg.size();

    size_t steps_b = 0;
    size_t steps_a = 0;

    while (steps_b < count_b || steps_a < count_a) {
        result.push_back(poly_b[i] + poly_a_neg[j]);

        const Vec2 edge_b = poly_b[(i + 1) % count_b] - poly_b[i];
        const Vec2 edge_a = poly_a_neg[(j + 1) % count_a] - poly_a_neg[j];

        const double cp = edge_b.cross(edge_a);

        if (steps_b < count_b && steps_a < count_a) {
            if (cp > 1e-9) {
                i = (i + 1) % count_b;
                steps_b++;
            } else if (cp < -1e-9) {
                j = (j + 1) % count_a;
                steps_a++;
            } else {
                i = (i + 1) % count_b;
                j = (j + 1) % count_a;
                steps_b++;
                steps_a++;
            }
        } else if (steps_b < count_b) {
            i = (i + 1) % count_b;
            steps_b++;
        } else {
            j = (j + 1) % count_a;
            steps_a++;
        }
    }

    return result;
}

[[nodiscard]] Polygon compute_c_obstacle(std::span<const Vec2> obstacle, std::span<const Vec2> robot) {
    const Polygon robot_neg = invert_and_reorder(robot);
    return minkowski_sum_convex(obstacle, robot_neg);
}

int main() {
    const Polygon robot = {
        {-0.4, -0.3},
        { 0.4, -0.3},
        { 0.4,  0.3},
        {-0.4,  0.3}
    };

    const Polygon obstacle = {
        {2.0, 1.0},
        {4.0, 1.0},
        {3.0, 3.0}
    };

    const Polygon c_obs = compute_c_obstacle(obstacle, robot);

    std::cout << "Побудовано C-перешкоду (" << c_obs.size() << " вершин):\n";
    for (size_t idx = 0; idx < c_obs.size(); ++idx) {
        std::cout << "  V[" << idx << "] = (" << c_obs[idx].x << ", " << c_obs[idx].y << ")\n";
    }

    return 0;
}
