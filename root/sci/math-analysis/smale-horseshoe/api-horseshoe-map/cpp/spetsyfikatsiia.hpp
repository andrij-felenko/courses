#ifndef HORSESHOE_HPP
#define HORSESHOE_HPP

#include <cmath>
#include <expected>
#include <optional>
#include <span>
#include <utility>
#include <vector>

namespace physics::mechanics {

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct Config {
    double alpha{0.35};
    double beta{2.4};
};

enum class MappingStatus {
    Success,
    OutOfBounds,
    EscapedDomain,
    InvalidParameter
};

class HorseshoeMap {
public:
    explicit HorseshoeMap(Config cfg) : config_(cfg) {}

    [[nodiscard]] std::expected<Point2D, MappingStatus> forward(const Point2D& pt) const noexcept {
        if (pt.x < 0.0 || pt.x > 1.0 || pt.y < 0.0 || pt.y > 1.0) {
            return std::unexpected(MappingStatus::OutOfBounds);
        }

        if (pt.y >= 0.0 && pt.y <= config_.alpha) {
            return Point2D{config_.alpha * pt.x, config_.beta * pt.y};
        }
        if (pt.y >= (1.0 - config_.alpha) && pt.y <= 1.0) {
            return Point2D{1.0 - config_.alpha * pt.x, config_.beta * (1.0 - pt.y)};
        }

        return std::unexpected(MappingStatus::EscapedDomain);
    }

    [[nodiscard]] std::expected<Point2D, MappingStatus> inverse(const Point2D& pt) const noexcept {
        if (pt.x < 0.0 || pt.x > 1.0 || pt.y < 0.0 || pt.y > 1.0) {
            return std::unexpected(MappingStatus::OutOfBounds);
        }

        if (pt.x >= 0.0 && pt.x <= config_.alpha) {
            return Point2D{pt.x / config_.alpha, pt.y / config_.beta};
        }
        if (pt.x >= (1.0 - config_.alpha) && pt.x <= 1.0) {
            return Point2D{(1.0 - pt.x) / config_.alpha, 1.0 - (pt.y / config_.beta)};
        }

        return std::unexpected(MappingStatus::EscapedDomain);
    }

    [[nodiscard]] std::pair<double, double> lyapunovExponents() const noexcept {
        return {std::log(config_.alpha), std::log(config_.beta)};
    }

    [[nodiscard]] Point2D reconstructFromSymbolicCode(std::span<const int> code_future,
                                                      std::span<const int> code_past) const noexcept {
        double x = 0.0;
        double alpha_power = 1.0;
        for (int s : code_future) {
            if (s == 1) {
                x += alpha_power * (1.0 - config_.alpha);
            }
            alpha_power *= config_.alpha;
        }

        double y = 0.0;
        double beta_power = 1.0 / config_.beta;
        for (int s : code_past) {
            if (s == 1) {
                y += beta_power;
            }
            beta_power /= config_.beta;
        }

        return Point2D{x, y};
    }

    [[nodiscard]] double capacityDimension() const noexcept {
        const double d_x = std::log(2.0) / std::log(1.0 / config_.alpha);
        const double d_y = std::log(2.0) / std::log(config_.beta);
        return d_x + d_y;
    }

private:
    Config config_;
};

} // namespace physics::mechanics

#endif /* HORSESHOE_HPP */
