#include <cstdint>
#include <algorithm>

namespace motion {

enum class BrakeMode : uint8_t {
    Coast = 0,
    Dynamic,
    Regenerative,
    PlugEmergency
};

enum class DriveState : uint8_t {
    Idle = 0,
    Running,
    Braking,
    HoldZero,
    FaultOvervoltage
};

struct PowerBusLimits {
    uint32_t vbus_nominal_mv{24000};
    uint32_t vbus_chopper_on_mv{28000};
    uint32_t vbus_chopper_off_mv{26000};
    uint32_t vbus_ovp_alarm_mv{31000};
    int32_t  max_brake_current_ma{15000};
    float    zero_speed_threshold_rad_s{2.0f};
};

template <typename HalDriver>
class MotorBrakingController {
public:
    explicit MotorBrakingController(HalDriver& driver, const PowerBusLimits& limits = {})
        : hal_{driver}, limits_{limits} {}

    void init() noexcept {
        state_ = DriveState::Idle;
        mode_ = BrakeMode::Coast;
        pwm_duty_q12_ = 0;
        chopper_active_ = false;
        hal_.setHBridgeHiZ();
        hal_.setBrakeChopper(false);
    }

    void requestBrake(BrakeMode mode) noexcept {
        if (state_ != DriveState::FaultOvervoltage) {
            mode_ = mode;
            state_ = DriveState::Braking;
        }
    }

    void update1kHz(uint32_t vbus_mv, int32_t current_ma, float speed_rad_s) noexcept {
        // 1. Апаратний захист від перенапруги
        if (vbus_mv >= limits_.vbus_ovp_alarm_mv) {
            state_ = DriveState::FaultOvervoltage;
            hal_.setHBridgeHiZ();
            hal_.setBrakeChopper(true);
            return;
        }

        // 2. Гістерезисний контроль гальмівного переривача
        if (vbus_mv >= limits_.vbus_chopper_on_mv) {
            chopper_active_ = true;
            hal_.setBrakeChopper(true);
        } else if (vbus_mv <= limits_.vbus_chopper_off_mv) {
            chopper_active_ = false;
            hal_.setBrakeChopper(false);
        }

        if (state_ != DriveState::Braking) {
            return;
        }

        // 3. Перевірка досягнення нульової швидкості
        if (std::abs(speed_rad_s) <= limits_.zero_speed_threshold_rad_s) {
            state_ = DriveState::HoldZero;
            pwm_duty_q12_ = 0;
            hal_.setHBridgeHiZ();
            return;
        }

        // 4. Реалізація вибраного алгоритму гальмування
        switch (mode_) {
            case BrakeMode::Coast:
                hal_.setHBridgeHiZ();
                break;

            case BrakeMode::Dynamic:
                pwm_duty_q12_ = std::min<uint16_t>(4095, pwm_duty_q12_ + 64);
                if (current_ma > limits_.max_brake_current_ma && pwm_duty_q12_ > 128) {
                    pwm_duty_q12_ -= 128;
                }
                hal_.setLowSidePwm(pwm_duty_q12_);
                break;

            case BrakeMode::Regenerative:
                if (pwm_duty_q12_ > 32) {
                    pwm_duty_q12_ -= 32;
                } else {
                    pwm_duty_q12_ = 0;
                    mode_ = BrakeMode::Dynamic;
                }
                break;

            case BrakeMode::PlugEmergency:
                if (speed_rad_s > 0.0f) {
                    hal_.setReversePlugPwm(2048); // 50% реверсу
                } else {
                    state_ = DriveState::HoldZero;
                    hal_.setHBridgeHiZ();
                }
                break;
        }
    }

    [[nodiscard]] DriveState state() const noexcept { return state_; }
    [[nodiscard]] bool isChopperActive() const noexcept { return chopper_active_; }

private:
    HalDriver& hal_;
    PowerBusLimits limits_{};
    DriveState state_{DriveState::Idle};
    BrakeMode mode_{BrakeMode::Coast};
    uint16_t pwm_duty_q12_{0};
    bool chopper_active_{false};
};

} // namespace motion
