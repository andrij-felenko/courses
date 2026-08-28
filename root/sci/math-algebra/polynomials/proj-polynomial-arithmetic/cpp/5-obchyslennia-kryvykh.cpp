#include <vector>
#include <span>
#include <concepts>

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr friend Point2D lerp(Point2D p0, Point2D p1, double t) noexcept {
        return {
            (1.0 - t) * p0.x + t * p1.x,
            (1.0 - t) * p0.y + t * p1.y
        };
    }
};

// Узагальнений алгоритм де Кастельжо для кривих Безьє довільного порядку n
// control_points: довільна кількість опорних точок (2 для відрізка, 3 для квадратичної, 4 для кубічної)
[[nodiscard]] Point2D evaluate_bezier_de_casteljau(std::span<const Point2D> control_points, double t) {
    if (control_points.empty()) {
        return {0.0, 0.0};
    }
    std::vector<Point2D> pts(control_points.begin(), control_points.end());
    for (size_t step = 1; step < control_points.size(); ++step) {
        for (size_t i = 0; i < control_points.size() - step; ++i) {
            pts[i] = lerp(pts[i], pts[i + 1], t);
        }
    }
    return pts.front();
}
