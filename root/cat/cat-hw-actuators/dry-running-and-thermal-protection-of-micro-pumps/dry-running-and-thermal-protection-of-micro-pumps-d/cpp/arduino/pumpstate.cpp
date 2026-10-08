#include <Arduino.h>

enum class PumpState {
    Idle,
    Running,
    Verifying,
    RetryPulse,
    ThermalCooling,
    FaultLockout
};

class MicroPumpController {
public:
    struct Config {
        uint32_t currentLowThresholdMa = 40;
        uint32_t currentHighThresholdMa = 350;
        uint32_t debounceMs = 150;
        uint32_t pulseOnMs = 100;
        uint32_t pulseOffMs = 900;
        uint32_t coolingMs = 5000;
        uint8_t  maxRetries = 3;
    };

    MicroPumpController(uint8_t controlPin, uint8_t sensePin, Config config = Config())
        : pinControl_(controlPin), pinSense_(sensePin), config_(config), state_(PumpState::Idle) {}

    void begin() {
        pinMode(pinControl_, OUTPUT);
        digitalWrite(pinControl_, LOW);
        state_ = PumpState::Idle;
        retryCount_ = 0;
    }

    void start() {
        if (state_ == PumpState::Idle) {
            state_ = PumpState::Running;
            retryCount_ = 0;
            setPump(true);
        }
    }

    void update(uint32_t nowMs) {
        uint32_t currentMa = readCurrentMa();

        switch (state_) {
            case PumpState::Idle:
                break;

            case PumpState::Running:
                if (currentMa < config_.currentLowThresholdMa || currentMa > config_.currentHighThresholdMa) {
                    state_ = PumpState::Verifying;
                    stateTimerMs_ = nowMs;
                }
                break;

            case PumpState::Verifying:
                if (currentMa >= config_.currentLowThresholdMa && currentMa <= config_.currentHighThresholdMa) {
                    state_ = PumpState::Running;
                } else if (nowMs - stateTimerMs_ >= config_.debounceMs) {
                    state_ = PumpState::RetryPulse;
                    pulseTimerMs_ = nowMs;
                    setPump(true);
                }
                break;

            case PumpState::RetryPulse:
                if (currentMa >= config_.currentLowThresholdMa && currentMa <= config_.currentHighThresholdMa) {
                    state_ = PumpState::Running;
                    retryCount_ = 0;
                    break;
                }

                if (outputActive_) {
                    if (nowMs - pulseTimerMs_ >= config_.pulseOnMs) {
                        setPump(false);
                        pulseTimerMs_ = nowMs;
                        retryCount_++;
                    }
                } else {
                    if (nowMs - pulseTimerMs_ >= config_.pulseOffMs) {
                        if (retryCount_ >= config_.maxRetries) {
                            state_ = PumpState::ThermalCooling;
                            stateTimerMs_ = nowMs;
                        } else {
                            setPump(true);
                            pulseTimerMs_ = nowMs;
                        }
                    }
                }
                break;

            case PumpState::ThermalCooling:
                setPump(false);
                if (nowMs - stateTimerMs_ >= config_.coolingMs) {
                    state_ = PumpState::FaultLockout;
                }
                break;

            case PumpState::FaultLockout:
                setPump(false);
                break;
        }
    }

    PumpState getState() const { return state_; }

private:
    uint8_t pinControl_;
    uint8_t pinSense_;
    Config config_;
    PumpState state_;
    uint8_t retryCount_ = 0;
    uint32_t stateTimerMs_ = 0;
    uint32_t pulseTimerMs_ = 0;
    bool outputActive_ = false;

    void setPump(bool enable) {
        outputActive_ = enable;
        digitalWrite(pinControl_, enable ? HIGH : LOW);
    }

    uint32_t readCurrentMa() {
        int raw = analogRead(pinSense_);
        return static_cast<uint32_t>((raw * 5000UL) / 1023UL);
    }
};
