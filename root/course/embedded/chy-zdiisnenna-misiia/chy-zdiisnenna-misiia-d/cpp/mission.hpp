#pragma once

#include <cstddef>
#include <string>
#include <string_view>
#include <vector>

namespace mission {

inline constexpr double kDegToRad     = 0.017453292519943295;
inline constexpr double kRadToDeg     = 57.29577951308232;
inline constexpr double kMetersPerDeg = 111320.0;
inline constexpr float  kGravity      = 9.80665f;

struct GeoPoint {
    double latitude_deg{};
    double longitude_deg{};
    float  altitude_msl_m{};   // ортометрична висота над геоїдом EGM96
};

struct Waypoint {
    GeoPoint position{};
    float    airspeed_mps{15.0f};
    float    loiter_s{0.0f};
    bool     survey{false};    // ділянка зйомки: потрібне достатньо високе сонце
};

// Межі, за якими судять здійсненність. Живуть поруч із планом, бо
// належать конкретному завданню, а не апарату.
struct Limits {
    float  safe_clearance_m{40.0f};
    float  sample_step_m{15.0f};
    float  min_ground_speed_mps{4.0f};
    float  max_duration_s{3000.0f};
    float  takeoff_wh{2.5f};
    float  landing_wh{1.5f};

    double site_latitude_deg{49.0};
    int    day_of_year{180};
    float  start_hour_local{9.0f};
    float  sunset_hour_local{20.5f};
    float  min_sun_elevation_deg{25.0f};
};

struct Plan {
    std::vector<Waypoint> waypoints;
    Limits                limits{};
};

enum class Failure {
    BadPlan,
    WindTooStrong,
    GroundSpeedTooLow,
    DemGap,
    TerrainCollision,
    ClimbRateExceeded,
    PowerUnreachable,
    EnergyBudget,
    NoSafeReturn,
    TimeWindow,
    SunsetDeadline,
    SunTooLow
};

[[nodiscard]] std::string_view describe(Failure reason) noexcept;

// Відмова несе не лише причину, а й місце: інженер має знати, який
// саме відрізок і чому.
struct Rejection {
    Failure     reason{};
    std::size_t leg_index{};   // індекс відрізка або точки; std::size_t(-1) — уся місія
    std::string detail;
};

inline constexpr std::size_t kWholeMission = static_cast<std::size_t>(-1);

struct Report {
    float total_distance_m{0.0f};
    float total_time_s{0.0f};
    float total_energy_wh{0.0f};
    float delivered_energy_wh{0.0f};
    float usable_energy_wh{0.0f};
    float reserve_left_pct{0.0f};

    float min_clearance_m{0.0f};
    float min_ground_speed_mps{0.0f};
    float peak_power_w{0.0f};
    float peak_current_a{0.0f};
    float min_sun_elevation_deg{90.0f};

    std::size_t psr_waypoint{0};
    float       psr_distance_m{0.0f};
};

[[nodiscard]] float    distance_m(const GeoPoint& a, const GeoPoint& b) noexcept;
[[nodiscard]] float    bearing_deg(const GeoPoint& a, const GeoPoint& b) noexcept;
[[nodiscard]] GeoPoint interpolate(const GeoPoint& a, const GeoPoint& b, float t) noexcept;
[[nodiscard]] float    wrap360(float degrees) noexcept;

}  // namespace mission
