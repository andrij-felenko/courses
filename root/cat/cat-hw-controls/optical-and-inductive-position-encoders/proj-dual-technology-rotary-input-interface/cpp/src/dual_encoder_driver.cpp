#include "dual_encoder_driver.hpp"
#include <algorithm>
#include <numeric>
#include <cmath>

namespace controls::encoders {

// Реалізація OpticalEncoderSensor
OpticalEncoderSensor::OpticalEncoderSensor(int32_t counts_per_rev)
    : cpr_(counts_per_rev > 0 ? counts_per_rev : 4096) {}

EncoderPosition OpticalEncoderSensor::read_position() {
    clock_us_ += 1000;
    EncoderPosition pos;
    pos.timestamp_us = clock_us_;
    pos.raw_value = static_cast<double>(pulse_count_);
    pos.health = health_;

    if (health_ != SensorHealth::OK) {
        pos.angle_deg = 0.0;
        return pos;
    }

    double degrees_per_count = 360.0 / static_cast<double>(cpr_);
    double uncompensated_angle = pulse_count_ * degrees_per_count;
    
    uncompensated_angle = std::fmod(uncompensated_angle + 180.0, 360.0);
    if (uncompensated_angle < 0) {
        uncompensated_angle += 360.0;
    }
    uncompensated_angle -= 180.0;

    pos.angle_deg = uncompensated_angle - zero_offset_deg_;
    return pos;
}

bool OpticalEncoderSensor::self_test() {
    return health_ == SensorHealth::OK;
}

void OpticalEncoderSensor::set_zero_offset(double offset_deg) {
    zero_offset_deg_ = offset_deg;
}

double OpticalEncoderSensor::get_zero_offset() const {
    return zero_offset_deg_;
}

void OpticalEncoderSensor::simulate_pulse_input(int32_t delta_pulses) {
    pulse_count_ += delta_pulses;
}

void OpticalEncoderSensor::set_hardware_fault(bool fault) {
    health_ = fault ? SensorHealth::HARDWARE_FAULT : SensorHealth::OK;
}

void OpticalEncoderSensor::set_index_pulse_detected(bool detected) {
    index_found_ = detected;
}

// Реалізація InductiveRvdtSensor
InductiveRvdtSensor::InductiveRvdtSensor(double v_ref_volts, double sensitivity_mv_per_deg)
    : v_ref_(v_ref_volts), sensitivity_mv_per_deg_(sensitivity_mv_per_deg) {}

EncoderPosition InductiveRvdtSensor::read_position() {
    clock_us_ += 1000;
    EncoderPosition pos;
    pos.timestamp_us = clock_us_;
    pos.raw_value = raw_voltage_;
    pos.health = health_;

    if (health_ != SensorHealth::OK) {
        pos.angle_deg = 0.0;
        return pos;
    }

    double delta_v = raw_voltage_ - (v_ref_ / 2.0);
    double sensitivity_v_per_deg = sensitivity_mv_per_deg_ / 1000.0;
    double uncompensated_angle = delta_v / sensitivity_v_per_deg;

    pos.angle_deg = uncompensated_angle - zero_offset_deg_;
    return pos;
}

bool InductiveRvdtSensor::self_test() {
    if (raw_voltage_ < 0.2 || raw_voltage_ > (v_ref_ - 0.2)) {
        health_ = SensorHealth::OUT_OF_RANGE;
        return false;
    }
    return health_ == SensorHealth::OK;
}

void InductiveRvdtSensor::set_zero_offset(double offset_deg) {
    zero_offset_deg_ = offset_deg;
}

double InductiveRvdtSensor::get_zero_offset() const {
    return zero_offset_deg_;
}

void InductiveRvdtSensor::simulate_adc_voltage(double voltage_volts) {
    raw_voltage_ = voltage_volts;
    self_test();
}

void InductiveRvdtSensor::set_hardware_fault(bool fault) {
    health_ = fault ? SensorHealth::HARDWARE_FAULT : SensorHealth::OK;
}

// Реалізація DualEncoderDriver
DualEncoderDriver::DualEncoderDriver(std::unique_ptr<IPositionSensor> optical_sensor,
                                     std::unique_ptr<IPositionSensor> rvdt_sensor,
                                     DriverConfig config)
    : optical_(std::move(optical_sensor)),
      rvdt_(std::move(rvdt_sensor)),
      config_(config) {
    if (optical_) {
        optical_->set_zero_offset(config_.zero_offset_optical_deg);
    }
    if (rvdt_) {
        rvdt_->set_zero_offset(config_.zero_offset_rvdt_deg);
    }
}

DiagnosticReport DualEncoderDriver::update() {
    system_tick_ms_ += 10;
    DiagnosticReport report;
    report.calibration = calibration_state_;

    if (!optical_ || !rvdt_) {
        report.system_valid = false;
        report.status = DiscrepancyStatus::CRITICAL_FAULT;
        report.status_message = "Помилка: Один із каналів давачів відсутній";
        last_report_ = report;
        return report;
    }

    EncoderPosition pos_opt = optical_->read_position();
    EncoderPosition pos_rvdt = rvdt_->read_position();

    report.optical_angle_deg = pos_opt.angle_deg;
    report.rvdt_angle_deg = pos_rvdt.angle_deg;

    bool opt_healthy = (pos_opt.health == SensorHealth::OK) && optical_->self_test();
    bool rvdt_healthy = (pos_rvdt.health == SensorHealth::OK) && rvdt_->self_test();

    if (!opt_healthy || !rvdt_healthy) {
        report.system_valid = false;
        report.status = DiscrepancyStatus::CRITICAL_FAULT;
        report.status_message = "Апаратна відмова: ";
        if (!opt_healthy) report.status_message += "[Оптичний канал несправний] ";
        if (!rvdt_healthy) report.status_message += "[RVDT канал несправний]";
        
        last_report_ = report;
        if (callback_) {
            callback_(report);
        }
        return report;
    }

    if (calibration_state_ == CalibrationState::IN_PROGRESS) {
        process_calibration_sample(pos_opt.angle_deg, pos_rvdt.angle_deg);
        report.status = DiscrepancyStatus::CALIBRATION_NEEDED;
        report.status_message = "Виконується автокалібрування нульової точки...";
        report.fused_angle_deg = pos_opt.angle_deg;
        report.system_valid = true;
        last_report_ = report;
        return report;
    }

    double raw_diff = std::abs(pos_opt.angle_deg - pos_rvdt.angle_deg);
    report.current_discrepancy_deg = raw_diff;

    report.status = evaluate_discrepancy(raw_diff);

    double candidate_fused = (0.7 * pos_opt.angle_deg) + (0.3 * pos_rvdt.angle_deg);

    if (first_update_) {
        prev_fused_angle_ = candidate_fused;
        first_update_ = false;
    }
    report.fused_angle_deg = filter_outliers(candidate_fused, prev_fused_angle_, config_.max_single_step_spike_deg);
    prev_fused_angle_ = report.fused_angle_deg;

    if (report.status == DiscrepancyStatus::CRITICAL_FAULT) {
        if (discrepancy_start_time_ms_ == 0) {
            discrepancy_start_time_ms_ = system_tick_ms_;
        }
        
        uint64_t duration = system_tick_ms_ - discrepancy_start_time_ms_;
        if (duration >= config_.discrepancy_timeout_ms) {
            report.system_valid = false;
            report.status_message = "КРИТИЧНА ПОМИЛКА: Перевищено ліміт часу розбіжності каналів (Discrepancy Event)";
        } else {
            report.system_valid = true;
            report.status_message = "УВАГА: Фіксація розбіжності каналів (накопичення таймера аварії)";
        }
    } else {
        discrepancy_start_time_ms_ = 0;
        report.system_valid = true;
        if (report.status == DiscrepancyStatus::WARNING) {
            report.status_message = "Попередження: Дрібне відхилення між оптичним та індуктивним каналом";
        } else {
            report.status_message = "Нормальний режим: Канали узгоджені";
        }
    }

    last_report_ = report;

    if (report.status != DiscrepancyStatus::OK && callback_) {
        callback_(report);
    }

    return report;
}

bool DualEncoderDriver::start_auto_zero_calibration() {
    calibration_samples_optical_.clear();
    calibration_samples_rvdt_.clear();
    calibration_samples_optical_.reserve(config_.calibration_samples_count);
    calibration_samples_rvdt_.reserve(config_.calibration_samples_count);
    
    calibration_state_ = CalibrationState::IN_PROGRESS;
    return true;
}

DiagnosticReport DualEncoderDriver::get_last_report() const {
    return last_report_;
}

void DualEncoderDriver::set_config(const DriverConfig& config) {
    config_ = config;
}

DriverConfig DualEncoderDriver::get_config() const {
    return config_;
}

void DualEncoderDriver::register_discrepancy_callback(DiscrepancyCallback callback) {
    callback_ = callback;
}

double DualEncoderDriver::filter_outliers(double current_val, double prev_val, double max_step) {
    double delta = std::abs(current_val - prev_val);
    if (delta > max_step) {
        return (current_val > prev_val) ? (prev_val + max_step) : (prev_val - max_step);
    }
    return current_val;
}

DiscrepancyStatus DualEncoderDriver::evaluate_discrepancy(double diff_deg) {
    if (diff_deg > config_.max_allowed_discrepancy_deg) {
        return DiscrepancyStatus::CRITICAL_FAULT;
    }
    if (diff_deg > config_.warning_discrepancy_deg) {
        return DiscrepancyStatus::WARNING;
    }
    return DiscrepancyStatus::OK;
}

void DualEncoderDriver::process_calibration_sample(double optical_angle, double rvdt_angle) {
    calibration_samples_optical_.push_back(optical_angle);
    calibration_samples_rvdt_.push_back(rvdt_angle);

    if (calibration_samples_optical_.size() >= config_.calibration_samples_count) {
        finalize_calibration();
    }
}

void DualEncoderDriver::finalize_calibration() {
    if (calibration_samples_optical_.empty() || calibration_samples_rvdt_.empty()) {
        calibration_state_ = CalibrationState::FAILED;
        return;
    }

    double sum_opt = std::accumulate(calibration_samples_optical_.begin(), calibration_samples_optical_.end(), 0.0);
    double sum_rvdt = std::accumulate(calibration_samples_rvdt_.begin(), calibration_samples_rvdt_.end(), 0.0);

    double mean_opt_err = sum_opt / static_cast<double>(calibration_samples_optical_.size());
    double mean_rvdt_err = sum_rvdt / static_cast<double>(calibration_samples_rvdt_.size());

    double new_opt_zero = optical_->get_zero_offset() + mean_opt_err;
    double new_rvdt_zero = rvdt_->get_zero_offset() + mean_rvdt_err;

    optical_->set_zero_offset(new_opt_zero);
    rvdt_->set_zero_offset(new_rvdt_zero);

    config_.zero_offset_optical_deg = new_opt_zero;
    config_.zero_offset_rvdt_deg = new_rvdt_zero;

    calibration_state_ = CalibrationState::CALIBRATED;
}

} // namespace controls::encoders
