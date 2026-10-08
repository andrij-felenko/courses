#include "mosfet_pwm_hal.hpp"
#include <algorithm>

MosfetPwmHal::MosfetPwmHal(std::uint8_t pwm_pin, std::uint32_t frequency_hz)
    : pwm_pin_(pwm_pin), frequency_hz_(frequency_hz), current_duty_(0.0f), enabled_(false) {}

bool MosfetPwmHal::init() {
    current_duty_ = 0.0f;
    enabled_ = true;
    return true;
}

void MosfetPwmHal::setDutyCycle(float duty_cycle) {
    if (!enabled_) {
        return;
    }

    current_duty_ = std::clamp(duty_cycle, 0.0f, 1.0f);
}

float MosfetPwmHal::getDutyCycle() const {
    return current_duty_;
}

void MosfetPwmHal::emergencyShutdown() {
    current_duty_ = 0.0f;
    enabled_ = false;
}

bool MosfetPwmHal::isEnabled() const {
    return enabled_;
}

std::uint32_t MosfetPwmHal::getFrequency() const {
    return frequency_hz_;
}

std::uint8_t MosfetPwmHal::getPin() const {
    return pwm_pin_;
}
