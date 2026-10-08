#include "cascade_pid.hpp"
#include <cmath>
#include <algorithm>

namespace gimbal {

float CascadePidController::clamp(float value, float min_val, float max_val) {
    return std::max(min_val, std::min(value, max_val));
}

void CascadePidController::configure_notch_filter(float center_freq_hz, float bw_hz, float sample_rate_hz) {
    notch_filter_.configure(center_freq_hz, bw_hz, sample_rate_hz);
}

float CascadePidController::update(float target_angle_rad, float measured_angle_rad, float measured_velocity_rad_s, float dt) {
    if (dt <= 0.0f) {
        return iq_cmd_;
    }

    // 1. ЗОВНІШНІЙ КОНТУР: Регулювання кутового положення
    float angle_error = target_angle_rad - measured_angle_rad;

    // Нормалізація кутової помилки в діапазон [-PI, PI]
    while (angle_error > 3.1415926535f) angle_error -= 6.28318530718f;
    while (angle_error < -3.1415926535f) angle_error += 6.28318530718f;

    // Накопичення інтегратора зовнішнього контуру з обмеженням
    angle_integral_ += angle_error * dt;
    angle_integral_ = clamp(angle_integral_, -angle_gains_.integrator_limit, angle_gains_.integrator_limit);

    // Розрахунок бажаної кутової швидкості (Output of Outer Loop)
    target_velocity_ = (angle_gains_.kp * angle_error) + (angle_gains_.ki * angle_integral_);
    target_velocity_ = clamp(target_velocity_, -angle_gains_.max_output, angle_gains_.max_output);

    // 2. ФІЛЬТРАЦІЯ ЗВОРТНОГО ЗВ'ЯЗКУ ШВИДКОСТІ ЧЕРЕЗ NOTCH FILTER
    // Пригнічення механічного резонансу системи в сигналі гіроскопа
    filtered_velocity_ = notch_filter_.update(measured_velocity_rad_s);

    // 3. ВНУТРІШНІЙ КОНТУР: Регулювання кутової швидкості
    float velocity_error = target_velocity_ - filtered_velocity_;

    // Інтегрування з захистом Anti-windup
    velocity_integral_ += velocity_error * dt;
    velocity_integral_ = clamp(velocity_integral_, -velocity_gains_.integrator_limit, velocity_gains_.integrator_limit);

    // Диференціальна складова за помилкою швидкості
    float velocity_derivative = (dt > 0.0f) ? (velocity_error - last_velocity_error_) / dt : 0.0f;
    last_velocity_error_ = velocity_error;

    // Обчислення вихідної команди моменту / струму Iq
    iq_cmd_ = (velocity_gains_.kp * velocity_error) + 
              (velocity_gains_.ki * velocity_integral_) + 
              (velocity_gains_.kd * velocity_derivative);

    // Обмеження максимального струму / напруги статора
    iq_cmd_ = clamp(iq_cmd_, -velocity_gains_.max_output, velocity_gains_.max_output);

    return iq_cmd_;
}

void CascadePidController::reset() {
    angle_integral_ = 0.0f;
    velocity_integral_ = 0.0f;
    last_velocity_error_ = 0.0f;
    target_velocity_ = 0.0f;
    filtered_velocity_ = 0.0f;
    iq_cmd_ = 0.0f;
    notch_filter_.reset();
}

} // namespace gimbal
