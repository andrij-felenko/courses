#include <iostream>
#include <array>
#include <cmath>
#include <algorithm>
#include <numbers>

class Pt1Filter {
public:
    constexpr Pt1Filter() noexcept = default;

    void init(float cutoff_hz, float dt) noexcept {
        const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz);
        alpha_ = dt / (rc + dt);
        state_ = 0.0f;
    }

    [[nodiscard]] float update(float input) noexcept {
        state_ += alpha_ * (input - state_);
        return state_;
    }

    [[nodiscard]] float state() const noexcept { return state_; }

private:
    float state_{0.0f};
    float alpha_{1.0f};
};

class RatePidController {
public:
    struct Config {
        float kp{0.18f};
        float ki{0.25f};
        float kd{0.004f};
        float k_ff{0.02f};
        float i_max{0.3f};
        float out_max{1.0f};
        float d_cutoff_hz{60.0f};
    };

    RatePidController(const Config& cfg, float dt) noexcept
        : cfg_(cfg), dt_(dt) {
        d_filter_.init(cfg_.d_cutoff_hz, dt_);
    }

    [[nodiscard]] float update(float target_rate, float meas_rate) noexcept {
        const float error = target_rate - meas_rate;

        const float p_out = cfg_.kp * error;
        const float ff_out = cfg_.k_ff * target_rate;

        // D-on-Measurement з фільтрацією PT1
        const float raw_d = -(meas_rate - prev_meas_) / dt_;
        prev_meas_ = meas_rate;
        const float filtered_d = d_filter_.update(raw_d);
        const float d_out = cfg_.kd * filtered_d;

        const float u_no_i = p_out + d_out + ff_out;

        // Anti-Windup Clamping & Conditional Integration
        const float new_i = std::clamp(i_term_ + (cfg_.ki * error * dt_), -cfg_.i_max, cfg_.i_max);
        const float potential_out = u_no_i + new_i;

        const bool saturated = (potential_out > cfg_.out_max && error > 0.0f) ||
                               (potential_out < -cfg_.out_max && error < 0.0f);

        if (!saturated) {
            i_term_ = new_i;
        }

        return std::clamp(u_no_i + i_term_, -cfg_.out_max, cfg_.out_max);
    }

    void reset() noexcept {
        i_term_ = 0.0f;
        prev_meas_ = 0.0f;
    }

private:
    Config cfg_;
    float dt_;
    float i_term_{0.0f};
    float prev_meas_{0.0f};
    Pt1Filter d_filter_;
};

class AnglePidController {
public:
    struct Config {
        float kp{6.5f};
        float max_rate{4.0f};
    };

    explicit constexpr AnglePidController(const Config& cfg) noexcept : cfg_(cfg) {}

    [[nodiscard]] float update(float target_angle, float meas_angle) const noexcept {
        const float error = target_angle - meas_angle;
        return std::clamp(cfg_.kp * error, -cfg_.max_rate, cfg_.max_rate);
    }

private:
    Config cfg_;
};

int main() {
    constexpr float kDtSim = 0.001f;     // Базовий крок 1000 Гц
    constexpr float kSimDuration = 2.0f; // 2 секунди
    constexpr auto kTotalSteps = static_cast<std::size_t>(kSimDuration / kDtSim);

    float angle_rad = 0.0f;
    float rate_rad_s = 0.0f;
    constexpr float kInertia = 0.005f;
    constexpr float kArmLength = 0.15f;
    constexpr float kMotorTau = 0.03f;
    float motor_thrust_diff = 0.0f;

    RatePidController rate_pid(RatePidController::Config{}, kDtSim);
    AnglePidController angle_pid(AnglePidController::Config{});

    constexpr float kTargetAngle = 0.35f; // Ціль 20 градусів
    float target_rate = 0.0f;

    for (std::size_t step = 0; step < kTotalSteps; ++step) {
        const float t = static_cast<float>(step) * kDtSim;

        if (step % 4 == 0) {
            target_rate = angle_pid.update(kTargetAngle, angle_rad);
        }

        const float control_cmd = rate_pid.update(target_rate, rate_rad_s);

        const float target_thrust = control_cmd * 2.0f;
        motor_thrust_diff += (kDtSim / kMotorTau) * (target_thrust - motor_thrust_diff);

        float wind_torque = 0.0f;
        if (t >= 1.0f && t <= 1.3f) {
            wind_torque = 0.08f;
        }

        const float total_torque = (motor_thrust_diff * kArmLength) + wind_torque;
        const float angular_accel = total_torque / kInertia;

        rate_rad_s += angular_accel * kDtSim;
        angle_rad += rate_rad_s * kDtSim;
    }

    return 0;
}
