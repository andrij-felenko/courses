#include <cmath>
#include <algorithm>
#include <cstdint>

namespace autonomy {

enum class DockStage : uint8_t {
    Idle = 0,
    CheckPower,
    PreTorque,
    ReverseCorridor,
    UnmooringBurst,
    TractionValidate,
    HeadingAlign,
    Success,
    AbortFault
};

struct VehicleParams {
    bool is_marine{false};
    float mass_kg{45.0f};
    float wheel_radius_m{0.125f};
    float gear_ratio{15.0f};
    float target_exit_dist_m{1.8f};
    float exit_velocity_mps{0.12f};
    float max_motor_current_a{20.0f};
};

struct SensorReadings {
    float charge_current_a{0.0f};
    float pitch_rad{0.0f};
    float encoder_dist_m{0.0f};
    float current_left_a{0.0f};
    float current_right_a{0.0f};
    float gnss_speed_mps{0.0f};
};

struct ControlCommands {
    float linear_vel_mps{0.0f};
    float angular_vel_radps{0.0f};
    float pre_torque_nm{0.0f};
    bool brake_release{false};
};

class DockExitController {
public:
    explicit DockExitController(VehicleParams params) : params_(params) {}

    void trigger_launch() noexcept {
        if (stage_ == DockStage::Idle) {
            stage_ = DockStage::CheckPower;
            timer_s_ = 0.0f;
        }
    }

    [[nodiscard]] DockStage stage() const noexcept { return stage_; }
    [[nodiscard]] bool is_active() const noexcept {
        return stage_ != DockStage::Idle && stage_ != DockStage::Success && stage_ != DockStage::AbortFault;
    }

    ControlCommands step(const SensorReadings& sensors, float dt) noexcept {
        timer_s_ += dt;
        ControlCommands cmd{};

        switch (stage_) {
            case DockStage::Idle:
                break;

            case DockStage::CheckPower:
                if (std::abs(sensors.charge_current_a) < 0.05f) {
                    stage_ = params_.is_marine ? DockStage::UnmooringBurst : DockStage::PreTorque;
                    timer_s_ = 0.0f;
                } else if (timer_s_ > 3.0f) {
                    stage_ = DockStage::AbortFault;
                }
                break;

            case DockStage::PreTorque: {
                constexpr float g = 9.80665f;
                const float m_hold = (params_.mass_kg * g * std::sin(sensors.pitch_rad) * params_.wheel_radius_m) / 
                                     (2.0f * params_.gear_ratio);
                cmd.pre_torque_nm = m_hold;

                if (timer_s_ > 0.2f) {
                    cmd.brake_release = true;
                }
                if (timer_s_ > 0.6f) {
                    stage_ = DockStage::ReverseCorridor;
                    timer_s_ = 0.0f;
                    start_encoder_dist_m_ = sensors.encoder_dist_m;
                }
                break;
            }

            case DockStage::ReverseCorridor: {
                cmd.brake_release = true;
                cmd.linear_vel_mps = -std::abs(params_.exit_velocity_mps);
                cmd.angular_vel_radps = 0.0f;

                if (std::abs(sensors.current_left_a) > params_.max_motor_current_a ||
                    std::abs(sensors.current_right_a) > params_.max_motor_current_a) {
                    stage_ = DockStage::AbortFault;
                    break;
                }

                const float traveled = std::abs(sensors.encoder_dist_m - start_encoder_dist_m_);
                if (traveled >= params_.target_exit_dist_m) {
                    stage_ = DockStage::TractionValidate;
                    timer_s_ = 0.0f;
                } else if (timer_s_ > 15.0f) {
                    stage_ = DockStage::AbortFault;
                }
                break;
            }

            case DockStage::UnmooringBurst:
                cmd.angular_vel_radps = 0.45f;
                cmd.linear_vel_mps = -0.30f;
                if (timer_s_ > 1.2f) {
                    stage_ = DockStage::HeadingAlign;
                    timer_s_ = 0.0f;
                }
                break;

            case DockStage::TractionValidate:
                cmd.brake_release = true;
                cmd.linear_vel_mps = -params_.exit_velocity_mps * 0.5f;
                if (timer_s_ > 1.0f) {
                    stage_ = DockStage::HeadingAlign;
                    timer_s_ = 0.0f;
                }
                break;

            case DockStage::HeadingAlign:
                cmd.brake_release = true;
                cmd.linear_vel_mps = params_.exit_velocity_mps;
                if (sensors.gnss_speed_mps > 0.8f || timer_s_ > 4.0f) {
                    stage_ = DockStage::Success;
                }
                break;

            case DockStage::Success:
                cmd.brake_release = true;
                break;

            case DockStage::AbortFault:
                cmd.brake_release = false;
                cmd.linear_vel_mps = 0.0f;
                cmd.angular_vel_radps = 0.0f;
                break;
        }

        return cmd;
    }

private:
    VehicleParams params_;
    DockStage stage_{DockStage::Idle};
    float timer_s_{0.0f};
    float start_encoder_dist_m_{0.0f};
};

} // namespace autonomy
