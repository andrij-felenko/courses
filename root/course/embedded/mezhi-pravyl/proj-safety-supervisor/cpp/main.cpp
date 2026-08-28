#include <cstdint>
#include <cmath>
#include <algorithm>
#include <expected>
#include <span>

namespace Safety {

struct CommandVector {
    float vx{0.0f};       // Лінійна швидкість уперед, м/с
    float vy{0.0f};       // Бічна швидкість, м/с
    float yaw_rate{0.0f}; // Кутова швидкість, рад/с
};

struct SensorEnvelope {
    float obstacle_dist_m{0.0f};
    float battery_voltage{16.0f};
    float current_tilt_rad{0.0f};
    float max_tilt_limit{0.52f}; // ~30 градусів
    bool  emergency_switch{false};
};

enum class Status : uint8_t {
    PassThrough,
    Clamped,
    BrakeEngaged,
    EmergencyStop
};

enum class FaultCode : uint8_t {
    InvalidTimeStep,
    SensorSignalLost,
    CriticalTiltExceeded
};

class Supervisor {
public:
    static constexpr float kSafetyMarginM{0.35f};
    static constexpr float kMaxBrakeAccelMps2{3.0f};
    static constexpr float kLatencyPadSec{0.04f};
    static constexpr float kMaxAllowedSpeedMps{2.5f};
    static constexpr float kMaxYawRateRadps{1.8f};
    static constexpr float kCriticalVoltageV{13.8f};
    static constexpr float kNominalVoltageV{16.0f};
    static constexpr uint32_t kWatchdogMaxTicks{10};

    constexpr Supervisor() noexcept = default;

    std::expected<std::pair<CommandVector, Status>, FaultCode> evaluate(
        const CommandVector& candidate,
        const SensorEnvelope& sensors,
        float dt_sec
    ) noexcept {
        if (dt_sec <= 0.0f) {
            return std::unexpected(FaultCode::InvalidTimeStep);
        }

        current_tick_++;

        if (sensors.emergency_switch) {
            last_safe_vx_ = 0.0f;
            return std::pair{CommandVector{0.0f, 0.0f, 0.0f}, Status::EmergencyStop};
        }

        // Захист від перевищення критичного крену
        if (sensors.current_tilt_rad >= sensors.max_tilt_limit) {
            last_safe_vx_ = 0.0f;
            return std::unexpected(FaultCode::CriticalTiltExceeded);
        }

        // Тайм-аут планувальника
        if ((current_tick_ - last_valid_tick_) > kWatchdogMaxTicks) {
            const float decel = kMaxBrakeAccelMps2 * dt_sec;
            last_safe_vx_ = std::max(0.0f, last_safe_vx_ - decel);
            return std::pair{CommandVector{last_safe_vx_, 0.0f, 0.0f}, Status::BrakeEngaged};
        }

        float target_vx = std::max(0.0f, candidate.vx);
        bool is_clamped = false;

        // 1. Динамічний гальмівний бар'єр
        const float stop_dist = (target_vx * target_vx) / (2.0f * kMaxBrakeAccelMps2)
                              + target_vx * kLatencyPadSec
                              + kSafetyMarginM;

        if (sensors.obstacle_dist_m < stop_dist) {
            const float available_dist = sensors.obstacle_dist_m - kSafetyMarginM;
            if (available_dist <= 0.05f) {
                target_vx = 0.0f;
            } else {
                const float max_v_safe = std::sqrt(2.0f * kMaxBrakeAccelMps2 * available_dist);
                if (target_vx > max_v_safe) {
                    target_vx = max_v_safe;
                    is_clamped = true;
                }
            }
        }

        // 2. Корекція за просіданням батареї
        if (sensors.battery_voltage < kNominalVoltageV) {
            const float v_span = kNominalVoltageV - kCriticalVoltageV;
            const float v_factor = std::clamp((sensors.battery_voltage - kCriticalVoltageV) / v_span, 0.0f, 1.0f);
            const float max_bat_vx = kMaxAllowedSpeedMps * v_factor;
            if (target_vx > max_bat_vx) {
                target_vx = max_bat_vx;
                is_clamped = true;
            }
        }

        // 3. Обмеження рискання за нахилом
        float target_yaw_rate = candidate.yaw_rate;
        const float tilt_warning_thresh = sensors.max_tilt_limit * 0.8f;
        if (sensors.current_tilt_rad > tilt_warning_thresh) {
            const float tilt_headroom = sensors.max_tilt_limit - tilt_warning_thresh;
            const float tilt_scale = std::clamp((sensors.max_tilt_limit - sensors.current_tilt_rad) / tilt_headroom, 0.0f, 1.0f);
            target_yaw_rate *= tilt_scale;
            target_vx *= tilt_scale;
            is_clamped = true;
        }

        // 4. Фізичні обмеження приводів
        if (target_vx > kMaxAllowedSpeedMps) {
            target_vx = kMaxAllowedSpeedMps;
            is_clamped = true;
        }
        const float clamped_yaw = std::clamp(target_yaw_rate, -kMaxYawRateRadps, kMaxYawRateRadps);
        if (clamped_yaw != target_yaw_rate) {
            target_yaw_rate = clamped_yaw;
            is_clamped = true;
        }

        last_safe_vx_ = target_vx;
        last_valid_tick_ = current_tick_;

        CommandVector safe_cmd{target_vx, candidate.vy, target_yaw_rate};
        return std::pair{safe_cmd, is_clamped ? Status::Clamped : Status::PassThrough};
    }

    void notify_planner_alive() noexcept {
        last_valid_tick_ = current_tick_;
    }

private:
    uint32_t last_valid_tick_{0};
    uint32_t current_tick_{0};
    float    last_safe_vx_{0.0f};
};

} // namespace Safety
