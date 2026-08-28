#include <cmath>
#include <numbers>
#include <vector>
#include <span>
#include <optional>
#include <algorithm>
#include <chrono>

namespace drone::navigation {

struct RallyPointDefinition {
    double latitude_deg{0.0};
    double longitude_deg{0.0};
    float altitude_amsl_m{0.0f};
    float break_alt_agl_m{50.0f};
    float landing_heading_deg{0.0f};
    float clearance_radius_m{100.0f};
    uint8_t priority{5};
    bool is_active{true};
};

struct VehicleFlightStatus {
    double current_lat{0.0};
    double current_lon{0.0};
    float current_alt_amsl_m{0.0f};
    float cruise_airspeed_m_s{18.0f};
    float climb_rate_m_s{2.5f};
    float cruise_power_w{150.0f};
    float climb_power_w{320.0f};
    float remaining_energy_wh{200.0f};
    float battery_voltage_v{22.2f};
    float battery_internal_res_ohm{0.025f};
};

struct WindConditions {
    float wind_speed_m_s{0.0f};
    float wind_from_direction_deg{0.0f};
};

struct RallyCandidateEvaluation {
    size_t point_index{0};
    float distance_to_point_m{0.0f};
    float ground_speed_m_s{0.0f};
    float flight_time_s{0.0f};
    float total_energy_wh{0.0f};
    float final_score{0.0f};
    bool is_feasible{false};
};

class RallyPointSelector {
public:
    static constexpr float DEG_TO_RAD = std::numbers::pi_v<float> / 180.0f;
    static constexpr float RAD_TO_DEG = 180.0f / std::numbers::pi_v<float>;

    explicit RallyPointSelector(float hysteresis_delta_j = 0.08f,
                                float hold_threshold_s = 3.0f) noexcept
        : hysteresis_delta_{hysteresis_delta_j}
        , hold_threshold_s_{hold_threshold_s} {}

    void set_points(std::vector<RallyPointDefinition> points) {
        registry_ = std::move(points);
        active_index_ = std::nullopt;
        pending_index_ = std::nullopt;
        pending_duration_s_ = 0.0f;
    }

    [[nodiscard]] static std::pair<float, float> calculate_distance_azimuth(
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

    [[nodiscard]] static std::optional<RallyCandidateEvaluation> evaluate_point(
        const RallyPointDefinition& rp, size_t index,
        const VehicleFlightStatus& vs,
        const WindConditions& wind) noexcept {
        if (!rp.is_active) return std::nullopt;

        const auto [dist_m, track_deg] = calculate_distance_azimuth(
            vs.current_lat, vs.current_lon, rp.latitude_deg, rp.longitude_deg);

        const float theta_rad = (track_deg - wind.wind_from_direction_deg - 180.0f) * DEG_TO_RAD;
        const float sin_crab = (wind.wind_speed_m_s / vs.cruise_airspeed_m_s) * std::sin(theta_rad);

        if (std::abs(sin_crab) >= 1.0f) return std::nullopt;

        const float crab_angle_rad = std::asin(sin_crab);
        const float vg = vs.cruise_airspeed_m_s * std::cos(crab_angle_rad) +
                         wind.wind_speed_m_s * std::cos(theta_rad);

        if (vg < 2.0f) return std::nullopt;

        const float target_alt = rp.altitude_amsl_m + rp.break_alt_agl_m;
        const float delta_h = target_alt - vs.current_alt_amsl_m;
        const float t_climb = (delta_h > 0.0f && vs.climb_rate_m_s > 0.1f)
                              ? (delta_h / vs.climb_rate_m_s) : 0.0f;

        const float dist_during_climb = t_climb * vg;
        const float dist_cruise = (dist_m > dist_during_climb) ? (dist_m - dist_during_climb) : 0.0f;
        const float t_cruise = dist_cruise / vg;
        const float t_total = t_climb + t_cruise;

        const float e_climb = (vs.climb_power_w * t_climb) / 3600.0f;
        const float e_cruise = (vs.cruise_power_w * t_cruise) / 3600.0f;
        const float e_land_reserve = (vs.cruise_power_w * 90.0f) / 3600.0f;
        const float e_total = e_climb + e_cruise + e_land_reserve;

        if ((e_total * 1.20f) > vs.remaining_energy_wh) return std::nullopt;

        const float wind_heading_diff = (wind.wind_from_direction_deg - rp.landing_heading_deg) * DEG_TO_RAD;
        const float wind_align_cost = 0.5f * (1.0f - std::cos(wind_heading_diff));

        const float energy_ratio = e_total / vs.remaining_energy_wh;
        const float time_ratio = t_total / 1800.0f;
        const float priority_ratio = static_cast<float>(rp.priority) / 10.0f;

        const float score = (0.45f * energy_ratio) +
                            (0.25f * wind_align_cost) +
                            (0.20f * time_ratio) -
                            (0.10f * priority_ratio);

        return RallyCandidateEvaluation{
            .point_index = index,
            .distance_to_point_m = dist_m,
            .ground_speed_m_s = vg,
            .flight_time_s = t_total,
            .total_energy_wh = e_total,
            .final_score = score,
            .is_feasible = true
        };
    }

    [[nodiscard]] std::optional<size_t> update(
        const VehicleFlightStatus& status,
        const WindConditions& wind,
        float dt_s) noexcept {
        if (registry_.empty()) return std::nullopt;

        std::optional<RallyCandidateEvaluation> best_eval;

        for (size_t i = 0; i < registry_.size(); ++i) {
            if (auto eval = evaluate_point(registry_[i], i, status, wind); eval.has_value()) {
                if (!best_eval.has_value() || eval->final_score < best_eval->final_score) {
                    best_eval = eval;
                }
            }
        }

        if (!best_eval.has_value()) {
            return std::nullopt;
        }

        if (!active_index_.has_value()) {
            active_index_ = best_eval->point_index;
            pending_index_ = std::nullopt;
            pending_duration_s_ = 0.0f;
            return active_index_;
        }

        const auto current_eval = evaluate_point(
            registry_[*active_index_], *active_index_, status, wind);

        if (!current_eval.has_value()) {
            active_index_ = best_eval->point_index;
            pending_index_ = std::nullopt;
            pending_duration_s_ = 0.0f;
            return active_index_;
        }

        if (best_eval->point_index == *active_index_) {
            pending_index_ = std::nullopt;
            pending_duration_s_ = 0.0f;
            return active_index_;
        }

        if (best_eval->final_score < (current_eval->final_score - hysteresis_delta_)) {
            if (pending_index_.has_value() && *pending_index_ == best_eval->point_index) {
                pending_duration_s_ += dt_s;
                if (pending_duration_s_ >= hold_threshold_s_) {
                    active_index_ = best_eval->point_index;
                    pending_index_ = std::nullopt;
                    pending_duration_s_ = 0.0f;
                }
            } else {
                pending_index_ = best_eval->point_index;
                pending_duration_s_ = 0.0f;
            }
        } else {
            pending_index_ = std::nullopt;
            pending_duration_s_ = 0.0f;
        }

        return active_index_;
    }

    [[nodiscard]] std::span<const RallyPointDefinition> points() const noexcept {
        return registry_;
    }

private:
    std::vector<RallyPointDefinition> registry_;
    std::optional<size_t> active_index_{std::nullopt};
    std::optional<size_t> pending_index_{std::nullopt};
    float pending_duration_s_{0.0f};
    float hysteresis_delta_{0.08f};
    float hold_threshold_s_{3.0f};
};

} // namespace drone::navigation
