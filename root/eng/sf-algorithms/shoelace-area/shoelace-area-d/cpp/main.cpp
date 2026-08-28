#include <cmath>
#include <cstddef>
#include <optional>
#include <span>
#include <vector>

namespace geom {

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct PolygonMetrics {
    double signed_area{0.0}; // орієнтована площа (>0: CCW, <0: CW)
    double abs_area{0.0};    // абсолютна площа
    Point2D centroid{};      // геометричний центроїд
    bool is_ccw{false};      // прапорець орієнтації проти годинникової стрілки
};

// Обчислення характеристик багатокутника через std::span без зайвих алокацій.
// Приймає будь-які неперервні контейнери: std::vector, std::array, C-масиви.
[[nodiscard]] constexpr std::optional<PolygonMetrics> 
calculate_polygon_metrics(std::span<const Point2D> vertices) noexcept {
    if (vertices.size() < 3) {
        return std::nullopt;
    }

    double double_area = 0.0;
    double cx_accum = 0.0;
    double cy_accum = 0.0;

    // Локальний зсув для числової стабільності
    const double x0 = vertices[0].x;
    const double y0 = vertices[0].y;
    const std::size_t count = vertices.size();

    for (std::size_t i = 0; i < count; ++i) {
        const std::size_t next = (i + 1 == count) ? 0 : (i + 1);

        const double xi = vertices[i].x - x0;
        const double yi = vertices[i].y - y0;
        const double x_next = vertices[next].x - x0;
        const double y_next = vertices[next].y - y0;

        // Обчислення косого добутку
        const double cross = (xi * y_next) - (x_next * yi);

        double_area += cross;
        cx_accum += (xi + x_next) * cross;
        cy_accum += (yi + y_next) * cross;
    }

    PolygonMetrics result{};
    result.signed_area = double_area * 0.5;
    result.abs_area = std::abs(result.signed_area);
    result.is_ccw = (result.signed_area > 0.0);

    if (std::abs(double_area) > 1e-12) {
        const double factor = 1.0 / (3.0 * double_area);
        result.centroid.x = x0 + (cx_accum * factor);
        result.centroid.y = y0 + (cy_accum * factor);
    } else {
        result.centroid.x = x0;
        result.centroid.y = y0;
    }

    return result;
}

} // namespace geom
