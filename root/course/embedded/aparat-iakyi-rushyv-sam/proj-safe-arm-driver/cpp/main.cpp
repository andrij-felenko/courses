#include <cstdint>
#include <optional>
#include <concepts>

namespace safety {

enum class ActuatorState : uint8_t {
    Disarmed = 0,
    ArmRequested,
    PreArmCheck,
    Armed,
    Fault
};

struct SafetyConfig {
    static constexpr uint32_t TokenMagic = 0x5A3C96E1U;
    static constexpr uint16_t PwmMaxDuty = 1000U;
    static constexpr uint16_t MinSafeVoltageMv = 11000U;
    static constexpr uint16_t MaxSafeVoltageMv = 14500U;
};

// Концепт апаратної платформи для компіляційної перевірки периферії
template <typename Platform>
concept HardwareInterface = requires(Platform p, bool b, uint16_t duty) {
    { p.writeHeartbeat(b) } -> std::same_as<void>;
    { p.setPwmDuty(duty) } -> std::same_as<void>;
    { p.getTimeMs() } -> std::same_as<uint32_t>;
    { p.readVoltageMv() } -> std::same_as<uint16_t>;
    { p.readEstopActive() } -> std::same_as<bool>;
    { p.feedWatchdog() } -> std::same_as<void>;
};

template <HardwareInterface Platform>
class SafeActuator {
public:
    explicit SafeActuator(Platform& hw) noexcept
        : hw_(hw), state_(ActuatorState::Disarmed), currentPwm_(0), hbPhase_(false) {
        // Гарантований безпечний стан апаратних ліній при інстанціації
        hw_.writeHeartbeat(false);
        hw_.setPwmDuty(0);
    }

    [[nodiscard]] bool requestArm(uint32_t token) noexcept {
        if (token != SafetyConfig::TokenMagic) {
            state_ = ActuatorState::Fault;
            disarm();
            return false;
        }
        if (state_ != ActuatorState::Disarmed) {
            return false;
        }
        state_ = ActuatorState::ArmRequested;
        return true;
    }

    void disarm() noexcept {
        hw_.writeHeartbeat(false);
        hw_.setPwmDuty(0);
        currentPwm_ = 0;
        if (state_ != ActuatorState::Fault) {
            state_ = ActuatorState::Disarmed;
        }
    }

    void update(uint16_t targetPwm) noexcept {
        if (hw_.readEstopActive()) {
            state_ = ActuatorState::Fault;
            disarm();
            return;
        }

        switch (state_) {
            case ActuatorState::Disarmed:
                hw_.writeHeartbeat(false);
                hw_.setPwmDuty(0);
                break;

            case ActuatorState::ArmRequested:
                state_ = ActuatorState::PreArmCheck;
                break;

            case ActuatorState::PreArmCheck: {
                const uint16_t v = hw_.readVoltageMv();
                if (v >= SafetyConfig::MinSafeVoltageMv && v <= SafetyConfig::MaxSafeVoltageMv) {
                    state_ = ActuatorState::Armed;
                } else {
                    state_ = ActuatorState::Fault;
                    disarm();
                }
                break;
            }

            case ActuatorState::Armed: {
                hbPhase_ = !hbPhase_;
                hw_.writeHeartbeat(hbPhase_);

                currentPwm_ = (targetPwm > SafetyConfig::PwmMaxDuty)
                                  ? SafetyConfig::PwmMaxDuty
                                  : targetPwm;
                hw_.setPwmDuty(currentPwm_);
                break;
            }

            case ActuatorState::Fault:
            default:
                disarm();
                break;
        }

        hw_.feedWatchdog();
    }

    [[nodiscard]] ActuatorState getState() const noexcept { return state_; }
    [[nodiscard]] bool isArmed() const noexcept { return state_ == ActuatorState::Armed; }

private:
    Platform& hw_;
    ActuatorState state_;
    uint16_t currentPwm_;
    bool hbPhase_;
};

} // namespace safety
