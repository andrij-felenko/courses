#include "RvdtDriver.hpp"
#include <algorithm>

namespace hw_controls {

RvdtDriver::RvdtDriver(const RvdtConfig& config) noexcept : config_(config) {}

RvdtReading RvdtDriver::processSample(float v_s1, float v_s2) noexcept {
    last_reading_.v_s1 = v_s1;
    last_reading_.v_s2 = v_s2;
    last_reading_.sum_voltage = v_s1 + v_s2;
    last_reading_.diff_voltage = v_s1 - v_s2;
    last_reading_.error = RvdtError::Ok;

    if (last_reading_.sum_voltage < config_.min_sum_voltage_v) {
        last_reading_.error = last_reading_.error | RvdtError::OpenCircuit;
        return last_reading_;
    }

    if (last_reading_.sum_voltage > config_.max_sum_voltage_v) {
        last_reading_.error = last_reading_.error | RvdtError::ShortCircuit;
        return last_reading_;
    }

    float angle_rad = std::atan2(last_reading_.diff_voltage, last_reading_.sum_voltage);
    float angle_deg = (angle_rad * 180.0f / 3.14159265358979323846f) - config_.zero_offset_deg;

    last_reading_.raw_angle_deg = angle_deg;

    if (std::abs(angle_deg) > config_.max_angle_deg) {
        last_reading_.error = last_reading_.error | RvdtError::OutOfRange;
    }

    float a = std::clamp(config_.alpha_filter, 0.01f, 1.0f);
    last_reading_.filtered_angle_deg = (a * angle_deg) + ((1.0f - a) * last_reading_.filtered_angle_deg);

    return last_reading_;
}

void RvdtDriver::calibrateZero() noexcept {
    config_.zero_offset_deg += last_reading_.raw_angle_deg;
    last_reading_.raw_angle_deg = 0.0f;
    last_reading_.filtered_angle_deg = 0.0f;
}

} // namespace hw_controls
