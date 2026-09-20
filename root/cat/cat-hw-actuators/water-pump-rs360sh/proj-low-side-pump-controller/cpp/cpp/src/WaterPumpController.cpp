#include "WaterPumpController.h"
#include <algorithm>

WaterPumpController::WaterPumpController(IPwmChannel& pwm, const Config& config)
    : pwmChannel_(pwm), config_(config), state_(State::Stopped) {
    pwmChannel_.setDutyCycle(0);
}

void WaterPumpController::start() {
    if (state_ == State::Stopped || state_ == State::Fault) {
        state_ = State::Starting;
        stateStartTime_ = std::chrono::steady_clock::now();
        lastWatchdogReset_ = stateStartTime_;
        pwmChannel_.setDutyCycle(config_.minDutyCycle);
    }
}

void WaterPumpController::stop() {
    state_ = State::Stopped;
    pwmChannel_.setDutyCycle(0);
}

void WaterPumpController::resetWatchdog() {
    lastWatchdogReset_ = std::chrono::steady_clock::now();
}

bool WaterPumpController::isFault() const {
    return state_ == State::Fault;
}

void WaterPumpController::update() {
    if (state_ == State::Stopped || state_ == State::Fault) {
        return;
    }

    auto now = std::chrono::steady_clock::now();

    // Перевірка сторожового таймера
    if (now - lastWatchdogReset_ >= config_.watchdogTimeout) {
        state_ = State::Fault;
        pwmChannel_.setDutyCycle(0);
        return;
    }

    // Плавний пуск
    if (state_ == State::Starting) {
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - stateStartTime_);
        if (elapsed >= config_.softStartDuration) {
            state_ = State::Running;
            pwmChannel_.setDutyCycle(config_.maxDutyCycle);
        } else {
            // Лінійна інтерполяція ШІМ
            float progress = static_cast<float>(elapsed.count()) / config_.softStartDuration.count();
            uint8_t duty = config_.minDutyCycle + 
                static_cast<uint8_t>(progress * (config_.maxDutyCycle - config_.minDutyCycle));
            pwmChannel_.setDutyCycle(duty);
        }
    }
}
