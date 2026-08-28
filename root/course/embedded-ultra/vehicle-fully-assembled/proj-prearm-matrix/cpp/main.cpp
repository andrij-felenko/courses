#include <cstdint>
#include <string_view>
#include <expected>
#include <chrono>

namespace vehicle::safety {

enum class CheckFlag : uint32_t {
    ImuOk       = 1U << 0,
    MagOk       = 1U << 1,
    BaroOk      = 1U << 2,
    BatteryOk   = 1U << 3,
    RcSafe      = 1U << 4,
    EkfOk       = 1U << 5,
    SafetySw    = 1U << 6
};

[[nodiscard]] constexpr uint32_t operator|(CheckFlag a, CheckFlag b) noexcept {
    return static_cast<uint32_t>(a) | static_cast<uint32_t>(b);
}

[[nodiscard]] constexpr uint32_t operator|(uint32_t a, CheckFlag b) noexcept {
    return a | static_cast<uint32_t>(b);
}

constexpr uint32_t RequiredMask = CheckFlag::ImuOk |
                                  CheckFlag::MagOk |
                                  CheckFlag::BaroOk |
                                  CheckFlag::BatteryOk |
                                  CheckFlag::RcSafe |
                                  CheckFlag::EkfOk |
                                  CheckFlag::SafetySw;

enum class ArmState {
    Disarmed,
    Armed,
    FailsafeLockout
};

enum class ArmingError {
    AlreadyArmed,
    FailsafeActive,
    ImuUncalibrated,
    MagInconsistent,
    BaroFault,
    BatteryLow,
    ThrottleNotZero,
    EkfDiverged,
    SafetySwitchOpen,
    HysteresisNotMet
};

struct SensorSnapshot {
    float cellVoltage{0.0f};
    float throttleStick{0.0f};
    float ekfPosVariance{0.0f};
    float gyroDriftRadS{0.0f};
    bool  imuCalibrated{false};
    bool  magCalibrated{false};
    bool  baroHealthy{false};
    bool  safetySwitchPressed{false};
};

class PreArmEvaluator {
public:
    constexpr PreArmEvaluator() noexcept = default;

    void update(const SensorSnapshot& snap, std::chrono::milliseconds dt) noexcept {
        uint32_t mask = 0;

        if (snap.imuCalibrated && snap.gyroDriftRadS < 0.05f) {
            mask |= CheckFlag::ImuOk;
        }
        if (snap.magCalibrated) {
            mask |= CheckFlag::MagOk;
        }
        if (snap.baroHealthy) {
            mask |= CheckFlag::BaroOk;
        }
        if (snap.cellVoltage >= 3.70f) {
            mask |= CheckFlag::BatteryOk;
        }
        if (snap.throttleStick <= 0.05f) {
            mask |= CheckFlag::RcSafe;
        }
        if (snap.ekfPosVariance < 0.80f) {
            mask |= CheckFlag::EkfOk;
        }
        if (snap.safetySwitchPressed) {
            mask |= CheckFlag::SafetySw;
        }

        currentMask_ = mask;

        if ((currentMask_ & RequiredMask) == RequiredMask) {
            stableDuration_ += dt;
        } else {
            stableDuration_ = std::chrono::milliseconds{0};
        }
    }

    [[nodiscard]] std::expected<void, ArmingError> requestArm() noexcept {
        if (state_ == ArmState::Armed) {
            return {};
        }
        if (state_ == ArmState::FailsafeLockout) {
            return std::unexpected(ArmingError::FailsafeActive);
        }

        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::ImuOk))) {
            return std::unexpected(ArmingError::ImuUncalibrated);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::MagOk))) {
            return std::unexpected(ArmingError::MagInconsistent);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::BaroOk))) {
            return std::unexpected(ArmingError::BaroFault);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::BatteryOk))) {
            return std::unexpected(ArmingError::BatteryLow);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::RcSafe))) {
            return std::unexpected(ArmingError::ThrottleNotZero);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::EkfOk))) {
            return std::unexpected(ArmingError::EkfDiverged);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::SafetySw))) {
            return std::unexpected(ArmingError::SafetySwitchOpen);
        }

        if (stableDuration_ < std::chrono::milliseconds{1500}) {
            return std::unexpected(ArmingError::HysteresisNotMet);
        }

        state_ = ArmState::Armed;
        return {};
    }

    void disarm() noexcept {
        state_ = ArmState::Disarmed;
    }

    void triggerFailsafe() noexcept {
        state_ = ArmState::FailsafeLockout;
    }

    [[nodiscard]] ArmState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t bitmask() const noexcept { return currentMask_; }

private:
    ArmState state_{ArmState::Disarmed};
    uint32_t currentMask_{0};
    std::chrono::milliseconds stableDuration_{0};
};

} // namespace vehicle::safety
