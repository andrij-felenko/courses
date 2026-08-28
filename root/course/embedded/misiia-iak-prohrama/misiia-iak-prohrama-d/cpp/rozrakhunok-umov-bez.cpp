#include <cstdint>
#include <chrono>

namespace mission {

enum class ConditionType {
    None,
    WaitDelay,
    WaitDistance,
    WaitBattery
};

struct ActiveCondition {
    ConditionType type{ConditionType::None};
    uint32_t      start_timestamp_ms{0};
    uint32_t      target_duration_ms{0};
    float         target_distance_m{0.0f};
    float         min_battery_soc_pct{0.0f};
};

[[nodiscard]] bool evaluate_condition_tick(const ActiveCondition& cond,
                                           uint32_t current_time_ms,
                                           float current_dist_m,
                                           float current_battery_pct) noexcept
{
    switch (cond.type) {
        case ConditionType::WaitDelay:
            return (current_time_ms - cond.start_timestamp_ms) >= cond.target_duration_ms;

        case ConditionType::WaitDistance:
            return (current_dist_m <= cond.target_distance_m);

        case ConditionType::WaitBattery:
            return (current_battery_pct < cond.min_battery_soc_pct);

        case ConditionType::None:
        default:
            return true;
    }
}

} // namespace mission
