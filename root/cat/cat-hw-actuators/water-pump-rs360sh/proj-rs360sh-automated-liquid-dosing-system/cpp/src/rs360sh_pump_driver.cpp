#include "rs360sh_pump_driver.hpp"
#include <algorithm>

// Реалізація RAII DosingGuard
DosingGuard::DosingGuard(RS360SHPumpDriver& driver)
    : driver_(&driver), armed_(true) {}

DosingGuard::~DosingGuard() {
    if (armed_ && driver_ != nullptr) {
        driver_->stop();
    }
}

DosingGuard::DosingGuard(DosingGuard&& other) noexcept
    : driver_(other.driver_), armed_(other.armed_) {
    other.driver_ = nullptr;
    other.armed_ = false;
}

DosingGuard& DosingGuard::operator=(DosingGuard&& other) noexcept {
    if (this != &other) {
        if (armed_ && driver_ != nullptr) {
            driver_->stop();
        }
        driver_ = other.driver_;
        armed_ = other.armed_;
        other.driver_ = nullptr;
        other.armed_ = false;
    }
    return *this;
}

void DosingGuard::dismiss() {
    armed_ = false;
}

// Реалізація RS360SHPumpDriver
RS360SHPumpDriver::RS360SHPumpDriver(MosfetPwmHal& pwm_hal, const PumpConfig& config)
    : pwm_hal_(pwm_hal), config_(config) {}

bool RS360SHPumpDriver::init() {
    state_ = PumpState::Idle;
    last_error_ = PumpError::None;
    dosed_volume_ml_ = 0.0f;
    dry_run_detected_ = false;
    return pwm_hal_.init();
}

bool RS360SHPumpDriver::startDosingVolume(float target_volume_ml, float target_duty) {
    if (state_ == PumpState::FaultDryRun || target_volume_ml <= 0.0f) {
        return false;
    }

    target_volume_ml_ = target_volume_ml;
    target_pwm_duty_ = std::clamp(target_duty, config_.min_operating_duty, config_.max_operating_duty);
    dosed_volume_ml_ = 0.0f;
    is_volume_mode_ = true;
    dry_run_detected_ = false;
    last_error_ = PumpError::None;

    float steady_flow_rate = config_.max_flow_rate_ml_per_sec * target_pwm_duty_;
    float ramp_volume = 0.5f * steady_flow_rate * (config_.ramp_up_duration_ms + config_.ramp_down_duration_ms) / 1000.0f;

    if (target_volume_ml_ <= ramp_volume) {
        total_target_duration_ms_ = config_.ramp_up_duration_ms + config_.ramp_down_duration_ms;
    } else {
        float remaining_volume = target_volume_ml_ - ramp_volume;
        std::uint32_t steady_time_ms = static_cast<std::uint32_t>((remaining_volume / steady_flow_rate) * 1000.0f);
        total_target_duration_ms_ = config_.ramp_up_duration_ms + steady_time_ms + config_.ramp_down_duration_ms;
    }

    transitionTo(PumpState::RampUp, 0);
    return true;
}

bool RS360SHPumpDriver::startDosingTime(std::uint32_t target_duration_ms, float target_duty) {
    if (state_ == PumpState::FaultDryRun || target_duration_ms == 0) {
        return false;
    }

    total_target_duration_ms_ = target_duration_ms;
    target_pwm_duty_ = std::clamp(target_duty, config_.min_operating_duty, config_.max_operating_duty);
    dosed_volume_ml_ = 0.0f;
    is_volume_mode_ = false;
    dry_run_detected_ = false;
    last_error_ = PumpError::None;

    transitionTo(PumpState::RampUp, 0);
    return true;
}

void RS360SHPumpDriver::stop() {
    if (state_ == PumpState::Idle) {
        return;
    }
    pwm_hal_.setDutyCycle(0.0f);
    current_pwm_duty_ = 0.0f;
    state_ = PumpState::Idle;
}

void RS360SHPumpDriver::update(std::uint32_t current_time_ms,
                               const FlowSensorData& flow_data,
                               const DryRunSensorData& dry_run_data) {
    if (state_ == PumpState::Idle) {
        return;
    }

    if (state_ == PumpState::FaultDryRun) {
        pwm_hal_.emergencyShutdown();
        return;
    }

    if (last_update_time_ms_ == 0) {
        last_update_time_ms_ = current_time_ms;
        state_start_time_ms_ = current_time_ms;
    }

    std::uint32_t dt_ms = current_time_ms - last_update_time_ms_;
    last_update_time_ms_ = current_time_ms;

    std::uint32_t elapsed_in_state_ms = current_time_ms - state_start_time_ms_;

    handleDryRunCheck(current_time_ms, flow_data, dry_run_data);
    if (state_ == PumpState::FaultDryRun) {
        return;
    }

    switch (state_) {
    case PumpState::RampUp: {
        if (config_.ramp_up_duration_ms == 0 || elapsed_in_state_ms >= config_.ramp_up_duration_ms) {
            current_pwm_duty_ = target_pwm_duty_;
            pwm_hal_.setDutyCycle(current_pwm_duty_);
            transitionTo(PumpState::Dosing, current_time_ms);
        } else {
            float progress = static_cast<float>(elapsed_in_state_ms) / static_cast<float>(config_.ramp_up_duration_ms);
            current_pwm_duty_ = progress * target_pwm_duty_;
            pwm_hal_.setDutyCycle(current_pwm_duty_);
        }
        break;
    }

    case PumpState::Dosing: {
        current_pwm_duty_ = target_pwm_duty_;
        pwm_hal_.setDutyCycle(current_pwm_duty_);

        bool time_to_ramp_down = false;
        std::uint32_t total_elapsed_ms = current_time_ms - (state_start_time_ms_ - config_.ramp_up_duration_ms);

        if (is_volume_mode_) {
            float steady_flow = config_.max_flow_rate_ml_per_sec * current_pwm_duty_;
            float ramp_down_vol = 0.5f * steady_flow * (config_.ramp_down_duration_ms / 1000.0f);
            if (dosed_volume_ml_ + ramp_down_vol >= target_volume_ml_) {
                time_to_ramp_down = true;
            }
        } else {
            if (total_elapsed_ms + config_.ramp_down_duration_ms >= total_target_duration_ms_) {
                time_to_ramp_down = true;
            }
        }

        if (time_to_ramp_down) {
            transitionTo(PumpState::RampDown, current_time_ms);
        }
        break;
    }

    case PumpState::RampDown: {
        if (config_.ramp_down_duration_ms == 0 || elapsed_in_state_ms >= config_.ramp_down_duration_ms) {
            current_pwm_duty_ = 0.0f;
            pwm_hal_.setDutyCycle(0.0f);
            transitionTo(PumpState::Idle, current_time_ms);
        } else {
            float progress = 1.0f - (static_cast<float>(elapsed_in_state_ms) / static_cast<float>(config_.ramp_down_duration_ms));
            current_pwm_duty_ = progress * target_pwm_duty_;
            pwm_hal_.setDutyCycle(current_pwm_duty_);
        }
        break;
    }

    default:
        break;
    }

    if (dt_ms > 0 && current_pwm_duty_ > 0.0f) {
        float dt_sec = static_cast<float>(dt_ms) / 1000.0f;
        float instant_flow_ml_per_sec = 0.0f;

        if (flow_data.sensor_present && flow_data.current_flow_ml_per_sec > 0.0f) {
            instant_flow_ml_per_sec = flow_data.current_flow_ml_per_sec;
        } else {
            instant_flow_ml_per_sec = config_.max_flow_rate_ml_per_sec * current_pwm_duty_;
        }

        dosed_volume_ml_ += instant_flow_ml_per_sec * dt_sec;
    }
}

void RS360SHPumpDriver::handleDryRunCheck(std::uint32_t current_time_ms,
                                          const FlowSensorData& flow_data,
                                          const DryRunSensorData& dry_run_data) {
    if (current_pwm_duty_ < config_.min_operating_duty) {
        dry_run_timer_ms_ = 0;
        return;
    }

    bool dry_condition = false;

    if (!dry_run_data.fluid_detected) {
        dry_condition = true;
    }

    if (flow_data.sensor_present && flow_data.current_flow_ml_per_sec <= 0.001f) {
        dry_condition = true;
    }

    if (dry_condition) {
        if (dry_run_timer_ms_ == 0) {
            dry_run_timer_ms_ = current_time_ms;
        } else if (current_time_ms - dry_run_timer_ms_ >= config_.dry_run_timeout_ms) {
            dry_run_detected_ = true;
            last_error_ = PumpError::DryRun;
            pwm_hal_.emergencyShutdown();
            transitionTo(PumpState::FaultDryRun, current_time_ms);
        }
    } else {
        dry_run_timer_ms_ = 0;
    }
}

void RS360SHPumpDriver::transitionTo(PumpState new_state, std::uint32_t current_time_ms) {
    state_ = new_state;
    state_start_time_ms_ = current_time_ms;
}

PumpState RS360SHPumpDriver::getState() const {
    return state_;
}

PumpError RS360SHPumpDriver::getLastError() const {
    return last_error_;
}

float RS360SHPumpDriver::getDosedVolumeMl() const {
    return dosed_volume_ml_;
}

bool RS360SHPumpDriver::isDryRunDetected() const {
    return dry_run_detected_;
}

void RS360SHPumpDriver::setFlowRateCalibration(float ml_per_sec_at_max_duty) {
    if (ml_per_sec_at_max_duty > 0.0f) {
        config_.max_flow_rate_ml_per_sec = ml_per_sec_at_max_duty;
    }
}

void RS360SHPumpDriver::clearFault() {
    if (state_ == PumpState::FaultDryRun) {
        state_ = PumpState::Idle;
        last_error_ = PumpError::None;
        dry_run_detected_ = false;
        dry_run_timer_ms_ = 0;
        pwm_hal_.init();
    }
}
