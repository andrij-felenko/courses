#include <vector>
#include <stdexcept>

struct Vec2 { double x{}, y{}; };
struct Centroid { Vec2 c; double area; };    // area — знакова

Centroid polygon_centroid(const std::vector<Vec2>& p) {
    const std::size_t n = p.size();
    double a2 = 0.0, cx = 0.0, cy = 0.0;      // a2 = 2·(знакова площа)
    for (std::size_t i = 0; i < n; ++i) {
        const Vec2& a = p[i];
        const Vec2& b = p[(i + 1) % n];       // наступна вершина (обвід замкнено)
        const double cross = a.x * b.y - b.x * a.y;
        a2 += cross;
        cx += (a.x + b.x) * cross;
        cy += (a.y + b.y) * cross;
    }
    if (a2 == 0.0) throw std::invalid_argument("вироджений контур: нульова площа");
    return { { cx / (3.0 * a2), cy / (3.0 * a2) }, a2 / 2.0 };
}
