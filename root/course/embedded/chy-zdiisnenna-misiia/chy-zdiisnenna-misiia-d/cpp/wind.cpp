#include "wind.hpp"

#include <algorithm>
#include <cmath>

namespace mission {

float WindProfile::at_height(float height_agl_m) const noexcept
{
    if (reference_height_m <= 0.0f) {
        return speed_mps;
    }
    // Нижче анемометра степеневий закон не екстраполюємо: він дав би
    // небезпечно оптимістичний штиль біля самої землі.
    const float z = std::max(height_agl_m, reference_height_m);
    return speed_mps * std::pow(z / reference_height_m, roughness_alpha);
}

std::expected<LegWind, Failure> solve_leg(const WindProfile& wind,
                                          float track_deg,
                                          float height_agl_m,
                                          float airspeed_mps) noexcept
{
    if (!std::isfinite(airspeed_mps) || airspeed_mps < 0.5f) {
        return std::unexpected(Failure::BadPlan);
    }

    const float w = wind.at_height(height_agl_m);
    const auto  relative_rad =
        static_cast<float>(static_cast<double>(wind.from_deg - track_deg) * kDegToRad);

    LegWind leg;
    leg.speed_mps = w;
    // from_deg — звідки дме, тому вектор руху повітря протилежний:
    // вітер строго в лоб дає along_mps < 0.
    leg.along_mps = -w * std::cos(relative_rad);
    leg.cross_mps = -w * std::sin(relative_rad);

    // v_air * sin(beta) + w_cross = 0 — ніс довертаємо проти зносу.
    const float sin_beta = -leg.cross_mps / airspeed_mps;
    if (std::abs(sin_beta) >= 1.0f) {
        return std::unexpected(Failure::WindTooStrong);
    }

    leg.crab_deg = static_cast<float>(std::asin(sin_beta) * kRadToDeg);
    leg.ground_speed_mps = airspeed_mps * std::sqrt(1.0f - sin_beta * sin_beta) + leg.along_mps;
    return leg;
}

}  // namespace mission
