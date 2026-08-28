#include <cmath>
#include <numbers>
#include <vector>
#include <span>
#include <optional>
#include <algorithm>

namespace drone::navigation {

struct RallyPoint {
    double lat{0.0};
    double lon{0.0};
    float alt_amsl_m{0.0f};
    float break_alt_m{50.0f};
    float landing_hdg_deg{0.0f};
    float clearance_radius_m{100.0f};
    uint8_t priority{5};
    bool is_active{true};
};

struct VehicleState {
    double lat{0.0};
    double lon{0.0};
    float alt_amsl_m{0.0f};
    float airspeed_m_s{18.0f};
    float remaining_energy_wh{200.0f};
    float cruise_power_w{150.0f};
    float climb_power_w{320.0f};
    float climb_rate_m_s{2.5f};
};

struct WindEstimate {
    float speed_m_s{0.0f};
    float dir_from_deg{0.0f};
};

struct EvaluatedRally {
    size_t original_index{0};
    float ground_speed_m_s{0.0f};
    float flight_time_s{0.0f};
    float energy_required_wh{0.0f};
    float score{0.0f};
    bool is_reachable{false};
};

class RallyPointRanker {
public:
    static constexpr float DEG_TO_RAD = std::numbers::pi_v<float> / 180.0f;
    static constexpr float RAD_TO_DEG = 180.0f / std::numbers::pi_v<float>;

    [[nodiscard]] static std::pair<float, float> calculate_distance_bearing(
        double lat1, double lon1, double lat2, double lon2) noexcept {
        const double dlat = (lat2 - lat1) * DEG_TO_RAD;
        const double dlon = (lon2 - lon1) * DEG_TO_RAD;
        const double mean_lat = (lat1 + lat2) * 0.5 * DEG_TO_RAD;

        const double x = dlon * std::cos(mean_lat) * 6371000.0;
        const double y = dlat * 6371000.0;

        const auto dist = static_cast<float>(std::hypot(x, y));
        auto brg = static_cast<float>(std::atan2(x, y) * RAD_TO_DEG);
        if (brg < 0.0f) brg += 360.0f;
        return {dist, brg};
    }

    [[nodiscard]] static std::optional<EvaluatedRally> evaluate(
        const RallyPoint& rp, size_t index,
        const VehicleState& vs, const WindEstimate& wind) noexcept {
        if (!rp.is_active) return std::nullopt;

        const auto [dist_m, track_deg] = calculate_distance_bearing(
            vs.lat, vs.lon, rp.lat, rp.lon);

        const float theta_rad = (track_deg - wind.dir_from_deg - 180.0f) * DEG_TO_RAD;
        const float sin_crab = (wind.speed_m_s / vs.airspeed_m_s) * std::sin(theta_rad);

        if (std::abs(sin_crab) >= 1.0f) {
            return std::nullopt; /* Неможливо скомпенсувати вітер */
        }

        const float crab_rad = std::asin(sin_crab);
        const float vg = vs.airspeed_m_s * std::cos(crab_rad) + wind.speed_m_s * std::cos(theta_rad);
        if (vg < 2.0f) {
            return std::nullopt; /* Недостатнє просування */
        }

        const float target_alt = rp.alt_amsl_m + rp.break_alt_m;
        const float delta_h = target_alt - vs.alt_amsl_m;
        const float t_climb = (delta_h > 0.0f) ? (delta_h / vs.climb_rate_m_s) : 0.0f;
        const float dist_climb = t_climb * vg;
        const float dist_cruise = (dist_m > dist_climb) ? (dist_m - dist_climb) : 0.0f;
        const float t_cruise = dist_cruise / vg;
        const float t_total = t_climb + t_cruise;

        const float e_climb = (vs.climb_power_w * t_climb) / 3600.0f;
        const float e_cruise = (vs.cruise_power_w * t_cruise) / 3600.0f;
        const float e_approach = (vs.cruise_power_w * 90.0f) / 3600.0f;
        const float e_total = e_climb + e_cruise + e_approach;

        const bool reachable = (e_total * 1.20f) <= vs.remaining_energy_wh;
        if (!reachable) return std::nullopt;

        const float wind_land_diff = (wind.dir_from_deg - rp.landing_hdg_deg) * DEG_TO_RAD;
        const float wind_align_cost = 0.5f * (1.0f - std::cos(wind_land_diff));

        const float energy_norm = e_total / vs.remaining_energy_wh;
        const float time_norm = t_total / 1800.0f;
        const float priority_norm = static_cast<float>(rp.priority) / 10.0f;

        const float score = 0.45f * energy_norm +
                            0.25f * wind_align_cost +
                            0.20f * time_norm -
                            0.10f * priority_norm;

        return EvaluatedRally{
            .original_index = index,
            .ground_speed_m_s = vg,
            .flight_time_s = t_total,
            .energy_required_wh = e_total,
            .score = score,
            .is_reachable = true
        };
    }

    [[nodiscard]] static std::vector<EvaluatedRally> rank_candidates(
        std::span<const RallyPoint> points,
        const VehicleState& vs,
        const WindEstimate& wind) {
        std::vector<EvaluatedRally> ranked;
        ranked.reserve(points.size());

        for (size_t i = 0; i < points.size(); ++i) {
            if (auto eval = evaluate(points[i], i, vs, wind); eval.has_value()) {
                ranked.push_back(*eval);
            }
        }

        std::ranges::sort(ranked, [](const auto& a, const auto& b) noexcept {
            return a.score < b.score;
        });

        return ranked;
    }
};

} // namespace drone::navigation
