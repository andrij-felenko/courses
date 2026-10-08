#include "servo_pwm.hpp"
#include <algorithm>
#include <cmath>

namespace actuators {

ServoPwmGenerator::ServoPwmGenerator(const ServoPwmConfig& config)
    : config_(config) {
    // Встановлюємо початкове значення у нейтральне положення (90 градусів)
    current_angle_deg_ = (config_.min_angle_deg + config_.max_angle_deg) / 2.0f;
    current_pulse_us_ = angle_to_pulse_us(current_angle_deg_);
}

bool ServoPwmGenerator::initialize() {
    // Налаштування таймерної периферії для генерації 50 Гц ШІМ
    enabled_ = false;
    current_pulse_us_ = angle_to_pulse_us(current_angle_deg_);
    return true;
}

void ServoPwmGenerator::enable() {
    enabled_ = true;
    apply_hardware_pwm(current_pulse_us_);
}

void ServoPwmGenerator::disable() {
    enabled_ = false;
    // Апаратне зняття імпульсів з виходу керування (виставити 0V)
    apply_hardware_pwm(0);
}

bool ServoPwmGenerator::is_enabled() const {
    return enabled_;
}

bool ServoPwmGenerator::set_angle(float angle_deg) {
    float clamped = clamp_angle(angle_deg);
    current_angle_deg_ = clamped;
    current_pulse_us_ = angle_to_pulse_us(clamped);

    if (enabled_) {
        apply_hardware_pwm(current_pulse_us_);
    }

    // Повертаємо true, якщо вхідне значення не потребувало обмеження
    return std::abs(angle_deg - clamped) < 0.001f;
}

bool ServoPwmGenerator::set_pulse_width_us(uint16_t pulse_us) {
    uint16_t clamped = clamp_pulse_us(pulse_us);
    current_pulse_us_ = clamped;
    current_angle_deg_ = pulse_us_to_angle(clamped);

    if (enabled_) {
        apply_hardware_pwm(current_pulse_us_);
    }

    return (pulse_us == clamped);
}

float ServoPwmGenerator::get_current_angle() const {
    return current_angle_deg_;
}

uint16_t ServoPwmGenerator::get_current_pulse_us() const {
    return current_pulse_us_;
}

const ServoPwmConfig& ServoPwmGenerator::get_config() const {
    return config_;
}

uint16_t ServoPwmGenerator::angle_to_pulse_us(float angle_deg) const {
    float clamped = clamp_angle(angle_deg);
    float angle_range = config_.max_angle_deg - config_.min_angle_deg;
    if (angle_range <= 0.0f) {
        return config_.min_pulse_us;
    }

    float normalized = (clamped - config_.min_angle_deg) / angle_range;
    float pulse_range = static_cast<float>(config_.max_pulse_us - config_.min_pulse_us);
    float pulse = static_cast<float>(config_.min_pulse_us) + (normalized * pulse_range);
    
    return clamp_pulse_us(static_cast<uint16_t>(std::round(pulse)));
}

float ServoPwmGenerator::pulse_us_to_angle(uint16_t pulse_us) const {
    uint16_t clamped = clamp_pulse_us(pulse_us);
    float pulse_range = static_cast<float>(config_.max_pulse_us - config_.min_pulse_us);
    if (pulse_range <= 0.0f) {
        return config_.min_angle_deg;
    }

    float normalized = static_cast<float>(clamped - config_.min_pulse_us) / pulse_range;
    float angle_range = config_.max_angle_deg - config_.min_angle_deg;
    float angle = config_.min_angle_deg + (normalized * angle_range);

    return clamp_angle(angle);
}

float ServoPwmGenerator::clamp_angle(float angle_deg) const {
    return std::clamp(angle_deg, config_.min_angle_deg, config_.max_angle_deg);
}

uint16_t ServoPwmGenerator::clamp_pulse_us(uint16_t pulse_us) const {
    return std::clamp(pulse_us, config_.min_pulse_us, config_.max_pulse_us);
}

void ServoPwmGenerator::apply_hardware_pwm(uint16_t pulse_us) {
    // В реальній прошивці тут відбувається запис у регістр таймера (наприклад, TIMx->CCR1).
    // Для симуляції та верифікації стан імпульсів оновлюється в об'єкті.
    (void)pulse_us;
}

} // namespace actuators
