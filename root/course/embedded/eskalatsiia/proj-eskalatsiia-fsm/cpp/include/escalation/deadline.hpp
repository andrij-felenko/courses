#pragma once

#include <chrono>

namespace esc {

using namespace std::chrono_literals;

inline constexpr std::chrono::milliseconds kDeadlineMax  = 15000ms;
inline constexpr std::chrono::milliseconds kDeadlineIdle = 15000ms;

// Час до точки неповернення. 0 мс означає «часу на діалог немає, гальмувати негайно».
[[nodiscard]] constexpr std::chrono::milliseconds deadline_for(
    float distance_to_obstacle_m,
    float current_speed_mps,
    float max_braking_decel_mps2,
    float safety_margin_m,
    std::chrono::milliseconds sensor_lag) noexcept
{
    constexpr auto is_nan = [](float v) noexcept { return v != v; };
    if (is_nan(distance_to_obstacle_m) || is_nan(current_speed_mps) ||
        is_nan(max_braking_decel_mps2) || is_nan(safety_margin_m)) {
        return 0ms;  // сенсор віддав NaN — поводимося як у найгіршому випадку
    }
    if (max_braking_decel_mps2 <= 0.05f) {
        return 0ms;  // гальм фактично немає
    }
    if (current_speed_mps < 0.1f) {
        return kDeadlineIdle;  // стоїмо: часу вдосталь, але не безкінечно
    }
    if (distance_to_obstacle_m <= 0.0f) {
        return 0ms;
    }

    // Гальмівний шлях S = V^2 / (2a) плюс обов'язковий запас
    const float braking_m = (current_speed_mps * current_speed_mps) / (2.0f * max_braking_decel_mps2);
    const float safe_m    = braking_m + safety_margin_m;
    if (distance_to_obstacle_m <= safe_m) {
        return 0ms;  // уже в зоні екстреного гальмування
    }

    const float free_sec = (distance_to_obstacle_m - safe_m) / current_speed_mps;
    if (free_sec >= 60.0f) {
        return kDeadlineMax;
    }

    // Латентність тракту (кадр, інференс, радіо) цей час уже з'їла
    const auto free_ms = std::chrono::milliseconds{static_cast<std::int64_t>(free_sec * 1000.0f)};
    if (free_ms <= sensor_lag) {
        return 0ms;
    }
    const auto left = free_ms - sensor_lag;
    return (left > kDeadlineMax) ? kDeadlineMax : left;
}

}  // namespace esc
