#include <cstdint>
#include <cmath>
#include <algorithm>
#include <expected>
#include <string_view>

namespace autonomy::docking {

enum class State : uint8_t {
    Idle = 0,
    PowerCheck,
    PreTorque,
    CorridorReverse,
    UnmooringBurst,
    TractionCheck,
    HeadingAlign,
    Complete,
    Abort
};

enum class Error : uint8_t {
    None = 0,
    PowerNotDisconnected,
    BrakeReleaseFailed,
    CorridorJammed,
    ExcessiveSlip,
    Timeout
};

struct Config {
    bool is_marine_vehicle{false};
    float exit_velocity_mps{0.12f};
    float exit_distance_m{1.80f};
    float vehicle_mass_kg{45.0f};
    float wheel_radius_m{0.125f};
    float gear_ratio{15.0f};
    float max_allowed_slip{0.25f};
    float max_motor_current_a{18.0f};
    float unmooring_burst_thrust{0.75f};
    float unmooring_burst_dur_s{1.20f};
    float phase_timeout_s{5.0f};
};

struct Telemetry {
    float charge_current_a{0.0f};
    float dock_voltage_v{0.0f};
    float pitch_angle_rad{0.0f};
    float current_left_a{0.0f};
    float current_right_a{0.0f};
    float encoder_dist_m{0.0f};
    float encoder_vel_mps{0.0f};
    float imu_accel_x_mps2{0.0f};
    float imu_gyro_z_radps{0.0f};
    float gnss_ground_speed_mps{0.0f};
};

struct ActuatorCommands {
    float cmd_vel_linear_mps{0.0f};
    float cmd_vel_angular_radps{0.0f};
    float cmd_motor_torque_nm{0.0f};
    float cmd_thrust_left{0.0f};
    float cmd_thrust_right{0.0f};
    bool brake_release_gpio{false};
};

class DockExitFsm {
public:
    explicit DockExitFsm(Config cfg) : cfg_(cfg) {}

    void start() noexcept {
        if (state_ == State::Idle) {
            state_ = State::PowerCheck;
            error_ = Error::None;
            state_timer_s_ = 0.0f;
            integrated_heading_rad_ = 0.0f;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] Error error() const noexcept { return error_; }
    [[nodiscard]] bool is_finished() const noexcept { return state_ == State::Complete; }
    [[nodiscard]] bool is_faulted() const noexcept { return state_ == State::Abort; }

    ActuatorCommands update(const Telemetry& in, float dt) noexcept {
        state_timer_s_ += dt;
        integrated_heading_rad_ += in.imu_gyro_z_radps * dt;

        ActuatorCommands out{};

        switch (state_) {
            case State::Idle:
                break;

            case State::PowerCheck:
                if (std::abs(in.charge_current_a) < 0.05f && in.dock_voltage_v < 1.5f) {
                    state_ = cfg_.is_marine_vehicle ? State::UnmooringBurst : State::PreTorque;
                    state_timer_s_ = 0.0f;
                } else if (state_timer_s_ > cfg_.phase_timeout_s) {
                    abort(Error::PowerNotDisconnected);
                }
                break;

            case State::PreTorque: {
                constexpr float g = 9.80665f;
                const float slope_torque = (cfg_.vehicle_mass_kg * g * std::sin(in.pitch_angle_rad) * 
                                            cfg_.wheel_radius_m) / (2.0f * cfg_.gear_ratio);
                
                out.cmd_motor_torque_nm = slope_torque;
                if (state_timer_s_ > 0.2f) {
                    out.brake_release_gpio = true;
                }
                if (state_timer_s_ > 0.6f) {
                    state_ = State::CorridorReverse;
                    state_timer_s_ = 0.0f;
                    start_encoder_dist_m_ = in.encoder_dist_m;
                }
                break;
            }

            case State::CorridorReverse: {
                out.brake_release_gpio = true;
                out.cmd_vel_linear_mps = -std::abs(cfg_.exit_velocity_mps);
                out.cmd_vel_angular_radps = 0.0f;

                if (std::abs(in.current_left_a) > cfg_.max_motor_current_a ||
                    std::abs(in.current_right_a) > cfg_.max_motor_current_a) {
                    abort(Error::CorridorJammed);
                    break;
                }

                const float traveled = std::abs(in.encoder_dist_m - start_encoder_dist_m_);
                if (traveled >= cfg_.exit_distance_m) {
                    state_ = State::TractionCheck;
                    state_timer_s_ = 0.0f;
                } else if (state_timer_s_ > cfg_.phase_timeout_s) {
                    abort(Error::Timeout);
                }
                break;
            }

            case State::UnmooringBurst:
                out.cmd_thrust_left = cfg_.unmooring_burst_thrust;
                out.cmd_thrust_right = -cfg_.unmooring_burst_thrust * 0.5f;

                if (state_timer_s_ >= cfg_.unmooring_burst_dur_s) {
                    state_ = State::HeadingAlign;
                    state_timer_s_ = 0.0f;
                }
                break;

            case State::TractionCheck: {
                out.brake_release_gpio = true;
                out.cmd_vel_linear_mps = -cfg_.exit_velocity_mps * 0.5f;

                const float est_speed = std::abs(in.imu_accel_x_mps2 * state_timer_s_);
                const float enc_speed = std::abs(in.encoder_vel_mps);
                const float max_s = std::max(enc_speed, est_speed);

                const float slip_ratio = (max_s > 0.05f) ? (std::abs(enc_speed - est_speed) / max_s) : 0.0f;

                if (slip_ratio > cfg_.max_allowed_slip && state_timer_s_ > 0.5f) {
                    abort(Error::ExcessiveSlip);
                } else if (state_timer_s_ > 1.0f) {
                    state_ = State::HeadingAlign;
                    state_timer_s_ = 0.0f;
                }
                break;
            }

            case State::HeadingAlign:
                out.brake_release_gpio = true;
                out.cmd_vel_angular_radps = -1.5f * integrated_heading_rad_;
                out.cmd_vel_linear_mps = cfg_.exit_velocity_mps;

                if (in.gnss_ground_speed_mps > 0.8f || state_timer_s_ > 3.0f) {
                    state_ = State::Complete;
                }
                break;

            case State::Complete:
                out.brake_release_gpio = true;
                break;

            case State::Abort:
                out.brake_release_gpio = false;
                out.cmd_vel_linear_mps = 0.0f;
                out.cmd_vel_angular_radps = 0.0f;
                break;
        }

        return out;
    }

private:
    void abort(Error err) noexcept {
        state_ = State::Abort;
        error_ = err;
    }

    Config cfg_;
    State state_{State::Idle};
    Error error_{Error::None};
    float state_timer_s_{0.0f};
    float start_encoder_dist_m_{0.0f};
    float integrated_heading_rad_{0.0f};
};

} // namespace autonomy::docking
