#include <cstdint>
#include <chrono>
#include <algorithm>

using namespace std::chrono_literals;

class DriveController {
public:
    enum class State : uint8_t {
        Init,
        Running,
        FaultDerating,
        SafeStop
    };

    struct HardwareInterface {
        void (*setMotorPwm)(uint32_t powerPct);
        std::chrono::milliseconds (*getMonotonicTime)();
    };

    explicit DriveController(HardwareInterface hw) noexcept
        : hw_{hw}, lastHeartbeat_{hw_.getMonotonicTime()} {
        hw_.setMotorPwm(0);
    }

    void feedHeartbeat() noexcept {
        lastHeartbeat_ = hw_.getMonotonicTime();
        if (state_ == State::FaultDerating || state_ == State::Init) {
            state_ = State::Running;
        }
    }

    void update(uint32_t targetPowerPct) noexcept {
        const auto now = hw_.getMonotonicTime();
        const auto elapsed = now - lastHeartbeat_;
        const bool linkLost = (elapsed > HeartbeatTimeout);

        switch (state_) {
            case State::Running:
                if (linkLost) {
                    state_ = State::FaultDerating;
                    faultCode_ = 0xE001;
                } else {
                    currentPowerPct_ = std::clamp(targetPowerPct, 0U, 100U);
                    hw_.setMotorPwm(currentPowerPct_);
                }
                break;

            case State::FaultDerating:
                // Плавне зниження шпаруватості без кидків напруги
                if (currentPowerPct_ > DerateStepPct) {
                    currentPowerPct_ -= DerateStepPct;
                } else {
                    currentPowerPct_ = 0;
                    state_ = State::SafeStop;
                }
                hw_.setMotorPwm(currentPowerPct_);
                break;

            case State::SafeStop:
            case State::Init:
            default:
                hw_.setMotorPwm(0);
                break;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint32_t faultCode() const noexcept { return faultCode_; }

private:
    static constexpr auto HeartbeatTimeout = 100ms;
    static constexpr uint32_t DerateStepPct = 10;

    HardwareInterface hw_;
    std::chrono::milliseconds lastHeartbeat_{0};
    uint32_t currentPowerPct_{0};
    State state_{State::Init};
    uint32_t faultCode_{0};
};
