#include <cstdint>

enum class Signal : uint8_t {
    Entry,
    Exit,
    BtnPress,
    TimerExpired
};

class PumpController {
public:
    using StateFn = void (PumpController::*)(Signal);

    PumpController() noexcept {
        transition(&PumpController::stateFilling);
    }

    void dispatch(Signal sig) noexcept {
        if (state_) {
            (this->*state_)(sig);
        }
    }

private:
    void transition(StateFn target) noexcept {
        if (state_) {
            (this->*state_)(Signal::Exit);
        }
        state_ = target;
        if (state_) {
            (this->*state_)(Signal::Entry);
        }
    }

    void stateFilling(Signal sig) noexcept {
        switch (sig) {
            case Signal::Entry:
                // OpenValve();
                break;
            case Signal::Exit:
                // CloseValve();
                break;
            case Signal::TimerExpired:
                transition(&PumpController::stateDraining);
                break;
            default:
                break;
        }
    }

    void stateDraining(Signal sig) noexcept {
        switch (sig) {
            case Signal::Entry:
                // StartPump();
                break;
            case Signal::Exit:
                // StopPump();
                break;
            case Signal::BtnPress:
                transition(&PumpController::stateFilling);
                break;
            default:
                break;
        }
    }

    StateFn state_{nullptr};
    uint32_t fill_level_{0};
};
