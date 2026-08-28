[[nodiscard]] constexpr std::chrono::milliseconds calculate_dynamic_deadline(
    float distance_to_obstacle_m,
    float current_speed_mps,
    float max_braking_decel_mps2,
    float safety_margin_m,
    std::chrono::milliseconds sensor_lag) noexcept
{
    if (current_speed_mps < 0.1f) {
        return 15000ms; // 15 секунд на місці у стаціонарному режимі
    }

    const float braking_distance_m = (current_speed_mps * current_speed_mps) / (2.0f * max_braking_decel_mps2);
    const float total_safe_distance_m = braking_distance_m + safety_margin_m;

    if (distance_to_obstacle_m <= total_safe_distance_m) {
        return 0ms;
    }

    const float distance_available_m = distance_to_obstacle_m - total_safe_distance_m;
    const float time_available_sec = distance_available_m / current_speed_mps;
    const auto time_available_ms = std::chrono::milliseconds(static_cast<int64_t>(time_available_sec * 1000.0f));

    if (time_available_ms <= sensor_lag) {
        return 0ms;
    }
    return time_available_ms - sensor_lag;
}
