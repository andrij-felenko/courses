// 1. Глобальний фрагмент модуля (Global Module Fragment) — опціональний
module;

#include <cstdlib>
#include <sys/types.h>

// 2. Оголошення преамбули модуля (Module Preamble)
export module math.geometry;

// 3. Секція імпорту залежностей
import <cmath>;
import <vector>;

// 4. Сфера дії модуля (Module Purview)
export namespace math {

struct Point {
    double x{0.0};
    double y{0.0};
};

[[nodiscard]] export double distance(Point a, Point b) noexcept {
    const double dx = a.x - b.x;
    const double dy = a.y - b.y;
    return std::sqrt(dx * dx + dy * dy);
}

} // namespace math
