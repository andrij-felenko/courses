#include <vector>
#include <span>
#include <cmath>
#include <optional>
#include <algorithm>

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr double dist_sq(const Point2D& other) const noexcept {
        const double dx = x - other.x;
        const double dy = y - other.y;
        return dx * dx + dy * dy;
    }
};

struct VoronoiEdge {
    Point2D start{};
    Point2D end{};
    std::size_t site_a{0};
    std::size_t site_b{0};
    bool is_ray{false};
};

class VoronoiDiagram {
public:
    explicit VoronoiDiagram(std::vector<Point2D> sites) : sites_(std::move(sites)) {}

    [[nodiscard]] std::span<const Point2D> sites() const noexcept { return sites_; }
    [[nodiscard]] std::span<const VoronoiEdge> edges() const noexcept { return edges_; }

    /* Пошук найближчого сайта прямим проходом (еталон для верифікації) */
    [[nodiscard]] std::optional<std::size_t> find_nearest_linear(Point2D query) const noexcept {
        if (sites_.empty()) return std::nullopt;

        auto it = std::min_element(sites_.begin(), sites_.end(),
            [&query](const Point2D& a, const Point2D& b) noexcept {
                return a.dist_sq(query) < b.dist_sq(query);
            });

        return std::distance(sites_.begin(), it);
    }

private:
    std::vector<Point2D> sites_;
    std::vector<VoronoiEdge> edges_;
};
