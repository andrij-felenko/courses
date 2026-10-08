#include <cstdint>
#include <algorithm>

class PIDThermostat {
private:
    float kp_;
    float ki_;
    float kd_;
    float prev_error_{0.0f};
    float integral_{0.0f};

public:
    PIDThermostat(float kp, float ki, float kd) : kp_(kp), ki_(ki), kd_(kd) {}

    std::uint16_t computePWM(float setpoint, float current_temp, float dt, float v_src, float p_max, float r_tip) {
        float error = setpoint - current_temp;
        integral_ += error * dt;
        float derivative = (error - prev_error_) / dt;
        prev_error_ = error;

        float output = (kp_ * error) + (ki_ * integral_) + (kd_ * derivative);

        float p_peak = (v_src * v_src) / r_tip;
        float max_duty = std::min(1.0f, p_max / p_peak);

        output = std::clamp(output, 0.0f, max_duty);

        return static_cast<std::uint16_t>(output * 4095.0f);
    }
};
