#include "pi_controller.hpp"

namespace foc {

PiController::PiController(float kp, float ki, float dt, float out_min, float out_max)
    : kp_(kp), ki_(ki), dt_(dt), out_min_(out_min), out_max_(out_max) {}

void PiController::setGains(float kp, float ki) {
    kp_ = kp;
    ki_ = ki;
}

void PiController::setOutputLimits(float out_min, float out_max) {
    out_min_ = out_min;
    out_max_ = out_max;
}

void PiController::reset() {
    integral_ = 0.0f;
    prev_error_ = 0.0f;
}

float PiController::update(float setpoint, float measured) {
    float error = setpoint - measured;

    // Пропорційна складова
    float p_term = kp_ * error;

    // Попередній розрахунок інтегральної складової
    float integral_next = integral_ + ki_ * error * dt_;

    // Необмежений вихідний сигнал
    float output_raw = p_term + integral_next;

    // Обмеження виходу (saturation)
    float output = std::clamp(output_raw, out_min_, out_max_);

    // Механізм Anti-Windup (Conditional Integration):
    // Інтегральна сума оновлюється лише якщо вихідний сигнал не досяг меж насичення
    if (output == output_raw) {
        integral_ = integral_next;
    }

    prev_error_ = error;
    return output;
}

} // namespace foc
