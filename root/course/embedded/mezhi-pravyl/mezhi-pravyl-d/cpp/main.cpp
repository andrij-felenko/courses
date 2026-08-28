#include <cmath>
#include <algorithm>
#include <expected>

namespace Control {

struct Setpoint {
    float vx{0.0f};       // м/с
    float yaw_rate{0.0f}; // рад/с
};

struct ObstacleEnvelope {
    float range_ahead_m{0.0f};
    float max_brake_accel_mps2{3.0f};
    float safety_margin_m{0.4f};
};

enum class BarrierStatus {
    PassThrough,
    SpeedClamped,
    EmergencyHalt
};

class SafetyBarrier {
public:
    [[nodiscard]] static constexpr std::pair<Setpoint, BarrierStatus> enforce(
        const Setpoint& candidate,
        const ObstacleEnvelope& env
    ) noexcept {
        if (candidate.vx <= 0.0f) {
            return {candidate, BarrierStatus::PassThrough};
        }

        const float d_avail = env.range_ahead_m - env.safety_margin_m;
        if (d_avail <= 0.02f) {
            return {Setpoint{0.0f, candidate.yaw_rate}, BarrierStatus::EmergencyHalt};
        }

        // Аналітичний розрахунок граничної безпечної швидкості v = sqrt(2 * a * d)
        const float v_max_allowed = std::sqrt(2.0f * env.max_brake_accel_mps2 * d_avail);

        if (candidate.vx > v_max_allowed) {
            return {Setpoint{v_max_allowed, candidate.yaw_rate}, BarrierStatus::SpeedClamped};
        }

        return {candidate, BarrierStatus::PassThrough};
    }
};

} // namespace Control
