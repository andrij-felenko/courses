#include <iostream>
#include <cmath>
#include <string>
#include <string_view>
#include <vector>
#include <format>
#include <optional>

namespace eda {

struct CopperPrimitive {
    double x_min{0.0};
    double y_min{0.0};
    double x_max{0.0};
    double y_max{0.0};
    int net_id{0};
    std::string label;

    [[nodiscard]] double distance_to(const CopperPrimitive& other) const noexcept {
        double dx = 0.0;
        if (x_max < other.x_min) {
            dx = other.x_min - x_max;
        } else if (other.x_max < x_min) {
            dx = x_min - other.x_max;
        }

        double dy = 0.0;
        if (y_max < other.y_min) {
            dy = other.y_min - y_max;
        } else if (other.y_max < y_min) {
            dy = y_min - other.y_max;
        }

        return std::hypot(dx, dy);
    }
};

class DrcEngine {
public:
    static std::optional<std::string> check_pair(const CopperPrimitive& a,
                                                const CopperPrimitive& b,
                                                double min_clearance) {
        if (a.net_id == b.net_id) {
            return std::nullopt;
        }

        double actual_dist = a.distance_to(b);
        if (actual_dist < min_clearance) {
            return std::format("DRC VIOLATION: '{}' (Net {}) vs '{}' (Net {}) distance {:.3f} mm < limit {:.3f} mm",
                               a.label, a.net_id, b.label, b.net_id, actual_dist, min_clearance);
        }
        return std::nullopt;
    }
};

} // namespace eda
