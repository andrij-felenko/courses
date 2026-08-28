#include <cstdint>
#include <cmath>
#include <numbers>
#include <algorithm>

namespace gimbal {

struct GimbalConfig {
    uint8_t pole_pairs{11};
    float zero_offset_rad{0.0f};
    float v_bus{12.0f};
    float u_limit{6.0f};
    float notch_freq_hz{220.0f};
    float notch_q{2.5f};
};

class AxisController {
public:
    AxisController(const GimbalConfig& cfg, 
                   const PidController& pos_pid, 
                   const PidController& rate_pid,
                   float sample_rate_hz = 1000.0f)
        : config_(cfg), pos_pid_(pos_pid), rate_pid_(rate_pid) {
        notch_.init(config_.notch_freq_hz, config_.notch_q, sample_rate_hz);
    }

    void update_feedback(float raw_mech_angle, float gyro_rate_rad_s) noexcept {
        mech_angle_rad_ = raw_mech_angle;
        gyro_rate_rad_s_ = gyro_rate_rad_s;
        
        float elec = (static_cast<float>(config_.pole_pairs) * raw_mech_angle) - config_.zero_offset_rad;
        float a = std::fmod(elec, 2.0f * std::numbers::pi_v<float>);
        elec_angle_rad_ = (a >= 0.0f) ? a : (a + 2.0f * std::numbers::pi_v<float>);
    }

    void update_cascade(float target_angle, float current_estimated_angle, float feedforward_v, float dt) noexcept {
        float error_angle = target_angle - current_estimated_angle;
        constexpr float PI = std::numbers::pi_v<float>;
        constexpr float TWO_PI = 2.0f * PI;
        while (error_angle > PI)  error_angle -= TWO_PI;
        while (error_angle < -PI) error_angle += TWO_PI;

        float des_rate = pos_pid_.update(target_angle, current_estimated_angle, dt);

        float filtered_gyro = notch_.update(gyro_rate_rad_s_);
        float u_q_cmd = rate_pid_.update(des_rate, filtered_gyro, dt) + feedforward_v;
        
        u_q_ = std::clamp(u_q_cmd, -config_.u_limit, config_.u_limit);
        u_d_ = 0.0f;

        const float s_e = std::sin(elec_angle_rad_);
        const float c_e = std::cos(elec_angle_rad_);

        const float u_alpha = -u_q_ * s_e + u_d_ * c_e;
        const float u_beta  =  u_q_ * c_e + u_d_ * s_e;

        svpwm_ = FocDriver::generate_svpwm(u_alpha, u_beta, config_.v_bus);
    }

    [[nodiscard]] const SvpwmDuty& get_duty() const noexcept { return svpwm_; }
    [[nodiscard]] float get_mech_angle() const noexcept { return mech_angle_rad_; }

private:
    GimbalConfig config_;
    PidController pos_pid_;
    PidController rate_pid_;
    BiquadNotchFilter notch_;
    
    float mech_angle_rad_{0.0f};
    float elec_angle_rad_{0.0f};
    float gyro_rate_rad_s_{0.0f};
    
    float u_d_{0.0f};
    float u_q_{0.0f};
    SvpwmDuty svpwm_{};
};

class TriaxialGimbalSystem {
public:
    TriaxialGimbalSystem(AxisController yaw, AxisController roll, AxisController pitch, float pitch_gravity_ff = 0.8f)
        : yaw_(yaw), roll_(roll), pitch_(pitch), pitch_gravity_ff_(pitch_gravity_ff) {}

    void process(const Vec3& targets, const Vec3& estimated_attitude, const Vec3& gyro_rates, float dt) {
        float pitch_ff = pitch_gravity_ff_ * std::cos(estimated_attitude.y);
        
        yaw_.update_cascade(targets.z, estimated_attitude.z, 0.0f, dt);
        roll_.update_cascade(targets.x, estimated_attitude.x, 0.0f, dt);
        pitch_.update_cascade(targets.y, estimated_attitude.y, pitch_ff, dt);
    }

    [[nodiscard]] const AxisController& yaw() const noexcept { return yaw_; }
    [[nodiscard]] const AxisController& roll() const noexcept { return roll_; }
    [[nodiscard]] const AxisController& pitch() const noexcept { return pitch_; }

    AxisController& yaw() noexcept { return yaw_; }
    AxisController& roll() noexcept { return roll_; }
    AxisController& pitch() noexcept { return pitch_; }

private:
    AxisController yaw_;
    AxisController roll_;
    AxisController pitch_;
    float pitch_gravity_ff_{0.8f};
};

} // namespace gimbal
