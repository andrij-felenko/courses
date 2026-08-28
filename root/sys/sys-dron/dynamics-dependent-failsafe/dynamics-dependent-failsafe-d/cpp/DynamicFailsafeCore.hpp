// DynamicFailsafeCore.hpp
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace drone::control {

enum class FailsafePhase : uint8_t {
    Idle = 0,
    Unroll,       // Фаза 1: гасіння кутових швидкостей та крену
    Pullout,      // Фаза 2: вивід з пікірування з лімітом G
    EnergyClimb,  // Фаза 3: стабілізація енергії та набір висоти
    Handoff       // Фаза 4: готовність до навігаційного RTL
};

struct VehicleState {
    float roll_rad{0.0f};
    float pitch_rad{0.0f};
    float gyro_p{0.0f};
    float gyro_q{0.0f};
    float gyro_r{0.0f};
    float airspeed_m_s{0.0f};
    float accel_z_m_s2{0.0f};
    float altitude_m{0.0f};
    float vz_m_s{0.0f};
};

struct FailsafeConfig {
    float max_nz{2.5f};
    float stall_airspeed{13.0f};
    float cruise_airspeed{22.0f};
    float safe_altitude{60.0f};
    float v_ref_airspeed{20.0f};
};

struct ControlOutput {
    float aileron{0.0f};
    float elevator{0.0f};
    float rudder{0.0f};
    float throttle{0.0f};
    FailsafePhase phase{FailsafePhase::Idle};
    bool ready_for_rtl{false};
};

class DynamicFailsafeController {
public:
    constexpr explicit DynamicFailsafeController(FailsafeConfig cfg) noexcept
        : cfg_(cfg) {}

    void trigger() noexcept {
        if (phase_ == FailsafePhase::Idle) {
            phase_ = FailsafePhase::Unroll;
            nz_integral_ = 0.0f;
        }
    }

    void reset() noexcept {
        phase_ = FailsafePhase::Idle;
        nz_integral_ = 0.0f;
    }

    [[nodiscard]] constexpr FailsafePhase currentPhase() const noexcept {
        return phase_;
    }

    [[nodiscard]] ControlOutput update(const VehicleState& st, float dt) noexcept {
        ControlOutput out{};
        out.phase = phase_;

        if (phase_ == FailsafePhase::Idle) {
            return out;
        }

        const float v_curr = std::max(st.airspeed_m_s, 5.0f);
        const float q_ratio = (cfg_.v_ref_airspeed * cfg_.v_ref_airspeed) / (v_curr * v_curr);
        const float q_scale = std::clamp(q_ratio, 0.25f, 2.50f);

        constexpr float g_const = 9.80665f;
        const float nz_current = 1.0f - (st.accel_z_m_s2 / g_const);

        switch (phase_) {
        case FailsafePhase::Unroll: {
            const float roll_err = -st.roll_rad;
            out.aileron = (roll_err * 1.8f - st.gyro_p * 0.25f) * q_scale;
            out.elevator = (-st.gyro_q * 0.15f) * q_scale;
            out.rudder = (-st.gyro_r * 0.20f) * q_scale;
            out.throttle = (st.airspeed_m_s > cfg_.cruise_airspeed) ? 0.05f : 0.40f;

            if (std::abs(st.roll_rad) < 0.26f && std::abs(st.gyro_p) < 0.35f) {
                phase_ = FailsafePhase::Pullout;
                nz_integral_ = 0.0f;
            }
            break;
        }

        case FailsafePhase::Pullout: {
            out.aileron = (-st.roll_rad) * 1.5f * q_scale;
            out.rudder = (-st.gyro_r * 0.20f) * q_scale;

            const float target_nz = std::min(cfg_.max_nz, 2.5f);
            const float nz_err = target_nz - nz_current;
            nz_integral_ = std::clamp(nz_integral_ + nz_err * dt * 0.5f, -0.2f, 0.4f);

            const float elev_demand = nz_err * 0.35f + nz_integral_ - st.gyro_q * 0.15f;
            out.elevator = elev_demand * q_scale;
            out.throttle = (st.airspeed_m_s > cfg_.cruise_airspeed) ? 0.05f : 0.50f;

            if (st.pitch_rad >= -0.05f && st.vz_m_s >= -0.5f) {
                phase_ = FailsafePhase::EnergyClimb;
            }
            break;
        }

        case FailsafePhase::EnergyClimb: {
            out.aileron = (-st.roll_rad) * 1.2f * q_scale;
            out.rudder = (-st.gyro_r * 0.20f) * q_scale;

            float target_pitch = 0.12f;
            if (st.airspeed_m_s < cfg_.stall_airspeed * 1.3f) {
                target_pitch = 0.02f;
            }

            const float pitch_err = target_pitch - st.pitch_rad;
            out.elevator = (pitch_err * 1.4f - st.gyro_q * 0.20f) * q_scale;
            out.throttle = 0.85f;

            if (st.altitude_m >= cfg_.safe_altitude &&
                st.airspeed_m_s >= cfg_.stall_airspeed * 1.35f) {
                phase_ = FailsafePhase::Handoff;
            }
            break;
        }

        case FailsafePhase::Handoff: {
            out.aileron = (-st.roll_rad) * 1.0f * q_scale;
            out.elevator = (0.03f - st.pitch_rad) * 1.0f * q_scale;
            out.rudder = (-st.gyro_r * 0.20f) * q_scale;
            out.throttle = 0.60f;
            out.ready_for_rtl = true;
            break;
        }

        case FailsafePhase::Idle:
            break;
        }

        out.aileron = std::clamp(out.aileron, -1.0f, 1.0f);
        out.elevator = std::clamp(out.elevator, -1.0f, 1.0f);
        out.rudder = std::clamp(out.rudder, -1.0f, 1.0f);
        out.throttle = std::clamp(out.throttle, 0.0f, 1.0f);

        return out;
    }

private:
    FailsafeConfig cfg_;
    FailsafePhase phase_{FailsafePhase::Idle};
    float nz_integral_{0.0f};
};

} // namespace drone::control
