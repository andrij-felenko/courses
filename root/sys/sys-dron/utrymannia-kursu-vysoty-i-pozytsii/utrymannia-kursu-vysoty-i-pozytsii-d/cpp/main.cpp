#include <cmath>
#include <algorithm>
#include <numbers>

namespace autopilot {

constexpr float kGravity = 9.80665f;
constexpr float kMaxTiltRad = 0.6108f; // 35 градусів

struct Vector3 {
    float x{0.0f}, y{0.0f}, z{0.0f};
};

[[nodiscard]] constexpr float wrap_pi(float rad) noexcept {
    while (rad > std::numbers::pi_v<float>)  rad -= 2.0f * std::numbers::pi_v<float>;
    while (rad < -std::numbers::pi_v<float>) rad += 2.0f * std::numbers::pi_v<float>;
    return rad;
}

class Pid {
public:
    struct Config {
        float kp{0.0f}, ki{0.0f}, kd{0.0f};
        float i_max{0.0f};
        float out_min{-1.0f}, out_max{1.0f};
    };

    explicit Pid(const Config& cfg) : cfg_(cfg) {}

    [[nodiscard]] float update(float target, float meas, float dt) noexcept {
        const float err = target - meas;
        const float deriv = (dt > 1e-5f) ? -(meas - prev_meas_) / dt : 0.0f;
        prev_meas_ = meas;

        const float p_term = cfg_.kp * err;
        const float d_term = cfg_.kd * deriv;
        const float unsat = p_term + cfg_.ki * integ_ + d_term;

        if (!((unsat >= cfg_.out_max && err > 0.0f) || (unsat <= cfg_.out_min && err < 0.0f))) {
            integ_ = std::clamp(integ_ + err * dt, -cfg_.i_max, cfg_.i_max);
        }
        return std::clamp(p_term + cfg_.ki * integ_ + d_term, cfg_.out_min, cfg_.out_max);
    }

    void reset() noexcept { integ_ = 0.0f; prev_meas_ = 0.0f; }

private:
    Config cfg_;
    float integ_{0.0f};
    float prev_meas_{0.0f};
};

struct FlightState {
    Vector3 pos_neu;
    Vector3 vel_neu;
    Vector3 euler_rad;
    Vector3 gyro_rps;
    float v_battery{16.0f};
    float v_nominal{16.0f};
};

struct ActuatorCommands {
    Vector3 torques;
    float throttle{0.0f};
};

class CascadedController {
public:
    CascadedController()
        : p_pos_n_({ .kp = 1.0f, .out_min = -12.0f, .out_max = 12.0f }),
          p_pos_e_({ .kp = 1.0f, .out_min = -12.0f, .out_max = 12.0f }),
          p_pos_z_({ .kp = 1.2f, .out_min = -3.0f,  .out_max = 4.0f }),
          p_vel_n_({ .kp = 2.0f, .ki = 0.5f, .kd = 0.1f, .i_max = 5.0f, .out_min = -6.0f, .out_max = 6.0f }),
          p_vel_e_({ .kp = 2.0f, .ki = 0.5f, .kd = 0.1f, .i_max = 5.0f, .out_min = -6.0f, .out_max = 6.0f }),
          p_vel_z_({ .kp = 2.5f, .ki = 1.2f, .kd = 0.05f, .i_max = 4.0f, .out_min = -8.0f, .out_max = 8.0f }),
          p_rate_p_({ .kp = 0.15f, .ki = 0.2f, .kd = 0.003f, .i_max = 0.3f }),
          p_rate_q_({ .kp = 0.15f, .ki = 0.2f, .kd = 0.003f, .i_max = 0.3f }),
          p_rate_r_({ .kp = 0.22f, .ki = 0.12f, .kd = 0.0f,  .i_max = 0.3f }) {}

    void update_position_loop(const Vector3& target_pos, float target_yaw,
                              const FlightState& st, float dt) noexcept {
        // 1. Позиція -> Швидкість
        const float vn_des = p_pos_n_.update(target_pos.x, st.pos_neu.x, dt);
        const float ve_des = p_pos_e_.update(target_pos.y, st.pos_neu.y, dt);
        const float vz_des = p_pos_z_.update(target_pos.z, st.pos_neu.z, dt);

        // 2. Швидкість -> Прискорення
        const float an_des = p_vel_n_.update(vn_des, st.vel_neu.x, dt);
        const float ae_des = p_vel_e_.update(ve_des, st.vel_neu.y, dt);
        const float az_des = p_vel_z_.update(vz_des, st.vel_neu.z, dt);

        // 3. Проекція прискорень на курс
        const float psi = st.euler_rad.z;
        const float a_fwd =  an_des * std::cos(psi) + ae_des * std::sin(psi);
        const float a_rgt = -an_des * std::sin(psi) + ae_des * std::cos(psi);

        // 4. Бажані кути крену й тангажу
        target_euler_.x = std::clamp(std::atan2(a_rgt, kGravity), -kMaxTiltRad, kMaxTiltRad);
        target_euler_.y = std::clamp(std::atan2(a_fwd, kGravity), -kMaxTiltRad, kMaxTiltRad);
        target_euler_.z = target_yaw;

        // 5. Тяга з компенсацією нахилу та напруги
        const float cos_tilt = std::max(0.35f, std::cos(st.euler_rad.x) * std::cos(st.euler_rad.y));
        float raw_thr = (thr_hover_ + (az_des / kGravity) * thr_hover_) / cos_tilt;
        if (st.v_battery > 5.0f) raw_thr *= (st.v_nominal / st.v_battery);
        throttle_ = std::clamp(raw_thr, 0.05f, 0.95f);
    }

    [[nodiscard]] ActuatorCommands update_attitude_loop(const FlightState& st, float dt) noexcept {
        const float e_roll  = target_euler_.x - st.euler_rad.x;
        const float e_pitch = target_euler_.y - st.euler_rad.y;
        const float e_yaw   = wrap_pi(target_euler_.z - st.euler_rad.z);

        const float p_des = std::clamp(kp_roll_angle_  * e_roll,  -4.0f, 4.0f);
        const float q_des = std::clamp(kp_pitch_angle_ * e_pitch, -4.0f, 4.0f);
        const float r_des = std::clamp(kp_yaw_angle_   * e_yaw,   -2.5f, 2.5f);

        return ActuatorCommands{
            .torques = {
                p_rate_p_.update(p_des, st.gyro_rps.x, dt),
                p_rate_q_.update(q_des, st.gyro_rps.y, dt),
                p_rate_r_.update(r_des, st.gyro_rps.z, dt)
            },
            .throttle = throttle_
        };
    }

private:
    Vector3 target_euler_{};
    float throttle_{0.45f};
    float thr_hover_{0.45f};

    float kp_roll_angle_{6.5f};
    float kp_pitch_angle_{6.5f};
    float kp_yaw_angle_{3.5f};

    Pid p_pos_n_, p_pos_e_, p_pos_z_;
    Pid p_vel_n_, p_vel_e_, p_vel_z_;
    Pid p_rate_p_, p_rate_q_, p_rate_r_;
};

} // namespace autopilot
