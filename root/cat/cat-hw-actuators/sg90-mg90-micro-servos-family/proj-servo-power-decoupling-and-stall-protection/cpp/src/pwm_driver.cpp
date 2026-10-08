#include "pwm_driver.hpp"
#include <algorithm>

namespace towerpro {

PwmDriver::~PwmDriver() {
    detach();
}

bool PwmDriver::begin(uint8_t pin) {
    pin_ = pin;
    attached_ = true;
    hardwareSetPulse(currentPulseUs_);
    return true;
}

void PwmDriver::writeMicroseconds(uint16_t pulseUs) {
    currentPulseUs_ = std::clamp(pulseUs, static_cast<uint16_t>(500), static_cast<uint16_t>(2500));
    if (attached_) {
        hardwareSetPulse(currentPulseUs_);
    }
}

void PwmDriver::detach() {
    if (attached_) {
        attached_ = false;
        hardwareDetach();
    }
}

void PwmDriver::attach() {
    if (!attached_) {
        attached_ = true;
        hardwareSetPulse(currentPulseUs_);
    }
}

bool PwmDriver::isAttached() const {
    return attached_;
}

uint16_t PwmDriver::getPulseMicroseconds() const {
    return currentPulseUs_;
}

uint8_t PwmDriver::getPin() const {
    return pin_;
}

void PwmDriver::hardwareSetPulse(uint16_t pulseUs) {
    // Низькорівнева установка імпульсу на виводі MCU
    (void)pulseUs;
}

void PwmDriver::hardwareDetach() {
    // Зняття ШІМ-сигналу та переведення виводу у стан High-Z/Low
}

} // namespace towerpro
