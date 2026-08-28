#include <iostream>
#include <cmath>
#include <algorithm>

struct QuickPcbSpec {
    double width_mm{0.0};
    double height_mm{0.0};
    int layer_count{2};
    double copper_oz{1.0};
    double min_trace_mil{6.0};
    int quantity{100};
    int turnaround_hours{120};
};

[[nodiscard]] constexpr double calculate_quick_estimate(const QuickPcbSpec& s) noexcept {
    constexpr double panel_w = 457.0 - 25.0; // 18" мінус поля
    constexpr double panel_h = 610.0 - 25.0; // 24" мінус поля

    const int nx = static_cast<int>(std::floor((panel_w + 2.0) / (s.width_mm + 2.0)));
    const int ny = static_cast<int>(std::floor((panel_h + 2.0) / (s.height_mm + 2.0)));
    const int per_panel = std::max(1, nx * ny);

    const double layer_factor = 1.0 + 0.45 * static_cast<double>(s.layer_count > 2 ? s.layer_count - 2 : 0);
    const double cu_factor = 1.0 + 0.40 * std::max(0.0, s.copper_oz - 1.0);
    const double rush_factor = (s.turnaround_hours <= 48) ? 2.5 : 1.0;

    const double panel_base_cost = 45.0 * layer_factor * cu_factor * rush_factor;
    const double nre_base = (s.layer_count > 2 ? 150.0 : 60.0) * rush_factor;

    const int panels = (s.quantity + per_panel - 1) / per_panel;
    const double total = nre_base + static_cast<double>(panels) * panel_base_cost;

    return total / static_cast<double>(s.quantity);
}
