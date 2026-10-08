#include "continuous_servo.hpp"
#include <algorithm>
#include <cmath>
#include <iostream>

// --- Реалізація ServoGuard ---

ServoGuard::ServoGuard(ContinuousServo& servo)
    : servo_(&servo), active_(true) {}

ServoGuard::~ServoGuard() {
    if (active_ && servo_) {
        servo_->stop();
    }
}

ServoGuard::ServoGuard(ServoGuard&& other) noexcept
    : servo_(other.servo_), active_(other.active_) {
    other.servo_ = nullptr;
    other.active_ = false;
}

ServoGuard& ServoGuard::operator=(ServoGuard&& other) noexcept {
    if (this != &other) {
        if (active_ && servo_) {
            servo_->stop();
        }
        servo_ = other.servo_;
        active_ = other.active_;
        other.servo_ = nullptr;
        other.active_ = false;
    }
    return *this;
}

void ServoGuard::release() noexcept {
    active_ = false;
}

// --- Реалізація ContinuousServo ---

ContinuousServo::ContinuousServo(PwmTimer& timer, ServoPwmConfig config)
    : timer_(timer), config_(config) {
    current_pulse_us_ = getEffectiveNeutralUs();
}

bool ContinuousServo::init() {
    if (!timer_.init()) {
        initialized_ = false;
        return false;
    }

    initialized_ = true;
    stop(); // Початковий стан: зупинка вала та подача імпульсу нейтралі
    return true;
}

uint16_t ContinuousServo::getEffectiveNeutralUs() const noexcept {
    int32_t effective = static_cast<int32_t>(config_.neutral_pulse_us) + config_.trim_offset_us;
    effective = std::clamp(effective, static_cast<int32_t>(config_.min_pulse_us), static_cast<int32_t>(config_.max_pulse_us));
    return static_cast<uint16_t>(effective);
}

uint16_t ContinuousServo::calculatePulseWidthUs(float speed_percent) const noexcept {
    float clamped_speed = std::clamp(speed_percent, -100.0f, 100.0f);
    float effective_neutral = static_cast<float>(getEffectiveNeutralUs());

    if (std::abs(clamped_speed) < 0.01f) {
        return static_cast<uint16_t>(effective_neutral);
    }

    float pulse = effective_neutral;
    if (clamped_speed > 0.0f) {
        // За годинниковою стрілкою: інтерполяція від нейтралі до max_pulse_us
        float range = static_cast<float>(config_.max_pulse_us) - effective_neutral;
        pulse += (clamped_speed / 100.0f) * range;
    } else {
        // Проти годинникової стрілки: інтерполяція від нейтралі до min_pulse_us (clamped_speed від'ємне)
        float range = effective_neutral - static_cast<float>(config_.min_pulse_us);
        pulse += (clamped_speed / 100.0f) * range;
    }

    pulse = std::clamp(pulse, static_cast<float>(config_.min_pulse_us), static_cast<float>(config_.max_pulse_us));
    return static_cast<uint16_t>(std::round(pulse));
}

void ContinuousServo::setSpeed(float speed_percent) {
    if (!initialized_) {
        std::cerr << "[ContinuousServo] Помилка: спроба керування неініціалізованим сервоприводом!\n";
        return;
    }

    current_speed_ = std::clamp(speed_percent, -100.0f, 100.0f);
    current_pulse_us_ = calculatePulseWidthUs(current_speed_);
    timer_.setPulseWidthUs(current_pulse_us_);
}

void ContinuousServo::setSpeed(ServoDirection direction, float speed_percent) {
    float abs_speed = std::abs(speed_percent);
    switch (direction) {
        case ServoDirection::Clockwise:
            setSpeed(abs_speed);
            break;
        case ServoDirection::CounterClockwise:
            setSpeed(-abs_speed);
            break;
        case ServoDirection::Stop:
        default:
            stop();
            break;
    }
}

void ContinuousServo::stop() {
    setSpeed(0.0f);
}

void ContinuousServo::setTrimOffset(int16_t offset_us) {
    config_.trim_offset_us = offset_us;
    std::cout << "[ContinuousServo] Калібрування нейтралі (trim offset): "
              << offset_us << " мкс. Активна нейтраль: " << getEffectiveNeutralUs() << " мкс\n";

    if (initialized_) {
        setSpeed(current_speed_);
    }
}

bool ContinuousServo::isStopped() const noexcept {
    return std::abs(current_speed_) < 0.01f;
}
