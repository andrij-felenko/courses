#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <array>

namespace drone::navigation {

inline constexpr double EarthRadiusM = 6371000.0;
inline constexpr double DegToRad = std::numbers::pi / 180.0;
inline constexpr double RadToDeg = 180.0 / std::numbers::pi;

enum class HomeState {
    Uninitialized,
    AcquiringLock,
    LockedStatic,
    TrackingDynamic,
    FallbackRally
};

struct GeoCoord3D {
    double lat{0.0};      // Градуси
    double lon{0.0};      // Градуси
    float  alt_msl{0.0f}; // Метри над рівнем моря
};

struct Vector2D {
    float vx{0.0f}; // North, м/с
    float vy{0.0f}; // East, м/с
};

struct EkfState {
    GeoCoord3D pos;
    Vector2D   vel;
    float      hacc{99.0f};
    float      vacc{99.0f};
    float      hdop{99.0f};
    int        satellites{0};
    float      ekf_test_ratio{1.0f};
    bool       is_converged{false};
};

struct RallyPoint {
    int        id{0};
    GeoCoord3D pos;
    float      safe_alt_agl{30.0f};
    float      clear_radius_m{25.0f};
    bool       is_active{true};
};

struct HomeConfig {
    float req_hacc_m{1.8f};
    float req_hdop{1.2f};
    int   req_sats{14};
    float hold_time_s{5.0f};
    float air_speed_cruise_ms{15.0f};
    float power_cruise_w{180.0f};
    float power_climb_w{280.0f};
};

class HomeManager {
public:
    explicit HomeManager(HomeConfig config)
        : m_config(config) {}

    void add_rally_point(const RallyPoint& point) {
        m_rally_points.push_back(point);
    }

    void update_ekf(const EkfState& ekf, float dt_s, float raw_baro_pa) {
        if (dt_s <= 0.0f) return;

        switch (m_state) {
            case HomeState::Uninitialized:
                if (is_ekf_quality_sufficient(ekf)) {
                    m_state = HomeState::AcquiringLock;
                    m_stable_timer_s = dt_s;
                }
                break;

            case HomeState::AcquiringLock:
                if (is_ekf_quality_sufficient(ekf)) {
                    m_stable_timer_s += dt_s;
                    if (m_stable_timer_s >= m_config.hold_time_s) {
                        m_home_pos = ekf.pos;
                        m_home_baro_ground_pa = raw_baro_pa;
                        m_state = HomeState::LockedStatic;
                    }
                } else {
                    m_stable_timer_s = 0.0f;
                    m_state = HomeState::Uninitialized;
                }
                break;

            case HomeState::LockedStatic:
            case HomeState::TrackingDynamic:
            case HomeState::FallbackRally:
                break;
        }
    }

    void update_moving_base(GeoCoord3D base_raw, Vector2D base_vel, double timestamp_s, double current_time_s) {
        const double latency_s = current_time_s - timestamp_s;
        if (latency_s < 0.0 || latency_s > 5.0) {
            return;
        }

        const double dt_n_m = base_vel.vx * latency_s;
        const double dt_e_m = base_vel.vy * latency_s;

        const double lat_rad = base_raw.lat * DegToRad;
        const double dlat_deg = (dt_n_m / EarthRadiusM) * RadToDeg;
        const double dlon_deg = (dt_e_m / (EarthRadiusM * std::cos(lat_rad))) * RadToDeg;

        GeoCoord3D extrapolated_pos{
            base_raw.lat + dlat_deg,
            base_raw.lon + dlon_deg,
            base_raw.alt_msl
        };

        if (m_state == HomeState::LockedStatic || m_state == HomeState::TrackingDynamic) {
            m_home_pos = extrapolated_pos;
            m_base_vel_est = base_vel;
            m_last_base_update_s = current_time_s;
            m_state = HomeState::TrackingDynamic;
        }
    }

    struct ReturnPlan {
        GeoCoord3D destination;
        std::optional<int> rally_id;
        float required_energy_joules{0.0f};
        bool is_safe_return{false};
    };

    [[nodiscard]] ReturnPlan evaluate_return_destination(GeoCoord3D current_pos, Vector2D wind, float battery_energy_joules) const {
        ReturnPlan plan;
        float best_cost = 1e9f;
        GeoCoord3D best_destination = m_home_pos;
        std::optional<int> chosen_rally_id = std::nullopt;

        if (m_state == HomeState::LockedStatic || m_state == HomeState::TrackingDynamic) {
            best_cost = compute_travel_cost(current_pos, m_home_pos, wind);
        }

        for (const auto& rally : m_rally_points) {
            if (!rally.is_active) continue;
            float cost = compute_travel_cost(current_pos, rally.pos, wind);
            if (cost < best_cost) {
                best_cost = cost;
                best_destination = rally.pos;
                chosen_rally_id = rally.id;
            }
        }

        plan.destination = best_destination;
        plan.rally_id = chosen_rally_id;
        plan.required_energy_joules = best_cost;
        plan.is_safe_return = (best_cost * 1.30f <= battery_energy_joules);

        return plan;
    }

    [[nodiscard]] HomeState state() const noexcept { return m_state; }
    [[nodiscard]] GeoCoord3D home_position() const noexcept { return m_home_pos; }
    [[nodiscard]] float home_baro_pa() const noexcept { return m_home_baro_ground_pa; }

private:
    [[nodiscard]] bool is_ekf_quality_sufficient(const EkfState& ekf) const noexcept {
        return ekf.satellites >= m_config.req_sats &&
               ekf.hdop <= m_config.req_hdop &&
               ekf.hacc <= m_config.req_hacc_m &&
               ekf.ekf_test_ratio < 0.25f &&
               ekf.is_converged;
    }

    [[nodiscard]] static double compute_distance_m(GeoCoord3D a, GeoCoord3D b) noexcept {
        const double dlat = (b.lat - a.lat) * DegToRad;
        const double dlon = (b.lon - a.lon) * DegToRad;
        const double lat1 = a.lat * DegToRad;
        const double lat2 = b.lat * DegToRad;

        const double sin_dlat = std::sin(dlat / 2.0);
        const double sin_dlon = std::sin(dlon / 2.0);
        const double h = sin_dlat * sin_dlat + std::cos(lat1) * std::cos(lat2) * sin_dlon * sin_dlon;
        return EarthRadiusM * (2.0 * std::atan2(std::sqrt(h), std::sqrt(1.0 - h)));
    }

    [[nodiscard]] static double compute_bearing_rad(GeoCoord3D a, GeoCoord3D b) noexcept {
        const double lat1 = a.lat * DegToRad;
        const double lat2 = b.lat * DegToRad;
        const double dlon = (b.lon - a.lon) * DegToRad;

        const double y = std::sin(dlon) * std::cos(lat2);
        const double x = std::cos(lat1) * std::sin(lat2) - std::sin(lat1) * std::cos(lat2) * std::cos(dlon);
        double bearing = std::atan2(y, x);
        if (bearing < 0.0) {
            bearing += 2.0 * std::numbers::pi;
        }
        return bearing;
    }

    [[nodiscard]] float compute_travel_cost(GeoCoord3D current_pos, GeoCoord3D target_pos, Vector2D wind) const noexcept {
        const double dist_m = compute_distance_m(current_pos, target_pos);
        if (dist_m < 1.0) return 0.0f;

        const double bearing_rad = compute_bearing_rad(current_pos, target_pos);
        const float track_dx = static_cast<float>(std::sin(bearing_rad));
        const float track_dy = static_cast<float>(std::cos(bearing_rad));

        const float wind_along_track = wind.vy * track_dx + wind.vx * track_dy;
        const float ground_speed = m_config.air_speed_cruise_ms + wind_along_track;

        if (ground_speed < 2.0f) {
            return 1e9f; // Вітер перевищує можливості апарата
        }

        const float flight_time_s = static_cast<float>(dist_m / ground_speed);
        float energy_joules = flight_time_s * m_config.power_cruise_w;

        const float alt_diff = target_pos.alt_msl - current_pos.alt_msl;
        if (alt_diff > 0.0f) {
            const float climb_time_s = alt_diff / 2.5f;
            energy_joules += climb_time_s * m_config.power_climb_w;
        }

        return energy_joules;
    }

    HomeState              m_state{HomeState::Uninitialized};
    HomeConfig             m_config;
    GeoCoord3D             m_home_pos{};
    float                  m_home_baro_ground_pa{101325.0f};
    float                  m_stable_timer_s{0.0f};
    Vector2D               m_base_vel_est{};
    double                 m_last_base_update_s{0.0};
    std::vector<RallyPoint> m_rally_points{};
};

} // namespace drone::navigation
