#include <array>
#include <cmath>
#include <algorithm>
#include <numbers>

// ── 1. Двоквардатний режекторний фільтр (C++20 Biquad Notch) ───────────────
class BiquadFilter {
public:
    constexpr BiquadFilter() noexcept = default;

    void init_notch(float center_hz, float cutoff_hz, float dt) noexcept {
        const float omega = 2.0f * std::numbers::pi_v<float> * center_hz * dt;
        float octaves = std::log2(center_hz / cutoff_hz) * 2.0f;
        if (octaves < 0.1f) octaves = 0.1f;
        const float alpha = std::sin(omega) * std::sinh(std::log(2.0f) / 2.0f * octaves * omega / std::sin(omega));

        const float b0 = 1.0f;
        const float b1 = -2.0f * std::cos(omega);
        const float b2 = 1.0f;
        const float a0 = 1.0f + alpha;
        const float a1 = -2.0f * std::cos(omega);
        const float a2 = 1.0f - alpha;

        b0_ = b0 / a0;
        b1_ = b1 / a0;
        b2_ = b2 / a0;
        a1_ = a1 / a0;
        a2_ = a2 / a0;
        x1_ = x2_ = y1_ = y2_ = 0.0f;
    }

    [[nodiscard]] float update(float in) noexcept {
        const float out = (b0_ * in) + (b1_ * x1_) + (b2_ * x2_) - (a1_ * y1_) - (a2_ * y2_);
        x2_ = x1_;
        x1_ = in;
        y2_ = y1_;
        y1_ = out;
        return out;
    }

private:
    float b0_{1.0f}, b1_{0.0f}, b2_{0.0f};
    float a1_{0.0f}, a2_{0.0f};
    float x1_{0.0f}, x2_{0.0f};
    float y1_{0.0f}, y2_{0.0f};
};

// ── 2. ПІД-контролер осі з Anti-Windup та D-on-Measurement ──────────────────
class AxisPidController {
public:
    struct Parameters {
        float kp{0.20f};
        float ki{0.30f};
        float kd{0.005f};
        float k_ff{0.025f};
        float i_max{0.35f};
        float out_max{1.0f};
        float notch_center_hz{200.0f};
    };

    AxisPidController(const Parameters& params, float dt) noexcept
        : params_(params), dt_(dt) {
        d_filter_.init_notch(params_.notch_center_hz, params_.notch_center_hz * 0.7f, dt_);
    }

    [[nodiscard]] float update(float target_rate, float meas_rate) noexcept {
        const float error = target_rate - meas_rate;

        // P-ланка
        const float p_out = params_.kp * error;

        // Прямий зв'язок Feedforward
        const float d_setpoint = (target_rate - prev_setpoint_) / dt_;
        prev_setpoint_ = target_rate;
        const float ff_out = params_.k_ff * d_setpoint;

        // D-on-Measurement
        const float raw_d = -(meas_rate - prev_meas_) / dt_;
        prev_meas_ = meas_rate;
        const float filtered_d = d_filter_.update(raw_d);
        const float d_out = params_.kd * filtered_d;

        const float u_fast = p_out + d_out + ff_out;

        // Conditional Integration Anti-Windup
        const float potential_i = std::clamp(i_term_ + (params_.ki * error * dt_),
                                             -params_.i_max, params_.i_max);
        const float potential_total = u_fast + potential_i;

        const bool saturated = (potential_total > params_.out_max && error > 0.0f) ||
                               (potential_total < -params_.out_max && error < 0.0f);

        if (!saturated) {
            i_term_ = potential_i;
        }

        return std::clamp(u_fast + i_term_, -params_.out_max, params_.out_max);
    }

    void reset() noexcept {
        i_term_ = 0.0f;
        prev_meas_ = 0.0f;
        prev_setpoint_ = 0.0f;
    }

private:
    Parameters params_;
    float dt_;
    float i_term_{0.0f};
    float prev_meas_{0.0f};
    float prev_setpoint_{0.0f};
    BiquadFilter d_filter_;
};

// ── 3. Матриця мікшування Quad-X (C++20) ───────────────────────────────────
class QuadcopterMixer {
public:
    using MotorArray = std::array<float, 4>;

    [[nodiscard]] static MotorArray mix_quad_x(float throttle, float roll, float pitch, float yaw) noexcept {
        MotorArray motors{
            throttle - roll + pitch + yaw, // M1 Rear-Right (CW)
            throttle - roll - pitch - yaw, // M2 Front-Right (CCW)
            throttle + roll + pitch - yaw, // M3 Rear-Left (CCW)
            throttle + roll - pitch + yaw  // M4 Front-Left (CW)
        };

        // Air Mode: динамічний зсув діапазону для захисту керованості
        auto [min_it, max_it] = std::minmax_element(motors.begin(), motors.end());
        float min_val = *min_it;
        float max_val = *max_it;

        if (min_val < 0.0f) {
            const float shift_up = -min_val;
            for (auto& m : motors) m += shift_up;
            max_val += shift_up;
        }

        if (max_val > 1.0f) {
            const float shift_down = max_val - 1.0f;
            for (auto& m : motors) m -= shift_down;
        }

        for (auto& m : motors) {
            m = std::clamp(m, 0.0f, 1.0f);
        }

        return motors;
    }
};
