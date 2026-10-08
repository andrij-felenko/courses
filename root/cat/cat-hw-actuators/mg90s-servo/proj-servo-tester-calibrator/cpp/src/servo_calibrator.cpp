#include "servo_calibrator.hpp"
#include <algorithm>
#include <cmath>

namespace actuators {

ServoCalibrator::ServoCalibrator(ServoPwmGenerator& pwm_gen, CurrentMonitor& current_mon)
    : pwm_(pwm_gen), monitor_(current_mon) {
}

bool ServoCalibrator::initialize() {
    pwm_.initialize();
    monitor_.initialize();
    mode_ = CalibratorMode::Disabled;
    target_angle_deg_ = pwm_.get_current_angle();
    return true;
}

void ServoCalibrator::update(uint16_t raw_adc_current) {
    monitor_.process_sample(raw_adc_current);
    enforce_safety_check();

    if (mode_ == CalibratorMode::AutoScan) {
        process_auto_scan();
    }
}

void ServoCalibrator::update_simulated(float current_ma) {
    monitor_.process_direct_ma(current_ma);
    enforce_safety_check();

    if (mode_ == CalibratorMode::AutoScan) {
        process_auto_scan();
    }
}

bool ServoCalibrator::set_mode(CalibratorMode mode) {
    if (mode_ == CalibratorMode::EmergencyStop && mode != CalibratorMode::EmergencyStop) {
        // Заборонено виходити з аварійного стану без виклику reset_emergency_stop()
        return false;
    }

    mode_ = mode;

    switch (mode_) {
        case CalibratorMode::Disabled:
            pwm_.disable();
            break;
        case CalibratorMode::Manual:
        case CalibratorMode::AutoScan:
            pwm_.enable();
            pwm_.set_angle(target_angle_deg_);
            break;
        case CalibratorMode::EmergencyStop:
            pwm_.disable();
            break;
    }

    return true;
}

CalibratorMode ServoCalibrator::get_mode() const {
    return mode_;
}

std::string_view ServoCalibrator::get_mode_name() const {
    switch (mode_) {
        case CalibratorMode::Disabled:      return "Disabled";
        case CalibratorMode::Manual:        return "Manual";
        case CalibratorMode::AutoScan:      return "AutoScan";
        case CalibratorMode::EmergencyStop: return "EMERGENCY_STOP";
    }
    return "Unknown";
}

bool ServoCalibrator::set_target_angle(float angle_deg) {
    if (mode_ == CalibratorMode::EmergencyStop || mode_ == CalibratorMode::Disabled) {
        return false;
    }

    float clamped_target = std::clamp(angle_deg, limits_.min_angle_deg, limits_.max_angle_deg);
    target_angle_deg_ = clamped_target;
    return pwm_.set_angle(target_angle_deg_);
}

bool ServoCalibrator::step_angle(float delta_deg) {
    return set_target_angle(target_angle_deg_ + delta_deg);
}

void ServoCalibrator::set_scan_params(float step_deg, bool auto_reverse) {
    scan_step_deg_ = std::abs(step_deg);
    auto_reverse_scan_ = auto_reverse;
}

void ServoCalibrator::set_limits(const CalibrationLimits& limits) {
    limits_.min_angle_deg = std::max(pwm_.get_config().min_angle_deg, limits.min_angle_deg);
    limits_.max_angle_deg = std::min(pwm_.get_config().max_angle_deg, limits.max_angle_deg);
    
    if (limits_.min_angle_deg > limits_.max_angle_deg) {
        std::swap(limits_.min_angle_deg, limits_.max_angle_deg);
    }

    limits_.min_pulse_us = pwm_.angle_to_pulse_us(limits_.min_angle_deg);
    limits_.max_pulse_us = pwm_.angle_to_pulse_us(limits_.max_angle_deg);

    // Впевнюємось, що поточний кут залишається в нових межах
    set_target_angle(target_angle_deg_);
}

const CalibrationLimits& ServoCalibrator::get_limits() const {
    return limits_;
}

bool ServoCalibrator::calibrate_current_as_min() {
    float current_angle = pwm_.get_current_angle();
    if (current_angle >= limits_.max_angle_deg) {
        return false;
    }

    limits_.min_angle_deg = current_angle;
    limits_.min_pulse_us = pwm_.get_current_pulse_us();
    return true;
}

bool ServoCalibrator::calibrate_current_as_max() {
    float current_angle = pwm_.get_current_angle();
    if (current_angle <= limits_.min_angle_deg) {
        return false;
    }

    limits_.max_angle_deg = current_angle;
    limits_.max_pulse_us = pwm_.get_current_pulse_us();
    return true;
}

bool ServoCalibrator::is_emergency_stop() const {
    return mode_ == CalibratorMode::EmergencyStop;
}

void ServoCalibrator::reset_emergency_stop() {
    monitor_.reset_stall_alarm();
    mode_ = CalibratorMode::Manual;
    pwm_.enable();
    pwm_.set_angle(target_angle_deg_);
}

void ServoCalibrator::process_auto_scan() {
    if (mode_ != CalibratorMode::AutoScan || !pwm_.is_enabled()) {
        return;
    }

    float next_angle = target_angle_deg_;
    if (scan_direction_forward_) {
        next_angle += scan_step_deg_;
        if (next_angle >= limits_.max_angle_deg) {
            next_angle = limits_.max_angle_deg;
            if (auto_reverse_scan_) {
                scan_direction_forward_ = false;
            }
        }
    } else {
        next_angle -= scan_step_deg_;
        if (next_angle <= limits_.min_angle_deg) {
            next_angle = limits_.min_angle_deg;
            if (auto_reverse_scan_) {
                scan_direction_forward_ = true;
            }
        }
    }

    set_target_angle(next_angle);
}

void ServoCalibrator::enforce_safety_check() {
    if (monitor_.is_stall_detected()) {
        mode_ = CalibratorMode::EmergencyStop;
        pwm_.disable();
    }
}

} // namespace actuators
