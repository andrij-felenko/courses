#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <expected>

namespace drone::geofence {

inline constexpr std::size_t MaxPolygonVertices = 32;
inline constexpr std::size_t MaxPolygons        = 16;
inline constexpr std::size_t MaxCylinders       = 16;

enum class Result : std::int8_t {
    Ok                  = 0,
    NullPointer         = -1,
    InvalidParam        = -2,
    CapacityExceeded    = -3,
    DegeneratePolygon   = -4,
    AltitudeInverted    = -5
};

enum class ZoneType : std::uint8_t {
    KeepIn  = 0,
    KeepOut = 1
};

enum class State : std::uint8_t {
    Safe    = 0,
    Warning = 1,
    Breach  = 2
};

enum class Action : std::uint8_t {
    None        = 0,
    Warn        = 1,
    BrakeHold   = 2,
    Rtl         = 3,
    SmartRtl    = 4,
    Land        = 5,
    Terminate   = 6
};

struct PointGeo {
    std::int32_t lat_e7{0};
    std::int32_t lon_e7{0};
    float        alt_m{0.0f};
};

struct VelocityNed {
    float vx{0.0f};
    float vy{0.0f};
    float vz{0.0f};

    [[nodiscard]] constexpr float speed_horizontal_sq() const noexcept {
        return vx * vx + vy * vy;
    }
};

struct AABB {
    std::int32_t min_lat{0};
    std::int32_t max_lat{0};
    std::int32_t min_lon{0};
    std::int32_t max_lon{0};

    [[nodiscard]] constexpr bool contains(std::int32_t lat, std::int32_t lon) const noexcept {
        return (lat >= min_lat && lat <= max_lat && lon >= min_lon && lon <= max_lon);
    }
};

struct Polygon {
    std::array<PointGeo, MaxPolygonVertices> vertices{};
    std::uint8_t                            vertex_count{0};
    ZoneType                                zone_type{ZoneType::KeepIn};
    float                                   alt_min_m{0.0f};
    float                                   alt_max_m{120.0f};
    AABB                                    aabb{};
    bool                                    enabled{true};
};

struct Cylinder {
    PointGeo center{};
    float    radius_m{100.0f};
    float    alt_min_m{0.0f};
    float    alt_max_m{120.0f};
    ZoneType zone_type{ZoneType::KeepIn};
    bool     enabled{true};
};

struct Config {
    float max_braking_accel_mps2{2.5f};
    float system_latency_s{0.3f};
    float static_margin_m{5.0f};
    float warning_time_s{3.0f};
};

struct Report {
    State        state{State::Safe};
    Action       recommended_action{Action::None};
    float        distance_to_boundary_m{1e6f};
    float        time_to_breach_s{1e6f};
    std::int16_t critical_zone_index{-1};
    bool         is_keep_in_breach{false};
    bool         is_keep_out_breach{false};
    bool         is_altitude_breach{false};
};

} // namespace drone::geofence
