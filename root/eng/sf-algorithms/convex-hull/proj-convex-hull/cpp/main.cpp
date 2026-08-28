#include <vector>
#include <cstdint>
#include <algorithm>
#include <span>
#include <iostream>

struct Point {
    std::int64_t x{0};
    std::int64_t y{0};

    constexpr auto operator<=>(const Point&) const = default;
};

// Векторний косий добуток (B - A) x (C - A)
[[nodiscard]] constexpr std::int64_t cross_product(Point a, Point b, Point c) noexcept {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

// Побудова строгої опуклої оболонки методом монотонного ланцюга Ендрю
[[nodiscard]] std::vector<Point> build_convex_hull(std::span<const Point> input_points) {
    if (input_points.size() <= 2) {
        return std::vector<Point>(input_points.begin(), input_points.end());
    }

    // 1. Копіювання та лексикографічне сортування
    std::vector<Point> pts(input_points.begin(), input_points.end());
    std::sort(pts.begin(), pts.end());
    
    // Видалення ідентичних точок
    const auto last_unique = std::unique(pts.begin(), pts.end());
    pts.erase(last_unique, pts.end());

    const std::size_t n = pts.size();
    if (n <= 2) {
        return pts;
    }

    std::vector<Point> hull;
    hull.reserve(2 * n);

    // 2. Побудова нижньої оболонки (зліва направо)
    for (std::size_t i = 0; i < n; ++i) {
        while (hull.size() >= 2 && 
               cross_product(hull[hull.size() - 2], hull[hull.size() - 1], pts[i]) <= 0) {
            hull.pop_back();
        }
        hull.push_back(pts[i]);
    }

    // 3. Побудова верхньої оболонки (справа наліво)
    const std::size_t lower_size_bound = hull.size() + 1;
    for (std::size_t i = n - 1; i > 0; --i) {
        const Point& pt = pts[i - 1];
        while (hull.size() >= lower_size_bound && 
               cross_product(hull[hull.size() - 2], hull[hull.size() - 1], pt) <= 0) {
            hull.pop_back();
        }
        hull.push_back(pt);
    }

    // Видаляємо останню точку, оскільки вона дублює початкову вершину hull[0]
    hull.pop_back();
    return hull;
}
