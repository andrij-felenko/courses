#include <iostream>

namespace embedded::fsm {

enum class CoolerState {
    Idle,
    Cooling,
    Alarm
};

class CoolerSystem {
public:
    CoolerSystem()
        : fan_comparator_(45.0f, 60.0f), alarm_limit_(85.0f), state_(CoolerState::Idle) {}

    void Step(float current_temperature_c) noexcept {
        const bool fan_active = fan_comparator_.Update(current_temperature_c);

        switch (state_) {
            case CoolerState::Idle:
                if (current_temperature_c >= alarm_limit_) {
                    state_ = CoolerState::Alarm;
                } else if (fan_active) {
                    state_ = CoolerState::Cooling;
                }
                break;

            case CoolerState::Cooling:
                if (current_temperature_c >= alarm_limit_) {
                    state_ = CoolerState::Alarm;
                } else if (!fan_active) {
                    state_ = CoolerState::Idle;
                }
                break;

            case CoolerState::Alarm:
                if (current_temperature_c < 45.0f) {
                    state_ = CoolerState::Idle;
                }
                break;
        }
    }

    [[nodiscard]] CoolerState GetState() const noexcept { return state_; }
    [[nodiscard]] bool IsFanRunning() const noexcept { return fan_comparator_.State(); }

private:
    control::HysteresisComparator<float> fan_comparator_;
    float alarm_limit_{85.0f};
    CoolerState state_{CoolerState::Idle};
};

} // namespace embedded::fsm
