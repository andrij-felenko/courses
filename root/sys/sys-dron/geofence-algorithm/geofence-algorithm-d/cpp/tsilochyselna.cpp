// Ідіоматична C++20 версія алгоритму перевірки належності точки полігону.
// Використовує std::span для безпечного доступу та constexpr для обчислень.

#include <span>
#include <cstdint>

namespace drone::geometry {

struct Point2D {
    std::int32_t x{0};
    std::int32_t y{0};
};

[[nodiscard]] constexpr bool is_point_in_polygon(Point2D p,
                                                 std::span<const Point2D> polygon) noexcept {
    const std::size_t n = polygon.size();
    if (n < 3) [[unlikely]] {
        return false;
    }

    bool inside = false;
    std::size_t j = n - 1;

    for (std::size_t i = 0; i < n; ++i) {
        const auto& vi = polygon[i];
        const auto& vj = polygon[j];

        if ((vi.y <= p.y && p.y < vj.y) || (vj.y <= p.y && p.y < vi.y)) {
            const std::int64_t cross = static_cast<std::int64_t>(p.x - vi.x) * (vj.y - vi.y) -
                                       static_cast<std::int64_t>(p.y - vi.y) * (vj.x - vi.x);

            if (vi.y < vj.y) {
                if (cross < 0) {
                    inside = !inside;
                }
            } else {
                if (cross > 0) {
                    inside = !inside;
                }
            }
        }
        j = i;
    }
    return inside;
}

} // namespace drone::geometry
