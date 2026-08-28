#include <cstdint>

enum class EvseSignal : uint8_t {
    CpVoltage12V,
    CpVoltage9V,
    CpVoltage6V,
    RfidAuthOk,
    Overcurrent,
    ResetBtn
};

enum class EvseStateId : uint8_t {
    Standby,
    Connected,
    Charging,
    Fault
};

class EvseController {
public:
    using StateHandler = void (EvseController::*)(EvseSignal);

    EvseController() noexcept {
        initHardware();
        state_ = &EvseController::stateStandby;
    }

    void dispatch(EvseSignal sig) noexcept {
        if (state_) {
            (this->*state_)(sig);
        }
    }

private:
    void initHardware() noexcept {
        setRelay(false);
        setPilotPwm(100);
        setRedLed(false);
    }

    void setPilotPwm(uint8_t duty) noexcept { (void)duty; }
    void setRelay(bool closed) noexcept { (void)closed; }
    void setRedLed(bool on) noexcept { (void)on; }

    void stateStandby(EvseSignal sig) noexcept {
        switch (sig) {
            case EvseSignal::CpVoltage9V:
                setPilotPwm(50);
                state_ = &EvseController::stateConnected;
                break;
            default:
                break;
        }
    }

    void stateConnected(EvseSignal sig) noexcept {
        switch (sig) {
            case EvseSignal::RfidAuthOk:
                is_authorized_ = true;
                break;

            case EvseSignal::CpVoltage6V:
                if (is_authorized_) {
                    setRelay(true);
                    state_ = &EvseController::stateCharging;
                }
                break;

            case EvseSignal::CpVoltage12V:
                is_authorized_ = false;
                setPilotPwm(100);
                state_ = &EvseController::stateStandby;
                break;

            case EvseSignal::Overcurrent:
                setRedLed(true);
                state_ = &EvseController::stateFault;
                break;

            default:
                break;
        }
    }

    void stateCharging(EvseSignal sig) noexcept {
        switch (sig) {
            case EvseSignal::CpVoltage9V:
                setRelay(false);
                state_ = &EvseController::stateConnected;
                break;

            case EvseSignal::CpVoltage12V:
                setRelay(false);
                is_authorized_ = false;
                setPilotPwm(100);
                state_ = &EvseController::stateStandby;
                break;

            case EvseSignal::Overcurrent:
                setRelay(false);
                setPilotPwm(0);
                setRedLed(true);
                state_ = &EvseController::stateFault;
                break;

            default:
                break;
        }
    }

    void stateFault(EvseSignal sig) noexcept {
        switch (sig) {
            case EvseSignal::ResetBtn:
                setRedLed(false);
                setPilotPwm(100);
                is_authorized_ = false;
                state_ = &EvseController::stateStandby;
                break;
            default:
                break;
        }
    }

    StateHandler state_{nullptr};
    bool is_authorized_{false};
    uint16_t current_limit_a_{32};
};
