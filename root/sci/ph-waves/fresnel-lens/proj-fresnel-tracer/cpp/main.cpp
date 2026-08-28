#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span >
#include <algorithm>

struct RayResult {
    double y_init{0.0};
    double y_focal{0.0};
    double intensity{1.0};
    bool is_lost{false};
};

class FresnelLensTracer {
public:
    struct Config {
        double focal_length{100.0};   // мм
        double refractive_index{1.49}; // PMMA
        double zone_pitch{0.5};        // крок зон p (мм)
        double draft_angle_deg{2.0};   // кут ухилу стінки (градуси)
        std::size_t num_zones{40};     // кількість зон
    };

    explicit FresnelLensTracer(Config cfg) : config_(cfg) {}

    [[nodiscard]] std::vector<RayResult> trace_beam(std::size_t num_rays) const {
        std::vector<RayResult> results(num_rays);
        const double max_r = config_.num_zones * config_.zone_pitch;
        const double dy = max_r / static_cast<double>(num_rays);
        const double draft_rad = config_.draft_angle_deg * std::numbers::pi / 180.0;

        for (std::size_t i = 0; i < num_rays; ++i) {
            const double y = (static_cast<double>(i) + 0.5) * dy;
            const auto zone_idx = static_cast<std::size_t>(y / config_.zone_pitch);
            const double r_zone = (static_cast<double>(zone_idx) + 0.5) * config_.zone_pitch;

            const double alpha = compute_facet_angle(r_zone);
            const double h_step = config_.zone_pitch * std::tan(alpha);
            const double shadow_width = h_step * std::tan(draft_rad);
            const double y_in_zone = std::fmod(y, config_.zone_pitch);

            results[i].y_init = y;

            if (y_in_zone > (config_.zone_pitch - shadow_width)) {
                results[i].is_lost = true;
                results[i].intensity = 0.0;
            } else {
                const double n_x = -std::sin(alpha);
                const double n_y = std::cos(alpha);
                const double cos_th1 = n_y;
                const double sin_th1_sq = 1.0 - cos_th1 * cos_th1;
                const double sin_th2_sq = sin_th1_sq / (config_.refractive_index * config_.refractive_index);

                if (sin_th2_sq > 1.0) {
                    results[i].is_lost = true;
                    results[i].intensity = 0.0;
                    continue;
                }

                const double cos_th2 = std::sqrt(1.0 - sin_th2_sq);
                const double gamma = cos_th1 - config_.refractive_index * cos_th2;
                const double rx = (1.0 / config_.refractive_index) + gamma * n_x;
                const double ry = gamma * n_y;

                results[i].y_focal = y + (ry / rx) * config_.focal_length;
            }
        }
        return results;
    }

    [[nodiscard]] static double compute_efficiency(std::span<const RayResult> rays) {
        if (rays.empty()) return 0.0;
        const auto passed = std::count_if(rays.begin(), rays.end(), [](const auto& r) { return !r.is_lost; });
        return static_cast<double>(passed) / static_cast<double>(rays.size());
    }

private:
    Config config_;

    [[nodiscard]] double compute_facet_angle(double r) const {
        const double theta = std::atan(r / config_.focal_length);
        return std::atan2(std::sin(theta), config_.refractive_index - std::cos(theta));
    }
};
