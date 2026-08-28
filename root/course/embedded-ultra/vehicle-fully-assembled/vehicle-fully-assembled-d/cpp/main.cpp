#include <cstdint>
#include <string_view>
#include <expected>
#include <chrono>

namespace vehicle::control {

enum class CheckBit : uint32_t {
    ImuHealthy       = 1U << 0,
    MagHealthy       = 1U << 1,
    BaroHealthy      = 1U << 2,
    BatteryHealthy   = 1U << 3,
    ThrottleZero     = 1U << 4,
    EkfConverged     = 1U << 5,
    SafetySwitchOn   = 1U << 6
};

[[nodiscard]] constexpr uint32_t operator|(CheckBit a, CheckBit b) noexcept {
    return static_cast<uint32_t>(a) | static_cast<uint32_t>(b);
}

[[nodiscard]] constexpr uint32_t operator|(uint32_t a, CheckBit b) noexcept {
    return a | static_cast<uint32_t>(b);
}

constexpr uint32_t CriticalMask = CheckBit::ImuHealthy |
                                  CheckBit::MagHealthy |
                                  CheckBit::BaroHealthy |
                                  CheckBit::BatteryHealthy |
                                  CheckBit::ThrottleZero |
                                  CheckBit::EkfConverged |
                                  CheckBit::SafetySwitchOn;

enum class SystemState {
    Disarmed,
    Armed,
    FailsafeLockout
};

enum class ArmRejectionReason {
    AlreadyArmed,
    FailsafeLocked,
    ImuFault,
    MagFault,
    BaroFault,
    BatteryLow,
    ThrottleRaised,
    EkfNotConverged,
    SafetySwitchOpen,
    StabilityTimeout
};

struct TelemetrySnapshot {
    float batteryCellVolts{0.0f};
    float throttlePercent{0.0f};
    float ekfVariancePos{0.0f};
    float gyroDriftNorm{0.0f};
    bool  accelCalibrated{false};
    bool  compassCalibrated{false};
    bool  baroReady{false};
    bool  safetySwitchClosed{false};
};

class ArmController {
public:
    constexpr ArmController() noexcept = default;

    void update(const TelemetrySnapshot& telem, std::chrono::milliseconds dt) noexcept {
        uint32_t mask = 0;

        if (telem.accelCalibrated && telem.gyroDriftNorm < 0.05f) {
            mask |= CheckBit::ImuHealthy;
        }
        if (telem.compassCalibrated) {
            mask |= CheckBit::MagHealthy;
        }
        if (telem.baroReady) {
            mask |= CheckBit::BaroHealthy;
        }
        if (telem.batteryCellVolts >= 3.70f) {
            mask |= CheckBit::BatteryHealthy;
        }
        if (telem.throttlePercent <= 0.05f) {
            mask |= CheckBit::ThrottleZero;
        }
        if (telem.ekfVariancePos < 0.80f) {
            mask |= CheckBit::EkfConverged;
        }
        if (telem.safetySwitchClosed) {
            mask |= CheckBit::SafetySwitchOn;
        }

        currentMask_ = mask;

        if ((currentMask_ & CriticalMask) == CriticalMask) {
            stableDuration_ += dt;
        } else {
            stableDuration_ = std::chrono::milliseconds{0};
        }
    }

    [[nodiscard]] std::expected<void, ArmRejectionReason> requestArm() noexcept {
        if (state_ == SystemState::Armed) {
            return {};
        }
        if (state_ == SystemState::FailsafeLockout) {
            return std::unexpected(ArmRejectionReason::FailsafeLocked);
        }

        if (!(currentMask_ & static_cast<uint32_t>(CheckBit::ImuHealthy))) {
            return std::unexpected(ArmRejectionReason::ImuFault);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckBit::BatteryHealthy))) {
            return std::unexpected(ArmRejectionReason::BatteryLow);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckBit::ThrottleZero))) {
            return std::unexpected(ArmRejectionReason::ThrottleRaised);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckBit::SafetySwitchOn))) {
            return std::unexpected(ArmRejectionReason::SafetySwitchOpen);
        }
        if ((currentMask_ & CriticalMask) != CriticalMask) {
            return std::unexpected(ArmRejectionReason::EkfNotConverged);
        }

        if (stableDuration_ < std::chrono::milliseconds{1500}) {
            return std::unexpected(ArmRejectionReason::StabilityTimeout);
        }

        state_ = SystemState::Armed;
        return {};
    }

    void disarm() noexcept {
        state_ = SystemState::Disarmed;
    }

    void forceFailsafe() noexcept {
        state_ = SystemState::FailsafeLockout;
    }

    [[nodiscard]] SystemState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t bitmask() const noexcept { return currentMask_; }

private:
    SystemState state_{SystemState::Disarmed};
    uint32_t currentMask_{0};
    std::chrono::milliseconds stableDuration_{0};
};

} // namespace vehicle::control
