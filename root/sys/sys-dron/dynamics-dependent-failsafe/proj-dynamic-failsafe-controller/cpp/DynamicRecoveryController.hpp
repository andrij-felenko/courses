// DynamicRecoveryController.hpp
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <numbers>

namespace drone::safety {

enum class RecoveryState : uint8_t {
    Idle = 0,
    RateDamping,   // Фаза 0: демпфування високих кутових швидкостей
    Unroll,        // Фаза 1: вирівнювання крену (Roll-First)
    GPullout,      // Фаза 2: вивід з пікірування з лімітом nz
    EnergyClimb,   // Фаза 3: стабілізація швидкості та набір безпечної висоти
    Handoff        // Фаза 4: завершення, передача в штатний RTL
};

struct KinematicState {
    float q_w{1.0f};
    float q_x{0.0f};
    float q_y{0.0f};
    float q_z{0.0f};
    float gyro_p{0.0f};          // [рад/с]
    float gyro_q{0.0f};          // [рад/с]
    float gyro_r{0.0f};          // [рад/с]
    float accel_x{0.0f};         // [м/с²]
    float accel_y{0.0f};         // [м/с²]
    float accel_z{-9.80665f};    // [м/с²]
    float airspeed_ias{20.0f};   // [м/с]
    float altitude{0.0f};        // [м]
    float climb_rate{0.0f};      // [м/с]
};

struct RecoveryConfig {
    float max_nz{2.5f};
    float stall_speed{13.0f};
    float cruise_speed{22.0f};
    float vne_speed{45.0f};
    float safe_altitude{50.0f};
    float v_ref_tuning{20.0f};
};

struct ActuatorCommands {
    float aileron{0.0f};
    float elevator{0.0f};
    float rudder{0.0f};
    float throttle{0.0f};
    RecoveryState state{RecoveryState::Idle};
    bool ready_for_navigation{false};
};

class DynamicRecoveryController {
public:
    constexpr explicit DynamicRecoveryController(RecoveryConfig cfg) noexcept
        : cfg_(cfg) {}

    void trigger() noexcept {
        if (state_ == RecoveryState::Idle) {
            state_ = RecoveryState::RateDamping;
            nz_integrator_ = 0.0f;
            state_timer_ = 0.0f;
        }
    }

    void reset() noexcept {
        state_ = RecoveryState::Idle;
        nz_integrator_ = 0.0f;
        state_timer_ = 0.0f;
    }

    [[nodiscard]] constexpr RecoveryState currentState() const noexcept {
        return state_;
    }

    [[nodiscard]] ActuatorCommands update(const KinematicState& st, float dt) noexcept {
        ActuatorCommands cmd{};
        cmd.state = state_;

        if (state_ == RecoveryState::Idle) {
            return cmd;
        }

        state_timer_ += dt;

        // 1. Оцінка кутів Ейлера безпосередньо з кватерніона
        const auto [roll, pitch, yaw] = quaternionToEuler(st.q_w, st.q_x, st.q_y, st.q_z);

        // 2. Q-Scheduling: масштабування коефіцієнтів
        const float v_safe = std::max(st.airspeed_ias, 6.0f);
        const float q_ratio = (cfg_.v_ref_tuning * cfg_.v_ref_tuning) / (v_safe * v_safe);
        const float q_scale = std::clamp(q_ratio, 0.25f, 2.50f);

        // 3. Нормальне перевантаження nz
        constexpr float g_const = 9.80665f;
        const float nz_current = 1.0f - (st.accel_z / g_const);

        switch (state_) {
        case RecoveryState::RateDamping: {
            cmd.aileron = (-st.gyro_p * 0.35f) * q_scale;
            cmd.elevator = (-st.gyro_q * 0.25f) * q_scale;
            cmd.rudder = (-st.gyro_r * 0.30f) * q_scale;
            cmd.throttle = (st.airspeed_ias > cfg_.cruise_speed) ? 0.05f : 0.35f;

            const bool rates_damped = std::abs(st.gyro_p) < 0.60f &&
                                      std::abs(st.gyro_q) < 0.60f &&
                                      std::abs(st.gyro_r) < 0.60f;

            if (rates_damped || state_timer_ > 0.6f) {
                state_ = RecoveryState::Unroll;
                state_timer_ = 0.0f;
            }
            break;
        }

        case RecoveryState::Unroll: {
            const float roll_error = 0.0f - roll;
            cmd.aileron = (roll_error * 1.70f - st.gyro_p * 0.22f) * q_scale;
            cmd.elevator = (-st.gyro_q * 0.15f) * q_scale;
            cmd.rudder = (-st.gyro_r * 0.25f) * q_scale;
            cmd.throttle = (st.airspeed_ias > cfg_.cruise_speed) ? 0.05f : 0.40f;

            if (std::abs(roll) < 0.26f && std::abs(st.gyro_p) < 0.30f) {
                state_ = RecoveryState::GPullout;
                state_timer_ = 0.0f;
                nz_integrator_ = 0.0f;
            }
            break;
        }

        case RecoveryState::GPullout: {
            cmd.aileron = (0.0f - roll) * 1.30f * q_scale;
            cmd.rudder = (-st.gyro_r * 0.20f) * q_scale;

            const float target_nz = std::min(cfg_.max_nz, 2.5f);
            const float nz_err = target_nz - nz_current;
            nz_integrator_ = std::clamp(nz_integrator_ + nz_err * dt * 0.45f, -0.25f, 0.45f);

            const float elev_demand = nz_err * 0.32f + nz_integrator_ - st.gyro_q * 0.18f;
            cmd.elevator = elev_demand * q_scale;
            cmd.throttle = (st.airspeed_ias > cfg_.cruise_speed) ? 0.0f : 0.50f;

            if (pitch >= -0.05f && st.climb_rate >= -0.5f) {
                state_ = RecoveryState::EnergyClimb;
                state_timer_ = 0.0f;
            }
            break;
        }

        case RecoveryState::EnergyClimb: {
            cmd.aileron = (0.0f - roll) * 1.10f * q_scale;
            cmd.rudder = (-st.gyro_r * 0.20f) * q_scale;

            float target_pitch = 0.12f; // ~7 градусів набору
            if (st.airspeed_ias < cfg_.stall_speed * 1.30f) {
                target_pitch = 0.02f;   // Знижуємо набір для розгону
            }

            const float pitch_err = target_pitch - pitch;
            cmd.elevator = (pitch_err * 1.35f - st.gyro_q * 0.20f) * q_scale;
            cmd.throttle = 0.85f;

            if (st.altitude >= cfg_.safe_altitude &&
                st.airspeed_ias >= cfg_.stall_speed * 1.35f) {
                state_ = RecoveryState::Handoff;
                state_timer_ = 0.0f;
            }
            break;
        }

        case RecoveryState::Handoff: {
            cmd.aileron = (0.0f - roll) * 1.0f * q_scale;
            cmd.elevator = (0.03f - pitch) * 1.0f * q_scale;
            cmd.rudder = (-st.gyro_r * 0.20f) * q_scale;
            cmd.throttle = 0.60f;
            cmd.ready_for_navigation = true;
            break;
        }

        case RecoveryState::Idle:
            break;
        }

        cmd.aileron = std::clamp(cmd.aileron, -1.0f, 1.0f);
        cmd.elevator = std::clamp(cmd.elevator, -1.0f, 1.0f);
        cmd.rudder = std::clamp(cmd.rudder, -1.0f, 1.0f);
        cmd.throttle = std::clamp(cmd.throttle, 0.0f, 1.0f);

        return cmd;
    }

private:
    struct EulerAngles { float roll{0.0f}; float pitch{0.0f}; float yaw{0.0f}; };

    [[nodiscard]] static EulerAngles quaternionToEuler(float qw, float qx, float qy, float qz) noexcept {
        EulerAngles ea{};
        const float sinr_cosp = 2.0f * (qw * qx + qy * qz);
        const float cosr_cosp = 1.0f - 2.0f * (qx * qx + qy * qy);
        ea.roll = std::atan2(sinr_cosp, cosr_cosp);

        const float sinp = 2.0f * (qw * qy - qz * qx);
        if (std::abs(sinp) >= 1.0f) {
            ea.pitch = std::copysign(1.57079632679f, sinp);
        } else {
            ea.pitch = std::asin(sinp);
        }

        const float siny_cosp = 2.0f * (qw * qz + qx * qy);
        const float cosy_cosp = 1.0f - 2.0f * (qy * qy + qz * qz);
        ea.yaw = std::atan2(siny_cosp, cosy_cosp);

        return ea;
    }

    RecoveryConfig cfg_;
    RecoveryState state_{RecoveryState::Idle};
    float nz_integrator_{0.0f};
    float state_timer_{0.0f};
};

} // namespace drone::safety
