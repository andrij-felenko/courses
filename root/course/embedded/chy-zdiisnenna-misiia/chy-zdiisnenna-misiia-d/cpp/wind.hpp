#pragma once

#include <expected>

#include "mission.hpp"

namespace mission {

// Прогноз із наземної станції: швидкість на висоті анемометра.
// На висоті польоту вітер інший — його дає степеневий закон Гельмана.
struct WindProfile {
    float speed_mps{0.0f};
    float from_deg{0.0f};            // звідки дме: 0 — з півночі, 90 — зі сходу
    float reference_height_m{10.0f};
    float roughness_alpha{0.14f};    // 0.14 поле, 0.20...0.28 ліс і пагорби

    [[nodiscard]] float at_height(float height_agl_m) const noexcept;
};

struct LegWind {
    float speed_mps{0.0f};
    float along_mps{0.0f};           // + попутний, - зустрічний
    float cross_mps{0.0f};           // + зносить праворуч від лінії шляху
    float crab_deg{0.0f};
    float ground_speed_mps{0.0f};
};

// Трикутник швидкостей для одного відрізка. Помилка замість -1: у виклику
// це або кут зносу без розв'язку, або нульова повітряна швидкість.
[[nodiscard]] std::expected<LegWind, Failure> solve_leg(const WindProfile& wind,
                                                        float track_deg,
                                                        float height_agl_m,
                                                        float airspeed_mps) noexcept;

}  // namespace mission
