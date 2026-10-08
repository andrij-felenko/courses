#include "current_monitor.hpp"
#include <algorithm>
#include <cmath>
#include <numeric>

namespace actuators {

CurrentMonitor::CurrentMonitor(const CurrentMonitorConfig& config)
    : config_(config) {
    sample_buffer_.fill(0.0f);
}

void CurrentMonitor::initialize() {
    sample_buffer_.fill(0.0f);
    buffer_index_ = 0;
    sample_count_ = 0;
    filtered_current_ma_ = 0.0f;
    peak_current_ma_ = 0.0f;
    overcurrent_counter_ = 0;
    stall_flag_ = false;
}

float CurrentMonitor::process_sample(uint16_t raw_adc) {
    float current_ma = raw_adc_to_ma(raw_adc);
    return process_direct_ma(current_ma);
}

float CurrentMonitor::process_direct_ma(float current_ma) {
    update_moving_average(current_ma);
    
    if (filtered_current_ma_ > peak_current_ma_) {
        peak_current_ma_ = filtered_current_ma_;
    }

    check_stall_condition();
    return filtered_current_ma_;
}

float CurrentMonitor::get_raw_adc_voltage(uint16_t raw_adc) const {
    uint32_t max_adc = (1U << config_.adc_resolution_bits) - 1U;
    if (max_adc == 0) {
        return 0.0f;
    }
    return (static_cast<float>(raw_adc) * config_.ref_voltage_v) / static_cast<float>(max_adc);
}

float CurrentMonitor::raw_adc_to_ma(uint16_t raw_adc) const {
    float voltage_v = get_raw_adc_voltage(raw_adc);
    float delta_v = std::abs(voltage_v - config_.zero_offset_v);
    float delta_mv = delta_v * 1000.0f;

    if (config_.sensor_sensitivity_mv_per_ma <= 0.0f) {
        return 0.0f;
    }

    return delta_mv / config_.sensor_sensitivity_mv_per_ma;
}

float CurrentMonitor::get_filtered_current_ma() const {
    return filtered_current_ma_;
}

float CurrentMonitor::get_peak_current_ma() const {
    return peak_current_ma_;
}

bool CurrentMonitor::is_stall_detected() const {
    return stall_flag_;
}

void CurrentMonitor::set_stall_threshold_ma(float ma) {
    config_.stall_threshold_ma = std::max(0.0f, ma);
}

void CurrentMonitor::reset_stall_alarm() {
    stall_flag_ = false;
    overcurrent_counter_ = 0;
}

void CurrentMonitor::reset_statistics() {
    peak_current_ma_ = filtered_current_ma_;
}

void CurrentMonitor::update_moving_average(float new_ma) {
    sample_buffer_[buffer_index_] = new_ma;
    buffer_index_ = (buffer_index_ + 1) % FILTER_WINDOW_SIZE;

    if (sample_count_ < FILTER_WINDOW_SIZE) {
        sample_count_++;
    }

    float sum = std::accumulate(sample_buffer_.begin(), 
                                sample_buffer_.begin() + sample_count_, 
                                0.0f);
    filtered_current_ma_ = sum / static_cast<float>(sample_count_);
}

void CurrentMonitor::check_stall_condition() {
    if (filtered_current_ma_ >= config_.stall_threshold_ma) {
        if (overcurrent_counter_ < config_.stall_confirm_samples) {
            overcurrent_counter_++;
        }
        if (overcurrent_counter_ >= config_.stall_confirm_samples) {
            stall_flag_ = true;
        }
    } else {
        if (overcurrent_counter_ > 0) {
            overcurrent_counter_--;
        }
    }
}

} // namespace actuators
