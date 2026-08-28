#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <format>
#include <string_view>

namespace ecad_mcad {

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

struct Mat4 {
    std::array<std::array<double, 4>, 4> m{};

    [[nodiscard]] constexpr Vec3 transform_point(const Vec3& pt) const noexcept {
        return Vec3{
            .x = m[0][0] * pt.x + m[0][1] * pt.y + m[0][2] * pt.z + m[0][3],
            .y = m[1][0] * pt.x + m[1][1] * pt.y + m[1][2] * pt.z + m[1][3],
            .z = m[2][0] * pt.x + m[2][1] * pt.y + m[2][2] * pt.z + m[2][3]
        };
    }
};

struct Plane {
    Vec3 normal{0.0, 0.0, 1.0};
    double d{0.0}; // A*x + B*y + C*z + d = 0

    [[nodiscard]] double distance_to(const Vec3& pt) const noexcept {
        const double num = normal.x * pt.x + normal.y * pt.y + normal.z * pt.z + d;
        const double den = std::sqrt(normal.x * normal.x + normal.y * normal.y + normal.z * normal.z);
        return (den > 1e-9) ? (num / den) : 0.0;
    }
};

struct BoundingBox3D {
    Vec3 min_pt;
    Vec3 max_pt;

    [[nodiscard]] std::array<Vec3, 8> get_corners() const noexcept {
        return {
            Vec3{min_pt.x, min_pt.y, min_pt.z},
            Vec3{max_pt.x, min_pt.y, min_pt.z},
            Vec3{min_pt.x, max_pt.y, min_pt.z},
            Vec3{max_pt.x, max_pt.y, min_pt.z},
            Vec3{min_pt.x, min_pt.y, max_pt.z},
            Vec3{max_pt.x, min_pt.y, max_pt.z},
            Vec3{min_pt.x, max_pt.y, max_pt.z},
            Vec3{max_pt.x, max_pt.y, max_pt.z}
        };
    }
};

class ClearanceAnalyzer {
public:
    explicit ClearanceAnalyzer(Mat4 board_to_chassis, Plane chassis_lid)
        : transform_(board_to_chassis), lid_(chassis_lid) {}

    [[nodiscard]] std::pair<bool, double> evaluate_component_clearance(
        const BoundingBox3D& comp_bbox, double min_allowed_clearance) const noexcept {
        
        double min_dist = 1e9;
        const auto corners = comp_bbox.get_corners();

        for (const auto& local_pt : corners) {
            const Vec3 world_pt = transform_.transform_point(local_pt);
            const double dist = lid_.distance_to(world_pt);
            min_dist = std::min(min_dist, dist);
        }

        const bool is_safe = (min_dist >= min_allowed_clearance);
        return {is_safe, min_dist};
    }

private:
    Mat4 transform_;
    Plane lid_;
};

} // namespace ecad_mcad

int main() {
    using namespace ecad_mcad;

    Mat4 board_placement{};
    board_placement.m = {{
        {1.0, 0.0, 0.0, 0.0},
        {0.0, 1.0, 0.0, 0.0},
        {0.0, 0.0, 1.0, 5.0}, // Стійки H = 5.0 мм
        {0.0, 0.0, 0.0, 1.0}
    }};

    Plane chassis_lid{
        .normal = {0.0, 0.0, -1.0},
        .d = 22.0 // Висота внутрішньої площини кришки Z = 22.0 мм
    };

    BoundingBox3D capacitor_bbox{
        .min_pt = {40.0, 20.0, 0.0},
        .max_pt = {50.0, 30.0, 15.5} // Конденсатор H = 15.5 мм
    };

    ClearanceAnalyzer analyzer(board_placement, chassis_lid);
    constexpr double kMinRequiredClearance = 1.0; // мм

    const auto [passed, actual_clearance] =
        analyzer.evaluate_component_clearance(capacitor_bbox, kMinRequiredClearance);

    std::cout << "=================================================================\n";
    std::cout << "   АНАЛІЗ ПРОСТОРОВОГО ЗАЗОРУ (C++20 CLEARANCE ANALYZER)        \n";
    std::cout << "=================================================================\n";
    std::cout << std::format("Висота стійок плати:                  {:6.2f} мм\n", board_placement.m[2][3]);
    std::cout << std::format("Висота деталі над платою:             {:6.2f} мм\n", capacitor_bbox.max_pt.z);
    std::cout << std::format("Абсолютна координата верхівки Z:      {:6.2f} мм\n", board_placement.m[2][3] + capacitor_bbox.max_pt.z);
    std::cout << std::format("Положення кришки корпусу Z:           {:6.2f} мм\n", chassis_lid.d);
    std::cout << "-----------------------------------------------------------------\n";
    std::cout << std::format("Фактичний зазор до кришки:            {:6.2f} мм\n", actual_clearance);
    std::cout << std::format("Мінімально допустимий зазор:          {:6.2f} мм\n", kMinRequiredClearance);
    std::cout << std::format("Статус перевірки:                     {}\n",
                             passed ? "[PASS] В НОРМІ" : "[FAIL] КОЛІЗІЯ!");
    std::cout << "=================================================================\n";

    return passed ? 0 : 1;
}
