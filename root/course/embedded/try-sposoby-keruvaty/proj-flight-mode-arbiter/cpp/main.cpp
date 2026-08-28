#include <chrono>
#include <algorithm>
#include <cmath>
#include <optional>

namespace FlightStack {

using namespace std::chrono_literals;

enum class ControlMode : uint8_t {
    DirectManual = 0, // 1. Acro / Rate
    AssistedAngle,    // 2. Fly-by-Wire / Stabilize
    SupervisoryAuto,  // 3. Waypoint / Offboard
    FailsafeLand      // Аварійна деградація
};

struct VehicleState {
    float roll_deg{0.0f};
    float pitch_deg{0.0f};
    float yaw_deg{0.0f};
    float rate_roll_deg_s{0.0f};
    float rate_pitch_deg_s{0.0f};
    float rate_yaw_deg_s{0.0f};
};

struct ControlSetpoint {
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
    float throttle{0.0f};
};

class ModeArbiter {
public:
    static constexpr float kMaxRateDegS    = 360.0f;
    static constexpr float kMaxAngleDeg   = 45.0f;
    static constexpr float kSlewRateDegS  = 180.0f;
    static constexpr auto kRcTimeout      = 500ms;
    static constexpr auto kOffboardTimeout = 1000ms;

    explicit ModeArbiter() = default;

    bool requestMode(ControlMode new_mode, const VehicleState& state) noexcept {
        if (current_mode_ == new_mode) {
            return true;
        }

        // Безударний перехід: занулення розриву уставки
        if (new_mode == ControlMode::DirectManual) {
            active_setpoint_.roll  = state.rate_roll_deg_s;
            active_setpoint_.pitch = state.rate_pitch_deg_s;
            active_setpoint_.yaw   = state.rate_yaw_deg_s;
        } else if (new_mode == ControlMode::AssistedAngle || 
                   new_mode == ControlMode::SupervisoryAuto) {
            active_setpoint_.roll  = std::clamp(state.roll_deg, -kMaxAngleDeg, kMaxAngleDeg);
            active_setpoint_.pitch = std::clamp(state.pitch_deg, -kMaxAngleDeg, kMaxAngleDeg);
            active_setpoint_.yaw   = state.yaw_deg;
        }

        current_mode_ = new_mode;
        return true;
    }

    void notifyRcPacket(std::chrono::milliseconds now) noexcept {
        last_rc_time_ = now;
    }

    void notifyOffboardPacket(std::chrono::milliseconds now) noexcept {
        last_offboard_time_ = now;
    }

    void update(const VehicleState& state,
                const ControlSetpoint& rc_sp,
                const ControlSetpoint& offboard_sp,
                std::chrono::milliseconds now,
                float dt_sec) noexcept {
        // 1. Перевірка тайм-аутів зв'язку
        const bool rc_valid = (now - last_rc_time_) <= kRcTimeout;
        const bool offboard_valid = (now - last_offboard_time_) <= kOffboardTimeout;

        // 2. Логіка деградації режимів
        if (current_mode_ == ControlMode::SupervisoryAuto && !offboard_valid) {
            if (rc_valid) {
                requestMode(ControlMode::AssistedAngle, state);
            } else {
                requestMode(ControlMode::FailsafeLand, state);
            }
        } else if ((current_mode_ == ControlMode::AssistedAngle || 
                    current_mode_ == ControlMode::DirectManual) && !rc_valid) {
            requestMode(ControlMode::FailsafeLand, state);
        }

        // 3. Формування цільової уставки
        ControlSetpoint target{};
        switch (current_mode_) {
            case ControlMode::DirectManual:
                target.roll     = rc_sp.roll * kMaxRateDegS;
                target.pitch    = rc_sp.pitch * kMaxRateDegS;
                target.yaw      = rc_sp.yaw * kMaxRateDegS;
                target.throttle = rc_sp.throttle;
                break;

            case ControlMode::AssistedAngle:
                target.roll     = rc_sp.roll * kMaxAngleDeg;
                target.pitch    = rc_sp.pitch * kMaxAngleDeg;
                target.yaw      = rc_sp.yaw * kMaxRateDegS;
                target.throttle = rc_sp.throttle;
                break;

            case ControlMode::SupervisoryAuto:
                target.roll     = std::clamp(offboard_sp.roll, -kMaxAngleDeg, kMaxAngleDeg);
                target.pitch    = std::clamp(offboard_sp.pitch, -kMaxAngleDeg, kMaxAngleDeg);
                target.yaw      = offboard_sp.yaw;
                target.throttle = offboard_sp.throttle;
                break;

            case ControlMode::FailsafeLand:
                target.roll     = 0.0f;
                target.pitch    = 0.0f;
                target.yaw      = state.yaw_deg;
                target.throttle = 0.40f; // Контрольована швидкість спуску
                break;
        }

        // 4. Плавний фільтр наростання уставки (Slew-rate limiting)
        const float max_delta = kSlewRateDegS * dt_sec;
        active_setpoint_.roll     = applySlewRate(active_setpoint_.roll, target.roll, max_delta);
        active_setpoint_.pitch    = applySlewRate(active_setpoint_.pitch, target.pitch, max_delta);
        active_setpoint_.yaw      = applySlewRate(active_setpoint_.yaw, target.yaw, max_delta);
        active_setpoint_.throttle = target.throttle;
    }

    [[nodiscard]] ControlMode currentMode() const noexcept { return current_mode_; }
    [[nodiscard]] const ControlSetpoint& activeSetpoint() const noexcept { return active_setpoint_; }

private:
    static float applySlewRate(float current, float target, float max_delta) noexcept {
        const float error = target - current;
        if (std::abs(error) <= max_delta) {
            return target;
        }
        return current + (error > 0.0f ? max_delta : -max_delta);
    }

    ControlMode current_mode_{ControlMode::AssistedAngle};
    ControlSetpoint active_setpoint_{};
    std::chrono::milliseconds last_rc_time_{0};
    std::chrono::milliseconds last_offboard_time_{0};
};

} // namespace FlightStack
