// servo_controller.hpp — Ідіоматична C++ реалізація прецизійного серворегулятора
#pragma once
#include <cmath>
#include <algorithm>
#include <numbers>

namespace servo {

struct Limits {
    float max_velocity{15.0f};       // рад/с
    float max_acceleration{50.0f};   // рад/с²
    float max_current{5.0f};         // Ампери
    float max_voltage{24.0f};        // Вольти
};

struct Gains {
    float kp_pos{35.0f};             // 1/с
    float kp_vel{0.45f};             // А/(рад/с)
    float ki_vel{4.50f};             // А/рад
    float kp_curr{2.80f};            // В/А
    float ki_curr{120.0f};           // В/(А·с)
};

struct DynamicsModel {
    float vel_filter_cutoff{100.0f}; // Гц
    float inertia_j{0.0015f};        // кг·м²
    float torque_const_kt{0.085f};   // Н·м/А
    float friction_coulomb{0.025f};  // Н·м
    float friction_viscous{0.0012f}; // Н·м/(рад/с)
    float friction_stiction{0.040f}; // Н·м
    float gravity_mass_arm{0.150f};  // Н·м
};

struct DeadbandParams {
    float enter_rad{0.0015f};        // ~0.08° (поріг входу в фіксацію)
    float exit_rad{0.0040f};         // ~0.23° (поріг виходу)
    float still_vel_rad_s{0.010f};   // поріг повної зупинки
};

struct Config {
    Limits         limits{};
    Gains          gains{};
    DynamicsModel  model{};
    DeadbandParams deadband{};
};

class PositionServo {
public:
    explicit PositionServo(Config config, float initial_pos = 0.0f) noexcept
        : cfg_{config},
          target_pos_{initial_pos},
          profile_pos_{initial_pos},
          prev_meas_pos_{initial_pos} {}

    void set_target(float new_target) noexcept {
        target_pos_ = new_target;
        profile_active_ = true;
        in_position_ = false;
    }

    [[nodiscard]] float update(float meas_pos, float meas_curr, float dt) noexcept {
        update_profile(dt);

        const float raw_vel = (meas_pos - prev_meas_pos_) / dt;
        prev_meas_pos_ = meas_pos;

        // IIR-фільтрація виміряної швидкості
        const float tau = 1.0f / (2.0f * std::numbers::pi_v<float> * cfg_.model.vel_filter_cutoff);
        const float alpha = dt / (tau + dt);
        filtered_vel_ += alpha * (raw_vel - filtered_vel_);
        const float meas_vel = filtered_vel_;

        update_deadband_state(meas_pos, meas_vel);

        const float vel_cmd = compute_position_loop(meas_pos, meas_vel);
        const float curr_cmd = compute_velocity_loop(vel_cmd, meas_vel, meas_pos, dt);
        const float volt_cmd = compute_current_loop(curr_cmd, meas_curr, dt);

        cmd_velocity_ = vel_cmd;
        cmd_current_ = curr_cmd;
        cmd_voltage_ = volt_cmd;

        return volt_cmd;
    }

    [[nodiscard]] bool is_in_position() const noexcept { return in_position_; }
    [[nodiscard]] float target_position() const noexcept { return target_pos_; }
    [[nodiscard]] float profile_position() const noexcept { return profile_pos_; }
    [[nodiscard]] float filtered_velocity() const noexcept { return filtered_vel_; }
    [[nodiscard]] float command_voltage() const noexcept { return cmd_voltage_; }

private:
    static constexpr float sgn(float val) noexcept {
        if (val > 1e-4f) return 1.0f;
        if (val < -1e-4f) return -1.0f;
        return 0.0f;
    }

    void update_profile(float dt) noexcept {
        if (!profile_active_) {
            profile_vel_ = 0.0f;
            profile_acc_ = 0.0f;
            return;
        }

        const float pos_err = target_pos_ - profile_pos_;
        const float dist = std::abs(pos_err);
        const float dir = sgn(pos_err);

        if (dist < 1e-5f && std::abs(profile_vel_) < 1e-4f) {
            profile_pos_ = target_pos_;
            profile_vel_ = 0.0f;
            profile_acc_ = 0.0f;
            profile_active_ = false;
            return;
        }

        const float stop_dist = (profile_vel_ * profile_vel_) / (2.0f * cfg_.limits.max_acceleration);

        if (dist <= stop_dist) {
            profile_acc_ = -dir * cfg_.limits.max_acceleration;
        } else {
            if (std::abs(profile_vel_) < cfg_.limits.max_velocity) {
                profile_acc_ = dir * cfg_.limits.max_acceleration;
            } else {
                profile_acc_ = 0.0f;
            }
        }

        profile_vel_ += profile_acc_ * dt;
        profile_vel_ = std::clamp(profile_vel_, -cfg_.limits.max_velocity, cfg_.limits.max_velocity);
        profile_pos_ += profile_vel_ * dt;
    }

    void update_deadband_state(float meas_pos, float meas_vel) noexcept {
        const float abs_err = std::abs(target_pos_ - meas_pos);
        const float abs_vel = std::abs(meas_vel);

        if (!in_position_) {
            if (!profile_active_ && abs_err <= cfg_.deadband.enter_rad && abs_vel <= cfg_.deadband.still_vel_rad_s) {
                in_position_ = true;
            }
        } else {
            if (abs_err > cfg_.deadband.exit_rad) {
                in_position_ = false;
            }
        }
    }

    [[nodiscard]] float compute_position_loop(float meas_pos, float meas_vel) const noexcept {
        if (in_position_) {
            return -0.1f * meas_vel; // Активне демпфування спокою
        }
        const float pos_err = profile_pos_ - meas_pos;
        const float p_term = cfg_.gains.kp_pos * pos_err;
        const float feedforward = profile_vel_; // Швидкісне випередження
        return std::clamp(p_term + feedforward, -cfg_.limits.max_velocity, cfg_.limits.max_velocity);
    }

    [[nodiscard]] float compute_velocity_loop(float vel_cmd, float meas_vel, float meas_pos, float dt) noexcept {
        const float vel_err = vel_cmd - meas_vel;
        const float p_term = cfg_.gains.kp_vel * vel_err;

        if (!in_position_) {
            integral_vel_ += (cfg_.gains.ki_vel * vel_err) * dt;
            integral_vel_ = std::clamp(integral_vel_, -cfg_.limits.max_current, cfg_.limits.max_current);
        }

        // Прискорювальне випередження інерції J · α*
        const float accel_ff = (cfg_.model.inertia_j * profile_acc_) / cfg_.model.torque_const_kt;

        // Випередження тертя (Stiction + Coulomb + Viscous)
        float fric_torque = (sgn(vel_cmd) * cfg_.model.friction_coulomb) + (cfg_.model.friction_viscous * vel_cmd);
        if (std::abs(meas_vel) < cfg_.deadband.still_vel_rad_s && std::abs(vel_cmd) > 1e-3f) {
            fric_torque += sgn(vel_cmd) * cfg_.model.friction_stiction;
        }
        const float fric_ff = fric_torque / cfg_.model.torque_const_kt;

        // Випередження сили тяжіння
        const float grav_torque = cfg_.model.gravity_mass_arm * std::cos(meas_pos);
        const float grav_ff = grav_torque / cfg_.model.torque_const_kt;

        const float total_curr = p_term + integral_vel_ + accel_ff + fric_ff + grav_ff;
        return std::clamp(total_curr, -cfg_.limits.max_current, cfg_.limits.max_current);
    }

    [[nodiscard]] float compute_current_loop(float curr_cmd, float meas_curr, float dt) noexcept {
        const float curr_err = curr_cmd - meas_curr;
        const float p_term = cfg_.gains.kp_curr * curr_err;

        integral_curr_ += (cfg_.gains.ki_curr * curr_err) * dt;
        integral_curr_ = std::clamp(integral_curr_, -cfg_.limits.max_voltage, cfg_.limits.max_voltage);

        return std::clamp(p_term + integral_curr_, -cfg_.limits.max_voltage, cfg_.limits.max_voltage);
    }

    Config cfg_{};

    float target_pos_{0.0f};
    float profile_pos_{0.0f};
    float profile_vel_{0.0f};
    float profile_acc_{0.0f};
    bool  profile_active_{false};

    float filtered_vel_{0.0f};
    float integral_vel_{0.0f};
    float integral_curr_{0.0f};
    float prev_meas_pos_{0.0f};

    bool  in_position_{true};

    float cmd_voltage_{0.0f};
    float cmd_current_{0.0f};
    float cmd_velocity_{0.0f};
};

} // namespace servo
