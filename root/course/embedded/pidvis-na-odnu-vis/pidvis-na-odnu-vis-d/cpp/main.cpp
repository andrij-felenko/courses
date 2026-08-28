// ============================================================================
// GimbalCore.hpp — Ядро одноосьової стабілізації на C++20
// ============================================================================

#include <cmath>
#include <algorithm>
#include <numbers>

namespace gimbal {

inline constexpr float DT = 0.005f; // 200 Гц

class ComplementaryFilter {
public:
    explicit constexpr ComplementaryFilter(float alpha = 0.99f) noexcept
        : alpha_{alpha}, angle_deg_{0.0f} {}

    [[nodiscard]] float update(float gyro_rate_dps, float ay, float az) noexcept {
        const float pred = angle_deg_ + gyro_rate_dps * DT;
        const float acc_angle = std::atan2(ay, az) * (180.0f / std::numbers::pi_v<float>);
        angle_deg_ = alpha_ * pred + (1.0f - alpha_) * acc_angle;
        return angle_deg_;
    }

    [[nodiscard]] constexpr float angle() const noexcept { return angle_deg_; }

private:
    float alpha_;
    float angle_deg_;
};

class PidController {
public:
    struct Config {
        float kp{2.0f};
        float ki{0.5f};
        float kd{0.06f};
        float out_min{-45.0f};
        float out_max{45.0f};
        float d_lpf_beta{0.44f};
    };

    explicit constexpr PidController(const Config& cfg) noexcept : cfg_{cfg} {}

    [[nodiscard]] float update(float setpoint, float measured_angle, float gyro_rate_dps) noexcept {
        const float error = setpoint - measured_angle;
        const float p_term = cfg_.kp * error;

        // D-терм за вимірюванням гіроскопа + ФНЧ
        const float d_raw = -gyro_rate_dps;
        d_filter_state_ += cfg_.d_lpf_beta * (d_raw - d_filter_state_);
        const float d_term = cfg_.kd * d_filter_state_;

        const float u_tentative = p_term + integrator_ + d_term;
        const bool saturated = (u_tentative > cfg_.out_max || u_tentative < cfg_.out_min);
        const bool same_direction = (u_tentative * error > 0.0f);

        if (!saturated || !same_direction) {
            integrator_ += cfg_.ki * error * DT;
        }

        const float u_out = p_term + integrator_ + d_term;
        return std::clamp(u_out, cfg_.out_min, cfg_.out_max);
    }

private:
    Config cfg_;
    float integrator_{0.0f};
    float d_filter_state_{0.0f};
};

} // namespace gimbal
