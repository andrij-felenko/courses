#include "plausibility_checker.hpp"
#include <algorithm>
#include <cmath>

namespace isa18_2 {

PlausibilityChecker::PlausibilityChecker(const PlausibilityConfig& config) noexcept
    : config_(config) {}

SensorConfidenceEstimate PlausibilityChecker::evaluate_triple_redundancy(
    float s1, float s2, float s3, float noise_sigma, float max_spread) noexcept {

    SensorConfidenceEstimate est{};
    std::array<float, 3> vals{s1, s2, s3};
    std::sort(vals.begin(), vals.end());
    const float median = vals[1];

    const float d12 = std::abs(s1 - s2);
    const float d23 = std::abs(s2 - s3);
    const float d31 = std::abs(s3 - s1);
    const float max_diff = std::max({d12, d23, d31});

    est.estimated_value = median;
    est.residual = max_diff;

    if (max_diff <= max_spread) {
        est.variance = (noise_sigma * noise_sigma) / 3.0f;
        est.confidence_bound_95 = 1.96f * std::sqrt(est.variance);
        est.confidence_score = std::max(0.0f, 1.0f - (max_diff / (max_spread * 2.0f)));
        est.status = PlausibilityStatus::Valid;
    } else if (d12 <= max_spread || d23 <= max_spread || d31 <= max_spread) {
        est.variance = (noise_sigma * noise_sigma) / 2.0f;
        est.confidence_bound_95 = 1.96f * std::sqrt(est.variance);
        est.confidence_score = 0.65f;
        est.status = PlausibilityStatus::Degraded;
    } else {
        est.variance = noise_sigma * noise_sigma * 4.0f;
        est.confidence_bound_95 = 1.96f * std::sqrt(est.variance);
        est.confidence_score = 0.15f;
        est.status = PlausibilityStatus::Failed;
    }

    return est;
}

void PlausibilityChecker::check_kinematics(float imu_accel_x, float gnss_vel_x, std::chrono::milliseconds now) noexcept {
    if (last_eval_time_ == 0ms) {
        last_eval_time_ = now;
        last_imu_accel_x_ = imu_accel_x;
        last_gnss_vel_x_ = gnss_vel_x;
        nav_velocity_confidence_.estimated_value = gnss_vel_x;
        nav_velocity_confidence_.confidence_score = 1.0f;
        nav_velocity_confidence_.status = PlausibilityStatus::Valid;
        return;
    }

    const float dt = std::chrono::duration<float>(now - last_eval_time_).count();
    if (dt <= 0.0001f) return;

    const float gnss_accel_x = (gnss_vel_x - last_gnss_vel_x_) / dt;
    const float residual = std::abs(gnss_accel_x - imu_accel_x);

    nav_velocity_confidence_.estimated_value = gnss_vel_x;
    nav_velocity_confidence_.residual = residual;
    nav_velocity_confidence_.variance = residual * 0.25f + 0.05f;
    nav_velocity_confidence_.confidence_bound_95 = 1.96f * std::sqrt(nav_velocity_confidence_.variance);

    if (residual < config_.max_kinematic_residual * 0.5f) {
        nav_velocity_confidence_.status = PlausibilityStatus::Valid;
        nav_velocity_confidence_.confidence_score = 0.95f;
    } else if (residual < config_.max_kinematic_residual) {
        nav_velocity_confidence_.status = PlausibilityStatus::Degraded;
        nav_velocity_confidence_.confidence_score = 0.70f;
    } else if (residual < config_.max_kinematic_residual * 2.0f) {
        nav_velocity_confidence_.status = PlausibilityStatus::Suspect;
        nav_velocity_confidence_.confidence_score = 0.35f;
    } else {
        nav_velocity_confidence_.status = PlausibilityStatus::Failed;
        nav_velocity_confidence_.confidence_score = 0.05f;
    }

    last_eval_time_ = now;
    last_imu_accel_x_ = imu_accel_x;
    last_gnss_vel_x_ = gnss_vel_x;
}

void PlausibilityChecker::check_battery_power(float voltage, float current, float expected_power_w, std::chrono::milliseconds /*now*/) noexcept {
    const float measured_power = voltage * current;
    const float power_residual = std::abs(measured_power - expected_power_w);

    battery_confidence_.estimated_value = voltage;
    battery_confidence_.residual = power_residual;
    battery_confidence_.variance = (power_residual / 50.0f) * 0.1f + 0.02f;
    battery_confidence_.confidence_bound_95 = 1.96f * std::sqrt(battery_confidence_.variance);

    if (power_residual <= config_.max_power_residual_w * 0.5f) {
        battery_confidence_.status = PlausibilityStatus::Valid;
        battery_confidence_.confidence_score = 0.98f;
    } else if (power_residual <= config_.max_power_residual_w) {
        battery_confidence_.status = PlausibilityStatus::Degraded;
        battery_confidence_.confidence_score = 0.75f;
    } else if (power_residual <= config_.max_power_residual_w * 2.0f) {
        battery_confidence_.status = PlausibilityStatus::Suspect;
        battery_confidence_.confidence_score = 0.40f;
    } else {
        battery_confidence_.status = PlausibilityStatus::Failed;
        battery_confidence_.confidence_score = 0.05f;
    }
}

void PlausibilityChecker::sync_to_rationalizer(AlarmRationalizer& ar, std::chrono::milliseconds now) const noexcept {
    const float min_conf = std::min(nav_velocity_confidence_.confidence_score, battery_confidence_.confidence_score);
    if (config_.diagnostic_alarm_id < ar.size()) {
        ar.update_value(config_.diagnostic_alarm_id, min_conf, now);
    }
}

} // namespace isa18_2
