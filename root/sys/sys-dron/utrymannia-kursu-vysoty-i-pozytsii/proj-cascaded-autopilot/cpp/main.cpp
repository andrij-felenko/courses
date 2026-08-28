#include <iostream>
#include <numbers>
#include <cmath>
#include <algorithm>

namespace autopilot {

struct Vector3 {
    float x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] constexpr float length_xy() const noexcept {
        return std::sqrt(x * x + y * y);
    }
};

[[nodiscard]] inline float wrap_pi(float rad) noexcept {
    while (rad > std::numbers::pi_v<float>)  rad -= 2.0f * std::numbers::pi_v<float>;
    while (rad < -std::numbers::pi_v<float>) rad += 2.0f * std::numbers::pi_v<float>;
    return rad;
}

class PidController {
public:
    struct Config {
        float kp{0.0f};
        float ki{0.0f};
        float kd{0.0f};
        float i_max{0.0f};
        float out_min{-1.0f};
        float out_max{1.0f};
    };

    explicit PidController(const Config& cfg) : cfg_(cfg) {}

    [[nodiscard]] float update(float target, float meas, float dt) noexcept {
        const float error = target - meas;
        float deriv = 0.0f;
        if (dt > 1e-6f) {
            deriv = -(meas - prev_meas_) / dt;
        }
        prev_meas_ = meas;

        const float p_term = cfg_.kp * error;
        const float d_term = cfg_.kd * deriv;
        const float out_raw = p_term + cfg_.ki * integ_ + d_term;

        // Clamping anti-windup
        const bool sat_high = (out_raw >= cfg_.out_max && error > 0.0f);
        const bool sat_low  = (out_raw <= cfg_.out_min && error < 0.0f);

        if (!sat_high && !sat_low) {
            integ_ += error * dt;
            integ_ = std::clamp(integ_, -cfg_.i_max, cfg_.i_max);
        }

        const float out = p_term + cfg_.ki * integ_ + d_term;
        return std::clamp(out, cfg_.out_min, cfg_.out_max);
    }

    void reset() noexcept {
        integ_ = 0.0f;
        prev_meas_ = 0.0f;
    }

private:
    Config cfg_;
    float integ_{0.0f};
    float prev_meas_{0.0f};
};

struct AutopilotState {
    Vector3 pos_neu;
    Vector3 vel_neu;
    Vector3 euler_rad;
    Vector3 gyro_rps;
    float v_battery{16.0f};
    float v_nominal{16.0f};
};

struct AutopilotCommands {
    float roll_torque{0.0f};
    float pitch_torque{0.0f};
    float yaw_torque{0.0f};
    float throttle{0.0f};
};

class CascadedFlightController {
public:
    CascadedFlightController()
        : pid_pos_n_({ .kp = 1.0f, .ki = 0.0f, .kd = 0.0f, .i_max = 0.0f, .out_min = -12.0f, .out_max = 12.0f }),
          pid_pos_e_({ .kp = 1.0f, .ki = 0.0f, .kd = 0.0f, .i_max = 0.0f, .out_min = -12.0f, .out_max = 12.0f }),
          pid_pos_z_({ .kp = 1.2f, .ki = 0.0f, .kd = 0.0f, .i_max = 0.0f, .out_min = -3.0f,  .out_max = 4.0f }),
          pid_vel_n_({ .kp = 2.0f, .ki = 0.5f, .kd = 0.1f, .i_max = 5.0f, .out_min = -6.0f,  .out_max = 6.0f }),
          pid_vel_e_({ .kp = 2.0f, .ki = 0.5f, .kd = 0.1f, .i_max = 5.0f, .out_min = -6.0f,  .out_max = 6.0f }),
          pid_vel_z_({ .kp = 2.5f, .ki = 1.2f, .kd = 0.05f, .i_max = 4.0f, .out_min = -8.0f, .out_max = 8.0f }),
          pid_rate_p_({ .kp = 0.15f, .ki = 0.20f, .kd = 0.003f, .i_max = 0.3f, .out_min = -1.0f, .out_max = 1.0f }),
          pid_rate_q_({ .kp = 0.15f, .ki = 0.20f, .kd = 0.003f, .i_max = 0.3f, .out_min = -1.0f, .out_max = 1.0f }),
          pid_rate_r_({ .kp = 0.22f, .ki = 0.12f, .kd = 0.000f, .i_max = 0.3f, .out_min = -1.0f, .out_max = 1.0f }) {}

    void set_targets(const Vector3& target_pos, float target_yaw_rad) noexcept {
        target_pos_ = target_pos;
        target_yaw_rad_ = target_yaw_rad;
    }

    void update_slow_loop(const AutopilotState& state, float dt) noexcept {
        constexpr float kGravity = 9.80665f;

        // 1. Позиція -> Швидкість
        float des_vn = pid_pos_n_.update(target_pos_.x, state.pos_neu.x, dt);
        float des_ve = pid_pos_e_.update(target_pos_.y, state.pos_neu.y, dt);
        float des_vz = pid_pos_z_.update(target_pos_.z, state.pos_neu.z, dt);

        const float horiz_spd = std::sqrt(des_vn * des_vn + des_ve * des_ve);
        if (horiz_spd > max_horiz_vel_ && horiz_spd > 1e-4f) {
            const float scale = max_horiz_vel_ / horiz_spd;
            des_vn *= scale;
            des_ve *= scale;
        }
        des_vel_ = { des_vn, des_ve, des_vz };

        // 2. Швидкість -> Прискорення
        const float a_n = pid_vel_n_.update(des_vel_.x, state.vel_neu.x, dt);
        const float a_e = pid_vel_e_.update(des_vel_.y, state.vel_neu.y, dt);
        const float a_z = pid_vel_z_.update(des_vel_.z, state.vel_neu.z, dt);

        // 3. Проекція прискорень на курс корпусу
        const float psi = state.euler_rad.z;
        const float cos_psi = std::cos(psi);
        const float sin_psi = std::sin(psi);

        const float a_fwd   =  a_n * cos_psi + a_e * sin_psi;
        const float a_right = -a_n * sin_psi + a_e * cos_psi;

        // 4. Прискорення -> Кути нахилу
        const float target_pitch = std::clamp(std::atan2(a_fwd, kGravity), -max_tilt_angle_, max_tilt_angle_);
        const float target_roll  = std::clamp(std::atan2(a_right, kGravity), -max_tilt_angle_, max_tilt_angle_);

        des_euler_ = { target_roll, target_pitch, target_yaw_rad_ };

        // 5. Вертикальний канал тяги
        const float cos_tilt = std::max(0.35f, std::cos(state.euler_rad.x) * std::cos(state.euler_rad.y));
        const float thr_accel_offset = (a_z / kGravity) * thr_hover_;
        float raw_thr = (thr_hover_ + thr_accel_offset) / cos_tilt;

        if (state.v_battery > 6.0f) {
            raw_thr *= (state.v_nominal / state.v_battery);
        }
        base_throttle_ = std::clamp(raw_thr, 0.08f, 0.95f);
    }

    [[nodiscard]] AutopilotCommands update_fast_loop(const AutopilotState& state, float dt) noexcept {
        // 1. Орієнтація (P) -> Кутові швидкості
        const float err_roll  = des_euler_.x - state.euler_rad.x;
        const float err_pitch = des_euler_.y - state.euler_rad.y;
        const float err_yaw   = wrap_pi(des_euler_.z - state.euler_rad.z);

        const Vector3 des_rates{
            std::clamp(kp_roll_angle_  * err_roll,  -4.0f, 4.0f),
            std::clamp(kp_pitch_angle_ * err_pitch, -4.0f, 4.0f),
            std::clamp(kp_yaw_angle_   * err_yaw,   -2.5f, 2.5f)
        };

        // 2. Кутові швидкості (PID) -> Моменти
        return AutopilotCommands{
            .roll_torque  = pid_rate_p_.update(des_rates.x, state.gyro_rps.x, dt),
            .pitch_torque = pid_rate_q_.update(des_rates.y, state.gyro_rps.y, dt),
            .yaw_torque   = pid_rate_r_.update(des_rates.z, state.gyro_rps.z, dt),
            .throttle     = base_throttle_
        };
    }

    [[nodiscard]] const Vector3& desired_velocity() const noexcept { return des_vel_; }
    [[nodiscard]] const Vector3& desired_euler() const noexcept { return des_euler_; }

private:
    Vector3 target_pos_{};
    float target_yaw_rad_{0.0f};

    Vector3 des_vel_{};
    Vector3 des_euler_{};
    float base_throttle_{0.45f};

    PidController pid_pos_n_, pid_pos_e_, pid_pos_z_;
    PidController pid_vel_n_, pid_vel_e_, pid_vel_z_;
    PidController pid_rate_p_, pid_rate_q_, pid_rate_r_;

    float kp_roll_angle_{6.5f};
    float kp_pitch_angle_{6.5f};
    float kp_yaw_angle_{3.5f};

    float max_horiz_vel_{12.0f};
    float max_tilt_angle_{35.0f * std::numbers::pi_v<float> / 180.0f};
    float thr_hover_{0.45f};
};

} // namespace autopilot

int main() {
    using namespace autopilot;

    CascadedFlightController controller;
    controller.set_targets(Vector3{ 10.0f, 5.0f, 25.0f }, 90.0f * std::numbers::pi_v<float> / 180.0f);

    AutopilotState state{
        .pos_neu   = { 0.0f, 0.0f, 20.0f },
        .vel_neu   = { 0.0f, 0.0f, 0.0f },
        .euler_rad = { 0.0f, 0.0f, 0.0f },
        .gyro_rps  = { 0.0f, 0.0f, 0.0f },
        .v_battery = 16.0f,
        .v_nominal = 16.0f
    };

    controller.update_slow_loop(state, 0.02f);
    const auto cmd = controller.update_fast_loop(state, 0.002f);

    std::cout << "C++ автопілот успішно розрахував такт керування.\n";
    std::cout << "Тяга: " << cmd.throttle
              << ", Моменти: [" << cmd.roll_torque
              << ", " << cmd.pitch_torque
              << ", " << cmd.yaw_torque << "]\n";

    return 0;
}
