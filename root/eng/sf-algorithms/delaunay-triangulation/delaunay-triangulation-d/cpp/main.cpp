#include <vector>
#include <span>
#include <cmath>
#include <algorithm>
#include <optional>

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr double dist_sq(const Point2D& other) const noexcept {
        const double dx = x - other.x;
        const double dy = y - other.y;
        return dx * dx + dy * dy;
    }
};

struct Triangle {
    std::size_t a{0};
    std::size_t b{0};
    std::size_t c{0};
};

class DelaunayGeometry {
public:
    /* Предикат 2D-орієнтації (поворот CCW) */
    [[nodiscard]] static constexpr double orient2d(Point2D a, Point2D b, Point2D c) noexcept {
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    }

    /* Предикат InCircle: строго > 0 означає, що d всередині кола abc */
    [[nodiscard]] static double incircle(Point2D a, Point2D b, Point2D c, Point2D d) noexcept {
        if (orient2d(a, b, c) < 0.0) {
            std::swap(b, c);
        }

        const double adx = a.x - d.x, ady = a.y - d.y;
        const double bdx = b.x - d.x, bdy = b.y - d.y;
        const double cdx = c.x - d.x, cdy = c.y - d.y;

        const double ab_det = adx * bdy - ady * bdx;
        const double bc_det = bdx * cdy - bdy * cdx;
        const double ca_det = cdx * ady - cdy * adx;

        const double alift = adx * adx + ady * ady;
        const double blift = bdx * bdx + bdy * bdy;
        const double clift = cdx * cdx + cdy * cdy;

        return alift * bc_det + blift * ca_det + clift * ab_det;
    }

    /* Перевірка легальності ребра */
    [[nodiscard]] static bool is_edge_legal(Point2D a, Point2D b, Point2D c, Point2D d) noexcept {
        return incircle(a, b, c, d) <= 1e-12;
    }
};
