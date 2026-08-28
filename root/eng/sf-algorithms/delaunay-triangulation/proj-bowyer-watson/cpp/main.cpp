#include <vector>
#include <span>
#include <cmath>
#include <algorithm>
#include <optional>
#include <iostream>

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr bool operator==(const Point2D& other) const noexcept {
        return std::abs(x - other.x) < 1e-9 && std::abs(y - other.y) < 1e-9;
    }
};

struct Edge2D {
    Point2D a{};
    Point2D b{};

    [[nodiscard]] constexpr bool operator==(const Edge2D& other) const noexcept {
        return (a == other.a && b == other.b) || (a == other.b && b == other.a);
    }
};

struct Triangle2D {
    Point2D a{};
    Point2D b{};
    Point2D c{};

    [[nodiscard]] constexpr bool has_vertex(const Point2D& p) const noexcept {
        return a == p || b == p || c == p;
    }
};

class DelaunayTriangulator {
public:
    [[nodiscard]] static std::vector<Triangle2D> triangulate(std::span<const Point2D> points) {
        if (points.empty()) return {};

        auto [min_x, max_x] = std::minmax_element(points.begin(), points.end(),
            [](const Point2D& p1, const Point2D& p2) { return p1.x < p2.x; });
        auto [min_y, max_y] = std::minmax_element(points.begin(), points.end(),
            [](const Point2D& p1, const Point2D& p2) { return p1.y < p2.y; });

        const double dx = max_x->x - min_x->x;
        const double dy = max_y->y - min_y->y;
        const double delta_max = std::max(std::max(dx, dy) * 20.0, 100.0);
        const double mid_x = (min_x->x + max_x->x) * 0.5;
        const double mid_y = (min_y->y + max_y->y) * 0.5;

        /* Супертрикутник */
        const Point2D st_a{ mid_x - delta_max, mid_y - delta_max };
        const Point2D st_b{ mid_x + delta_max, mid_y - delta_max };
        const Point2D st_c{ mid_x, mid_y + delta_max };

        std::vector<Triangle2D> mesh;
        mesh.push_back(Triangle2D{ st_a, st_b, st_c });

        std::vector<Edge2D> cavity_edges;

        for (const auto& pt : points) {
            cavity_edges.clear();

            /* Відбір поганих трикутників */
            auto it = std::remove_if(mesh.begin(), mesh.end(),
                [&pt, &cavity_edges](const Triangle2D& t) {
                    if (in_circumcircle(t.a, t.b, t.c, pt)) {
                        cavity_edges.push_back(Edge2D{ t.a, t.b });
                        cavity_edges.push_back(Edge2D{ t.b, t.c });
                        cavity_edges.push_back(Edge2D{ t.c, t.a });
                        return true;
                    }
                    return false;
                });
            mesh.erase(it, mesh.end());

            /* Пошук унікальних межових ребер */
            for (std::size_t i = 0; i < cavity_edges.size(); ++i) {
                bool is_shared = false;
                for (std::size_t j = 0; j < cavity_edges.size(); ++j) {
                    if (i != j && cavity_edges[i] == cavity_edges[j]) {
                        is_shared = true;
                        break;
                    }
                }
                if (!is_shared) {
                    mesh.push_back(Triangle2D{ cavity_edges[i].a, cavity_edges[i].b, pt });
                }
            }
        }

        /* Видалення трикутників із вершинами супертрикутника */
        std::erase_if(mesh, [&](const Triangle2D& t) {
            return t.has_vertex(st_a) || t.has_vertex(st_b) || t.has_vertex(st_c);
        });

        return mesh;
    }

private:
    [[nodiscard]] static constexpr double orientation_ccw(Point2D a, Point2D b, Point2D c) noexcept {
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    }

    [[nodiscard]] static bool in_circumcircle(Point2D a, Point2D b, Point2D c, Point2D d) noexcept {
        if (orientation_ccw(a, b, c) < 0.0) {
            std::swap(b, c);
        }

        const double adx = a.x - d.x;
        const double ady = a.y - d.y;
        const double bdx = b.x - d.x;
        const double bdy = b.y - d.y;
        const double cdx = c.x - d.x;
        const double cdy = c.y - d.y;

        const double ab_det = adx * bdy - ady * bdx;
        const double bc_det = bdx * cdy - bdy * cdx;
        const double ca_det = cdx * ady - cdy * adx;

        const double alift = adx * adx + ady * ady;
        const double blift = bdx * bdx + bdy * bdy;
        const double clift = cdx * cdx + cdy * cdy;

        const double det = alift * bc_det + blift * ca_det + clift * ab_det;
        return det > 1e-12;
    }
};
