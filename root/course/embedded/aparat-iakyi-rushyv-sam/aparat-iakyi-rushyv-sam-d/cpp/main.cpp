#include <cstdint>
#include <optional>
#include <concepts>

namespace power::safety {

enum class State : uint8_t {
    Disarmed = 0,
    PreArmTest,
    Armed,
    Fault
};

template <typename HardwarePlatform>
class SafeMotorDriver {
public:
    static constexpr uint32_t ArmTokenMagic = 0x5A3C96E1U;
    static constexpr uint16_t PwmMaxLimit = 1000U;
    static constexpr uint16_t SafeVoltageMinMv = 11000U;

    explicit SafeMotorDriver(HardwarePlatform& hw) noexcept
        : hw_(hw), state_(State::Disarmed), currentPwm_(0), hbPhase_(false) {
        // Гарантуємо безпечний стан виходів при ініціалізації об'єкта
        hw_.writeHeartbeatPin(false);
        hw_.setPwmDuty(0);
    }

    [[nodiscard]] bool requestArm(uint32_t token) noexcept {
        if (token != ArmTokenMagic || state_ != State::Disarmed) {
            state_ = State::Fault;
            disarm();
            return false;
        }

        if (hw_.isEmergencyStopActive() || hw_.readBatteryVoltageMv() < SafeVoltageMinMv) {
            state_ = State::Fault;
            disarm();
            return false;
        }

        state_ = State::Armed;
        return true;
    }

    void disarm() noexcept {
        hw_.writeHeartbeatPin(false);
        hw_.setPwmDuty(0);
        currentPwm_ = 0;
        if (state_ != State::Fault) {
            state_ = State::Disarmed;
        }
    }

    void update(uint16_t targetPwm) noexcept {
        if (hw_.isEmergencyStopActive()) {
            state_ = State::Fault;
            disarm();
            return;
        }

        if (state_ == State::Armed) {
            hbPhase_ = !hbPhase_;
            hw_.writeHeartbeatPin(hbPhase_);

            currentPwm_ = (targetPwm > PwmMaxLimit) ? PwmMaxLimit : targetPwm;
            hw_.setPwmDuty(currentPwm_);
        } else {
            hw_.writeHeartbeatPin(false);
            hw_.setPwmDuty(0);
        }

        hw_.feedWatchdog();
    }

    [[nodiscard]] State getState() const noexcept { return state_; }
    [[nodiscard]] bool isArmed() const noexcept { return state_ == State::Armed; }

private:
    HardwarePlatform& hw_;
    State state_;
    uint16_t currentPwm_;
    bool hbPhase_;
};

} // namespace power::safety
