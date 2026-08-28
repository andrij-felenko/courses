#include <cstdint>
#include <cmath>
#include <numbers>
#include <array>
#include <algorithm>

namespace gimbal {

constexpr float PI = std::numbers::pi_v<float>;
constexpr float TWO_PI = 2.0f * PI;
constexpr float SQRT3 = 1.73205080757f;

struct Vec3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct SvpwmDuty {
    float duty_a{0.5f};
    float duty_b{0.5f};
    float duty_c{0.5f};
    uint8_t sector{0};
};

class BiquadNotchFilter {
public:
    void init(float center_freq_hz, float q_factor, float sample_rate_hz) noexcept {
        const float omega = 2.0f * PI * center_freq_hz / sample_rate_hz;
        const float sn = std::sin(omega);
        const float cs = std::cos(omega);
        const float alpha = sn / (2.0f * q_factor);

        const float a0 = 1.0f + alpha;
        b0_ = 1.0f / a0;
        b1_ = (-2.0f * cs) / a0;
        b2_ = 1.0f / a0;
        a1_ = (-2.0f * cs) / a0;
        a2_ = (1.0f - alpha) / a0;

        reset();
    }

    float update(float in) noexcept {
        const float out = b0_ * in + b1_ * x1_ + b2_ * x2_ - a1_ * y1_ - a2_ * y2_;
        x2_ = x1_;
        x1_ = in;
        y2_ = y1_;
        y1_ = out;
        return out;
    }

    void reset() noexcept {
        x1_ = x2_ = y1_ = y2_ = 0.0f;
    }

private:
    float b0_{1.0f}, b1_{0.0f}, b2_{0.0f};
    float a1_{0.0f}, a2_{0.0f};
    float x1_{0.0f}, x2_{0.0f};
    float y1_{0.0f}, y2_{0.0f};
};

class PidController {
public:
    PidController(float kp, float ki, float kd, float out_max, float i_max, float d_alpha = 0.8f)
        : kp_(kp), ki_(ki), kd_(kd), out_max_(out_max), i_max_(i_max), d_alpha_(d_alpha) {}

    float update(float target, float current, float dt) noexcept {
        float error = target - current;
        
        float p_term = kp_ * error;
        
        // Anti-windup clamping
        integral_ += error * dt;
        integral_ = std::clamp(integral_, -i_max_, i_max_);
        float i_term = ki_ * integral_;
        
        // Диференціювання з ФНЧ
        float safe_dt = (dt > 1e-6f) ? dt : 1e-6f;
        float raw_d = (error - prev_error_) / safe_dt;
        prev_error_ = error;
        prev_d_filtered_ = d_alpha_ * prev_d_filtered_ + (1.0f - d_alpha_) * raw_d;
        float d_term = kd_ * prev_d_filtered_;
        
        float output = p_term + i_term + d_term;
        return std::clamp(output, -out_max_, out_max_);
    }

    void reset() noexcept {
        integral_ = 0.0f;
        prev_error_ = 0.0f;
        prev_d_filtered_ = 0.0f;
    }

private:
    float kp_;
    float ki_;
    float kd_;
    float integral_{0.0f};
    float prev_error_{0.0f};
    float out_max_;
    float i_max_;
    float d_alpha_;
    float prev_d_filtered_{0.0f};
};

class FocDriver {
public:
    static SvpwmDuty generate_svpwm(float u_alpha, float u_beta, float v_bus) noexcept {
        SvpwmDuty out;
        if (v_bus <= 0.01f) return out;

        const float u_a_norm = u_alpha / v_bus;
        const float u_b_norm = u_beta / v_bus;

        const float v1 = u_b_norm;
        const float v2 = (SQRT3 * u_a_norm - u_b_norm) * 0.5f;
        const float v3 = (-SQRT3 * u_a_norm - u_b_norm) * 0.5f;

        uint8_t sector_mask = 0;
        if (v1 > 0.0f) sector_mask |= 1;
        if (v2 > 0.0f) sector_mask |= 2;
        if (v3 > 0.0f) sector_mask |= 4;

        float t1 = 0.0f, t2 = 0.0f;

        switch (sector_mask) {
            case 3:
                t1 = SQRT3 * u_a_norm - u_b_norm;
                t2 = 2.0f * u_b_norm;
                out.sector = 1;
                break;
            case 1:
                t1 = SQRT3 * u_a_norm + u_b_norm;
                t2 = -SQRT3 * u_a_norm + u_b_norm;
                out.sector = 2;
                break;
            case 5:
                t1 = 2.0f * u_b_norm;
                t2 = -SQRT3 * u_a_norm - u_b_norm;
                out.sector = 3;
                break;
            case 4:
                t1 = -SQRT3 * u_a_norm + u_b_norm;
                t2 = -2.0f * u_b_norm;
                out.sector = 4;
                break;
            case 6:
                t1 = -SQRT3 * u_a_norm - u_b_norm;
                t2 = SQRT3 * u_a_norm - u_b_norm;
                out.sector = 5;
                break;
            case 2:
                t1 = -2.0f * u_b_norm;
                t2 = SQRT3 * u_a_norm + u_b_norm;
                out.sector = 6;
                break;
            default:
                out.sector = 0;
                return out;
        }

        const float t_sum = t1 + t2;
        if (t_sum > 1.0f) {
            t1 /= t_sum;
            t2 /= t_sum;
        }

        const float t0 = 1.0f - t1 - t2;
        const float t_half0 = t0 * 0.5f;

        switch (out.sector) {
            case 1:
                out.duty_a = t1 + t2 + t_half0;
                out.duty_b = t2 + t_half0;
                out.duty_c = t_half0;
                break;
            case 2:
                out.duty_a = t1 + t_half0;
                out.duty_b = t1 + t2 + t_half0;
                out.duty_c = t_half0;
                break;
            case 3:
                out.duty_a = t_half0;
                out.duty_b = t1 + t2 + t_half0;
                out.duty_c = t2 + t_half0;
                break;
            case 4:
                out.duty_a = t_half0;
                out.duty_b = t1 + t_half0;
                out.duty_c = t1 + t2 + t_half0;
                break;
            case 5:
                out.duty_a = t2 + t_half0;
                out.duty_b = t_half0;
                out.duty_c = t1 + t2 + t_half0;
                break;
            case 6:
                out.duty_a = t1 + t2 + t_half0;
                out.duty_b = t_half0;
                out.duty_c = t1 + t_half0;
                break;
            default:
                break;
        }
        return out;
    }
};

} // namespace gimbal
