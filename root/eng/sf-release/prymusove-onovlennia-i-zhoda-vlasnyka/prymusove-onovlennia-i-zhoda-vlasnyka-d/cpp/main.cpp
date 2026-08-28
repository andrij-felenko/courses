#include <iostream>
#include <cstdint>
#include <chrono>
#include <optional>
#include <expected>

namespace fleet::ota {

enum class UrgencyLevel : uint8_t {
    StandardFeature = 0,
    ImportantBugfix = 1,
    MandatoryRegulatory = 2,
    CriticalZeroDay = 3,
    SafetyEmergencyRecall = 4
};

enum class PolicyDecision : uint8_t {
    AllowDeferral,
    ForceImmediateSafeWindow,
    SafetyHoldWaitingConditions,
    ExecuteRebootAndSwitch
};

struct InterlockFlags {
    static constexpr uint32_t SpeedZero    = 1U << 0;
    static constexpr uint32_t BrakeEngaged = 1U << 1;
    static constexpr uint32_t BatteryOk    = 1U << 2;
    static constexpr uint32_t ActuatorsOff = 1U << 3;
    static constexpr uint32_t FsDrained    = 1U << 4;
    static constexpr uint32_t AllRequired  = SpeedZero | BrakeEngaged | BatteryOk | ActuatorsOff | FsDrained;
};

struct PolicyParameters {
    UrgencyLevel urgency{UrgencyLevel::StandardFeature};
    std::chrono::system_clock::time_point issued_at;
    std::chrono::system_clock::time_point hard_deadline;
    uint32_t max_deferrals{3};
    uint32_t deferrals_used{0};
    std::chrono::seconds stability_hold_duration{5};
};

struct VehicleTelemetry {
    double velocity_mps{0.0};
    bool parking_brake{false};
    uint8_t battery_soc_percent{0};
    bool is_ac_connected{false};
    double actuator_current_amps{0.0};
    bool filesystem_drained{false};

    [[nodiscard]] constexpr uint32_t compute_interlock_mask() const noexcept {
        uint32_t mask = 0;
        if (velocity_mps >= -0.01 && velocity_mps <= 0.01) {
            mask |= InterlockFlags::SpeedZero;
        }
        if (parking_brake) {
            mask |= InterlockFlags::BrakeEngaged;
        }
        if (battery_soc_percent >= 50 || is_ac_connected) {
            mask |= InterlockFlags::BatteryOk;
        }
        if (actuator_current_amps >= -0.05 && actuator_current_amps <= 0.05) {
            mask |= InterlockFlags::ActuatorsOff;
        }
        if (filesystem_drained) {
            mask |= InterlockFlags::FsDrained;
        }
        return mask;
    }
};

class PolicyEvaluator {
public:
    [[nodiscard]] static PolicyDecision evaluate(
        const PolicyParameters& policy,
        const VehicleTelemetry& telem,
        std::chrono::system_clock::time_point current_time,
        std::optional<std::chrono::steady_clock::time_point> safe_conditions_start,
        std::chrono::steady_clock::time_point steady_now) noexcept
    {
        const bool deadline_expired = (current_time >= policy.hard_deadline);
        const bool deferrals_exhausted = (policy.deferrals_used >= policy.max_deferrals);
        const bool must_force = deadline_expired || deferrals_exhausted || 
                               (policy.urgency == UrgencyLevel::SafetyEmergencyRecall);

        if (!must_force) {
            return PolicyDecision::AllowDeferral;
        }

        const uint32_t mask = telem.compute_interlock_mask();
        if ((mask & InterlockFlags::AllRequired) != InterlockFlags::AllRequired) {
            return PolicyDecision::SafetyHoldWaitingConditions;
        }

        if (safe_conditions_start.has_value()) {
            const auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
                steady_now - *safe_conditions_start
            );
            if (elapsed >= policy.stability_hold_duration) {
                return PolicyDecision::ExecuteRebootAndSwitch;
            }
        }

        return PolicyDecision::ForceImmediateSafeWindow;
    }
};

} // namespace fleet::ota
