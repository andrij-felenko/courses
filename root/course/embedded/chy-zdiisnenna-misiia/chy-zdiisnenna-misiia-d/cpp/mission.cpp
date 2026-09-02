#include "mission.hpp"

#include <cmath>
#include <utility>

namespace mission {
namespace {

// Зміщення в метрах на середній широті відрізка: на масштабах місії
// плоска модель точніша за роздільність DEM.
std::pair<double, double> offsets_m(const GeoPoint& a, const GeoPoint& b) noexcept
{
    const double mid_lat_rad = 0.5 * (a.latitude_deg + b.latitude_deg) * kDegToRad;
    const double north = (b.latitude_deg - a.latitude_deg) * kMetersPerDeg;
    const double east  = (b.longitude_deg - a.longitude_deg) * kMetersPerDeg * std::cos(mid_lat_rad);
    return {east, north};
}

}  // namespace

std::string_view describe(Failure reason) noexcept
{
    switch (reason) {
    case Failure::BadPlan:            return "план некоректний";
    case Failure::WindTooStrong:      return "боковий вітер сильніший за повітряну швидкість";
    case Failure::GroundSpeedTooLow:  return "шляхова швидкість нижча за поріг";
    case Failure::DemGap:             return "маршрут виходить за межі карти висот";
    case Failure::TerrainCollision:   return "недостатній кліренс над рельєфом";
    case Failure::ClimbRateExceeded:  return "потрібна швидкопідйомність вища за можливу";
    case Failure::PowerUnreachable:   return "потрібна потужність недосяжна для батареї";
    case Failure::EnergyBudget:       return "енергії не вистачає з урахуванням резерву";
    case Failure::NoSafeReturn:       return "точку безпечного повернення пройдено";
    case Failure::TimeWindow:         return "місія не вкладається в операційне вікно";
    case Failure::SunsetDeadline:     return "посадка пізніше за дозволений час до заходу сонця";
    case Failure::SunTooLow:          return "сонце надто низько для оптичного навантаження";
    }
    return "невідома причина";
}

float distance_m(const GeoPoint& a, const GeoPoint& b) noexcept
{
    const auto [east, north] = offsets_m(a, b);
    return static_cast<float>(std::hypot(east, north));
}

float bearing_deg(const GeoPoint& a, const GeoPoint& b) noexcept
{
    const auto [east, north] = offsets_m(a, b);
    if (east == 0.0 && north == 0.0) {
        return 0.0f;   // вироджений відрізок валідатор відсіює окремо
    }
    return wrap360(static_cast<float>(std::atan2(east, north) * kRadToDeg));
}

GeoPoint interpolate(const GeoPoint& a, const GeoPoint& b, float t) noexcept
{
    return GeoPoint{
        std::lerp(a.latitude_deg, b.latitude_deg, static_cast<double>(t)),
        std::lerp(a.longitude_deg, b.longitude_deg, static_cast<double>(t)),
        std::lerp(a.altitude_msl_m, b.altitude_msl_m, t)};
}

float wrap360(float degrees) noexcept
{
    if (!std::isfinite(degrees)) {
        return 0.0f;
    }
    degrees = std::fmod(degrees, 360.0f);
    return degrees < 0.0f ? degrees + 360.0f : degrees;
}

}  // namespace mission
