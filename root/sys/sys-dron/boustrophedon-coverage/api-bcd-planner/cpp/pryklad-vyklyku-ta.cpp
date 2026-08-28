#include "bcd_planner.hpp"
#include <iostream>
#include <vector>

int main() {
    using namespace robotics::coverage;

    PlannerConfig config{
        .swath_width = 12.0,
        .lateral_overlap = 0.6,
        .safety_margin = 2.0,
        .min_turn_radius = 5.0,
        .angle_mode = AngleMode::AutoMinTurns
    };

    BcdCoveragePlanner planner(config);

    const std::vector<Point2D> boundary = {
        { 0.0, 0.0 }, { 200.0, 0.0 }, { 200.0, 120.0 }, { 0.0, 120.0 }
    };
    if (auto res = planner.set_boundary(boundary); !res) {
        std::cerr << "Некоректна зовнішня межа!\n";
        return -1;
    }

    const std::vector<Point2D> obstacle = {
        { 80.0, 40.0 }, { 120.0, 40.0 }, { 120.0, 80.0 }, { 80.0, 80.0 }
    };
    planner.add_obstacle(obstacle);

    auto plan_result = planner.compute_plan();
    if (plan_result.has_value()) {
        const auto& waypoints = plan_result.value();
        auto metrics = planner.get_metrics().value();

        std::cout << "Успішно сплановано C++ місію:\n"
                  << "  Кількість точок: " << waypoints.size() << "\n"
                  << "  Кількість комірок: " << metrics.cell_count << "\n"
                  << "  Корисна площа: " << metrics.estimated_area_m2 << " м²\n";
    } else {
        std::cerr << "Помилка планування: " << static_cast<int>(plan_result.error()) << "\n";
    }

    return 0;
}
