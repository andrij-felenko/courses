#ifndef BCD_PLANNER_HPP
#define BCD_PLANNER_HPP

#include <span>
#include <vector>
#include <memory>
#include <expected>
#include <system_error>
#include <cmath>

namespace robotics::coverage {

enum class StatusCode {
    Ok = 0,
    InvalidArgument = -1,
    NonConvexHole = -2,
    SelfIntersecting = -3,
    OutOfMemory = -4,
    DecompositionFailed = -5,
    NoValidPath = -6
};

enum class AngleMode {
    Fixed,
    AutoLongestEdge,
    AutoMinTurns
};

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr bool operator==(const Point2D& other) const noexcept {
        return std::abs(x - other.x) < 1e-7 && std::abs(y - other.y) < 1e-7;
    }
};

struct PlannerConfig {
    double swath_width{10.0};
    double lateral_overlap{0.5};
    double safety_margin{1.0};
    double min_turn_radius{2.0};
    AngleMode angle_mode{AngleMode::AutoMinTurns};
    double custom_sweep_angle_rad{0.0};
};

struct CoverageMetrics {
    std::size_t cell_count{0};
    std::size_t stripe_count{0};
    std::size_t turn_count{0};
    double total_work_distance_m{0.0};
    double total_transit_distance_m{0.0};
    double estimated_area_m2{0.0};
};

class BcdCoveragePlanner {
public:
    explicit BcdCoveragePlanner(PlannerConfig config) noexcept;
    ~BcdCoveragePlanner() noexcept;

    BcdCoveragePlanner(const BcdCoveragePlanner&) = delete;
    BcdCoveragePlanner& operator=(const BcdCoveragePlanner&) = delete;

    BcdCoveragePlanner(BcdCoveragePlanner&&) noexcept;
    BcdCoveragePlanner& operator=(BcdCoveragePlanner&&) noexcept;

    std::expected<void, StatusCode> set_boundary(std::span<const Point2D> boundary);
    std::expected<void, StatusCode> add_obstacle(std::span<const Point2D> obstacle);
    void clear_obstacles() noexcept;

    std::expected<std::vector<Point2D>, StatusCode> compute_plan();
    [[nodiscard]] std::expected<CoverageMetrics, StatusCode> get_metrics() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace robotics::coverage

#endif /* BCD_PLANNER_HPP */
