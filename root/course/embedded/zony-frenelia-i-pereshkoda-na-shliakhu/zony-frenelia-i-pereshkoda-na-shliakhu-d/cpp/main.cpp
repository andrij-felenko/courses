#include <cmath>
#include <numbers>
#include <optional>
#include <span>
#include <vector>

struct TerrainPoint {
    double dist_from_tx_m{0.0};
    double ground_alt_m{0.0};
    double clutter_height_m{0.0};
};

struct ClearanceResult {
    double r1_radius_m{0.0};
    double earth_bulge_m{0.0};
    double los_height_m{0.0};
    double obstacle_top_m{0.0};
    double clearance_m{0.0};
    double clearance_ratio{0.0};
    double diffraction_loss_db{0.0};
    bool is_60_percent_clear{false};
};

class FresnelClearanceCalculator {
public:
    static constexpr double SpeedOfLight = 299792458.0;
    static constexpr double EarthEffectiveRadius = 8495000.0; // 4/3 * R_earth

    static constexpr double calculate_itu_loss(double v) noexcept {
        if (v <= -0.78) {
            return 0.0;
        }
        const double term = std::sqrt((v - 0.1) * (v - 0.1) + 1.0) + (v - 0.1);
        return 6.9 + 20.0 * std::log10(term);
    }

    [[nodiscard]] static ClearanceResult evaluate_point(
        double freq_hz,
        double total_dist_m,
        double tx_alt_m,
        double rx_alt_m,
        const TerrainPoint& obstacle
    ) noexcept {
        const double lambda = SpeedOfLight / freq_hz;
        const double d1 = obstacle.dist_from_tx_m;
        const double d2 = total_dist_m - d1;

        ClearanceResult res;
        res.r1_radius_m = std::sqrt((lambda * d1 * d2) / total_dist_m);
        res.earth_bulge_m = (d1 * d2) / (2.0 * EarthEffectiveRadius);

        const double slope = (rx_alt_m - tx_alt_m) / total_dist_m;
        res.los_height_m = tx_alt_m + slope * d1;
        res.obstacle_top_m = obstacle.ground_alt_m + obstacle.clutter_height_m + res.earth_bulge_m;

        res.clearance_m = res.los_height_m - res.obstacle_top_m;
        res.clearance_ratio = res.clearance_m / res.r1_radius_m;

        const double h_obstacle = -res.clearance_m;
        const double v = std::numbers::sqrt2 * (h_obstacle / res.r1_radius_m);

        res.diffraction_loss_db = calculate_itu_loss(v);
        res.is_60_percent_clear = (res.clearance_ratio >= 0.60);

        return res;
    }

    [[nodiscard]] static ClearanceResult find_worst_obstacle(
        double freq_hz,
        double total_dist_m,
        double tx_alt_m,
        double rx_alt_m,
        std::span<const TerrainPoint> profile
    ) noexcept {
        ClearanceResult worst{};
        double max_loss = -1.0;

        for (const auto& point : profile) {
            if (point.dist_from_tx_m <= 0.0 || point.dist_from_tx_m >= total_dist_m) {
                continue;
            }
            auto current = evaluate_point(freq_hz, total_dist_m, tx_alt_m, rx_alt_m, point);
            if (current.diffraction_loss_db > max_loss) {
                max_loss = current.diffraction_loss_db;
                worst = current;
            }
        }
        return worst;
    }
};
