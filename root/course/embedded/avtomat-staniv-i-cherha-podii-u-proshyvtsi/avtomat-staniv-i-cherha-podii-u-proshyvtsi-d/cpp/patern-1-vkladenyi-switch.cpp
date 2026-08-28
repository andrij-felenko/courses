#include <cstdint>

enum class FsmState : uint8_t {
    Standby,
    Connected,
    Charging,
    Fault
};

enum class FsmEvent : uint8_t {
    PlugIn,
    AuthSuccess,
    Unplug,
    Overcurrent,
    ResetBtn
};

class EvseController {
public:
    void dispatch(FsmEvent evt) noexcept {
        switch (state_) {
            case FsmState::Standby:
                if (evt == FsmEvent::PlugIn) {
                    is_locked_ = true;
                    state_ = FsmState::Connected;
                }
                break;

            case FsmState::Connected:
                if (evt == FsmEvent::AuthSuccess) {
                    state_ = FsmState::Charging;
                } else if (evt == FsmEvent::Unplug) {
                    is_locked_ = false;
                    state_ = FsmState::Standby;
                }
                break;

            case FsmState::Charging:
                if (evt == FsmEvent::Overcurrent) {
                    state_ = FsmState::Fault;
                } else if (evt == FsmEvent::Unplug) {
                    is_locked_ = false;
                    state_ = FsmState::Standby;
                }
                break;

            case FsmState::Fault:
                if (evt == FsmEvent::ResetBtn) {
                    state_ = FsmState::Standby;
                }
                break;
        }
    }

    [[nodiscard]] FsmState state() const noexcept { return state_; }

private:
    FsmState state_{FsmState::Standby};
    uint16_t current_ma_{0};
    bool is_locked_{false};
};
