#include "HallGimbal.hpp"
#include <algorithm>

HallGimbal::HallGimbal(const GimbalConfig& config)
    : config_(config),
      filtered_x_(static_cast<float>(config.axis_x.center_raw)),
      filtered_y_(static_cast<float>(config.axis_y.center_raw)) {}

void HallGimbal::calibrateCenter(uint16_t raw_x, uint16_t raw_y) {
    config_.axis_x.center_raw = raw_x;
    config_.axis_y.center_raw = raw_y;
    filtered_x_ = static_cast<float>(raw_x);
    filtered_y_ = static_cast<float>(raw_y);
}

float HallGimbal::normalizeAxis(float raw_val, const AxisCalibration& calib) const noexcept {
    if (raw_val < static_cast<float>(calib.center_raw)) {
        float span = static_cast<float>(calib.center_raw - calib.min_raw);
        if (span <= 0.0f) return -1.0f;
        float val = (raw_val - static_cast<float>(calib.center_raw)) / span;
        return std::clamp(val, -1.0f, 0.0f);
    } else {
        float span = static_cast<float>(calib.max_raw - calib.center_raw);
        if (span <= 0.0f) return 1.0f;
        float val = (raw_val - static_cast<float>(calib.center_raw)) / span;
        return std::clamp(val, 0.0f, 1.0f);
    }
}

GimbalPosition HallGimbal::update(uint16_t raw_x, uint16_t raw_y) {
    // 1. Апаратний контроль виходу за межі (обрив лінії сенсора Холла або зсув магніту)
    constexpr uint16_t safety_margin = 50;
    bool x_out_of_bounds = (raw_x < (config_.axis_x.min_raw > safety_margin ? config_.axis_x.min_raw - safety_margin : 0)) ||
                           (raw_x > config_.axis_x.max_raw + safety_margin);
    bool y_out_of_bounds = (raw_y < (config_.axis_y.min_raw > safety_margin ? config_.axis_y.min_raw - safety_margin : 0)) ||
                           (raw_y > config_.axis_y.max_raw + safety_margin);

    if (x_out_of_bounds || y_out_of_bounds) {
        current_pos_ = {0.0f, 0.0f, false};
        return current_pos_;
    }

    // 2. Експоненційне згладжування EMA (Exponential Moving Average)
    if (is_first_update_) {
        filtered_x_ = static_cast<float>(raw_x);
        filtered_y_ = static_cast<float>(raw_y);
        is_first_update_ = false;
    } else {
        float alpha = config_.alpha_ema;
        filtered_x_ = alpha * static_cast<float>(raw_x) + (1.0f - alpha) * filtered_x_;
        filtered_y_ = alpha * static_cast<float>(raw_y) + (1.0f - alpha) * filtered_y_;
    }

    // 3. Нормалізація в незалежний діапазон [-1.0, +1.0]
    float norm_x = normalizeAxis(filtered_x_, config_.axis_x);
    float norm_y = normalizeAxis(filtered_y_, config_.axis_y);

    // 4. Обчислення векторного радіуса r = sqrt(x^2 + y^2) та застосування радіальної deadzone
    float radius = std::hypot(norm_x, norm_y);
    float dz = config_.deadzone_radial;

    if (radius <= dz) {
        current_pos_ = {0.0f, 0.0f, true};
    } else {
        // Ресштабування вектора після мертвої зони від 0.0 до 1.0 для збереження лінійності
        float scaled_radius = std::min(1.0f, (radius - dz) / (1.0f - dz));
        float dir_x = norm_x / radius;
        float dir_y = norm_y / radius;

        current_pos_ = {dir_x * scaled_radius, dir_y * scaled_radius, true};
    }

    return current_pos_;
}
