#pragma once

#include <cmath>
#include <cstdint>
#include <numbers>

namespace mission {

/* Точка так, як її несе MAVLink: градуси × 1e7 у цілих і висота
   в метрах над точкою зльоту. */
struct GeoPoint {
    std::int32_t lat_e7{0};
    std::int32_t lon_e7{0};
    float        alt_m{0.0F};
};

/* Зміщення в локальній дотичній площині, метри. */
struct Offset {
    float east_m{0.0F};
    float north_m{0.0F};
};

inline constexpr float kDegPerE7      = 1.0e-7F;
inline constexpr float kMetresPerDeg  = 111320.0F;

[[nodiscard]] inline constexpr float to_rad(float deg) noexcept
{
    return deg * std::numbers::pi_v<float> / 180.0F;
}

[[nodiscard]] inline float lat_deg(std::int32_t lat_e7) noexcept
{
    return static_cast<float>(lat_e7) * kDegPerE7;
}

/* Проєкція на пласку дотичну площину. Різницю координат беремо
   в цілих і лише потім масштабуємо: повна широта у float втратила б
   метри на молодших розрядах. */
[[nodiscard]] inline Offset offset_between(GeoPoint from, GeoPoint to) noexcept
{
    const float d_lat = static_cast<float>(to.lat_e7 - from.lat_e7) * kDegPerE7;
    const float d_lon = static_cast<float>(to.lon_e7 - from.lon_e7) * kDegPerE7;
    const float k_lon = std::cos(to_rad(lat_deg(from.lat_e7)));

    return Offset{ .east_m  = d_lon * kMetresPerDeg * k_lon,
                   .north_m = d_lat * kMetresPerDeg };
}

/* КВАДРАТ відстані: усі пороги в диспетчері порівнюються з квадратом,
   і жоден такт не платить за std::sqrt. */
[[nodiscard]] inline float distance_sq(GeoPoint a, GeoPoint b) noexcept
{
    const auto o = offset_between(a, b);
    return o.east_m * o.east_m + o.north_m * o.north_m;
}

/* Кутова похибка → [-180, +180). Без цього перехід 359° → 1° дає
   хибний розворот на 358° у зворотний бік. */
[[nodiscard]] inline float wrap_deg(float deg) noexcept
{
    float a = std::fmod(deg + 180.0F, 360.0F);
    if (a < 0.0F) {
        a += 360.0F;
    }
    return a - 180.0F;
}

/* Курс → [0, 360). */
[[nodiscard]] inline float heading_deg(float deg) noexcept
{
    float a = std::fmod(deg, 360.0F);
    if (a < 0.0F) {
        a += 360.0F;
    }
    return a;
}

[[nodiscard]] inline float bearing_deg(GeoPoint from, GeoPoint to) noexcept
{
    const auto o = offset_between(from, to);
    if (o.east_m == 0.0F && o.north_m == 0.0F) {
        return 0.0F;
    }
    return heading_deg(std::atan2(o.east_m, o.north_m) * 180.0F / std::numbers::pi_v<float>);
}

[[nodiscard]] inline GeoPoint shifted(GeoPoint base, float east_m, float north_m) noexcept
{
    const float k_lon = std::cos(to_rad(lat_deg(base.lat_e7)));

    GeoPoint p = base;
    p.lat_e7 += static_cast<std::int32_t>(std::lround(north_m / kMetresPerDeg / kDegPerE7));
    if (std::fabs(k_lon) > 1.0e-6F) {
        p.lon_e7 += static_cast<std::int32_t>(
            std::lround(east_m / (kMetresPerDeg * k_lon) / kDegPerE7));
    }
    return p;
}

}  // namespace mission
