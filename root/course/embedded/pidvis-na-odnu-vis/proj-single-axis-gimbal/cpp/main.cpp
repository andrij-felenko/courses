/* ============================================================================
 * GimbalController.hpp
 * Модуль одноосьового гіропідвісу на ідіоматичному C++20
 * ============================================================================ */

#include <cstdint>
#include <cmath>
#include <span>
#include <algorithm>
#include <numbers>

namespace gimbal {

inline constexpr float DT_SEC        = 0.005f;   // 200 Гц такт
inline constexpr float SERVO_MIN_US  = 1000.0f;
inline constexpr float SERVO_MID_US  = 1500.0f;
inline constexpr float SERVO_MAX_US  = 2000.0f;
inline constexpr float MAX_ANGLE_DEG = 45.0f;
inline constexpr float MAX_BIAS_VAR  = 0.25f;    // (°/с)² поріг спокою

class ComplementaryFilter {
public:
    explicit constexpr ComplementaryFilter(float alpha = 0.98f) noexcept
        : alpha_{alpha}, angle_deg_{0.0f} {}

    [[nodiscard]] float update(float raw_gyro_dps, float gyro_bias_dps,
                               float ay, float az, float dt) noexcept {
        const float rate_dps = raw_gyro_dps - gyro_bias_dps;
        const float pred_angle = angle_deg_ + rate_dps * dt;

        // Кут за акселерометром
        const float acc_angle_deg = std::atan2(ay, az) *
                                   (180.0f / std::numbers::pi_v<float>);

        angle_deg_ = alpha_ * pred_angle + (1.0f - alpha_) * acc_angle_deg;
        return angle_deg_;
    }

    [[nodiscard]] constexpr float angle() const noexcept { return angle_deg_; }
    void reset(float initial_angle = 0.0f) noexcept { angle_deg_ = initial_angle; }

private:
    float alpha_;
    float angle_deg_;
};

class PidController {
public:
    struct Config {
        float kp{1.8f};
        float ki{0.6f};
        float kd{0.08f};
        float out_min{-MAX_ANGLE_DEG};
        float out_max{MAX_ANGLE_DEG};
        float d_cutoff_hz{25.0f};
    };

    explicit PidController(const Config& cfg) noexcept
        : cfg_{cfg} {
        if (cfg_.d_cutoff_hz > 0.0f) {
            const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cfg_.d_cutoff_hz);
            d_lpf_alpha_ = DT_SEC / (DT_SEC + rc);
        } else {
            d_lpf_alpha_ = 1.0f;
        }
    }

    [[nodiscard]] float update(float setpoint_deg, float current_angle_deg,
                               float measured_rate_dps, float dt) noexcept {
        const float error = setpoint_deg - current_angle_deg;
        const float p_term = cfg_.kp * error;

        // Derivative on Measurement + ФНЧ
        const float d_raw = -measured_rate_dps;
        d_lpf_state_ += d_lpf_alpha_ * (d_raw - d_lpf_state_);
        const float d_term = cfg_.kd * d_lpf_state_;

        // Попередній вихід для перевірки насичення
        const float u_tentative = p_term + integrator_ + d_term;
        const bool is_saturated = (u_tentative > cfg_.out_max || u_tentative < cfg_.out_min);
        const bool same_direction = (u_tentative * error > 0.0f);

        // Clamping Anti-Windup
        if (!is_saturated || !same_direction) {
            integrator_ += cfg_.ki * error * dt;
        }

        const float u_out = p_term + integrator_ + d_term;
        return std::clamp(u_out, cfg_.out_min, cfg_.out_max);
    }

    void reset() noexcept {
        integrator_ = 0.0f;
        d_lpf_state_ = 0.0f;
    }

private:
    Config cfg_;
    float  integrator_{0.0f};
    float  d_lpf_state_{0.0f};
    float  d_lpf_alpha_{1.0f};
};

class Stabilizer {
public:
    Stabilizer(float filter_alpha, const PidController::Config& pid_cfg) noexcept
        : filter_{filter_alpha}, pid_{pid_cfg} {}

    [[nodiscard]] bool calibrate_gyro(std::span<const float> static_samples) noexcept {
        if (static_samples.size() < 10) return false;

        float sum = 0.0f;
        for (float val : static_samples) {
            sum += val;
        }
        const float mean = sum / static_cast<float>(static_samples.size());

        float var_sum = 0.0f;
        for (float val : static_samples) {
            const float diff = val - mean;
            var_sum += diff * diff;
        }
        const float variance = var_sum / static_cast<float>(static_samples.size() - 1);

        if (variance > MAX_BIAS_VAR) {
            is_calibrated_ = false;
            return false;
        }

        gyro_bias_dps_ = mean;
        is_calibrated_ = true;
        return true;
    }

    [[nodiscard]] uint16_t process_step(float raw_gyro_dps, float ay, float az) noexcept {
        const float current_angle = filter_.update(raw_gyro_dps, gyro_bias_dps_,
                                                  ay, az, DT_SEC);
        const float rate_dps = raw_gyro_dps - gyro_bias_dps_;

        // Бажаний кут — горизонталь (0°)
        const float correction_deg = pid_.update(0.0f, current_angle, rate_dps, DT_SEC);

        return map_servo_pulse(correction_deg);
    }

    [[nodiscard]] static constexpr uint16_t map_servo_pulse(float angle_deg) noexcept {
        constexpr float us_per_deg = (SERVO_MAX_US - SERVO_MIN_US) / (2.0f * MAX_ANGLE_DEG);
        const float pulse = SERVO_MID_US + angle_deg * us_per_deg;
        const float clamped = std::clamp(pulse, SERVO_MIN_US, SERVO_MAX_US);
        return static_cast<uint16_t>(clamped + 0.5f);
    }

    [[nodiscard]] float estimated_angle() const noexcept { return filter_.angle(); }
    [[nodiscard]] bool is_calibrated() const noexcept { return is_calibrated_; }

private:
    ComplementaryFilter filter_;
    PidController       pid_;
    float               gyro_bias_dps_{0.0f};
    bool                is_calibrated_{false};
};

} // namespace gimbal
