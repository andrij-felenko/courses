#include <cstdint>
#include <array>
#include <span>
#include <optional>

enum class PowerState : uint8_t {
    DeepSleep = 0,
    SensorAcquisition,
    Processing,
    RadioTx,
    Count
};

struct PowerStateProfile {
    uint32_t current_ua{0};
    uint32_t duration_ms{0};
};

struct BatteryModel {
    uint32_t capacity_mah{0};
    uint32_t self_discharge_ua{0};
    uint16_t converter_efficiency_pct{90};
};

struct PowerBudgetResult {
    uint32_t total_cycle_time_ms{0};
    uint32_t avg_current_ua{0};
    uint32_t battery_lifetime_hours{0};
};

class PowerBudgetEstimator {
public:
    static constexpr size_t StateCount = static_cast<size_t>(PowerState::Count);

    [[nodiscard]] static std::optional<PowerBudgetResult> calculate(
        std::span<const PowerStateProfile, StateCount> states,
        const BatteryModel& battery) noexcept 
    {
        if (battery.converter_efficiency_pct == 0) {
            return std::nullopt;
        }

        uint64_t total_charge_uas = 0;
        uint32_t total_time_ms = 0;

        for (const auto& state : states) {
            total_charge_uas += static_cast<uint64_t>(state.current_ua) * state.duration_ms;
            total_time_ms += state.duration_ms;
        }

        if (total_time_ms == 0) {
            return std::nullopt;
        }

        PowerBudgetResult result{};
        result.total_cycle_time_ms = total_time_ms;

        const uint32_t load_avg_ua = static_cast<uint32_t>(total_charge_uas / total_time_ms);
        const uint32_t effective_draw_ua = 
            ((load_avg_ua * 100U) / battery.converter_efficiency_pct) + battery.self_discharge_ua;

        result.avg_current_ua = effective_draw_ua;

        if (effective_draw_ua > 0) {
            const uint64_t cap_uah = static_cast<uint64_t>(battery.capacity_mah) * 1000ULL;
            result.battery_lifetime_hours = static_cast<uint32_t>(cap_uah / effective_draw_ua);
        }

        return result;
    }
};
