#include <cmath>
#include <cstdint>
#include <string_view>

namespace FlightSafety {

enum class FlightMode : uint8_t {
    Stabilize = 0,
    AltHold,
    PosHold,
    AutoRth
};

enum class ConsistencyStatus : uint8_t {
    Ok = 0,
    WarnMismatch,
    TriggerOverride
};

struct RcSticks {
    float roll{0.0f};     // [-1.0 .. 1.0]
    float pitch{0.0f};    // [-1.0 .. 1.0]
    float throttle{0.0f}; // [0.0 .. 1.0]

    [[nodiscard]] constexpr float magnitude() const noexcept {
        return std::sqrt(roll * roll + pitch * pitch);
    }
};

struct VelocityEstimate {
    float vx{0.0f}; // North, м/с
    float vy{0.0f}; // East, м/с

    [[nodiscard]] constexpr float speed() const noexcept {
        return std::sqrt(vx * vx + vy * vy);
    }
};

class ModeMonitor {
public:
    static constexpr float StickFightThreshold{0.35f};
    static constexpr uint32_t FightTimeLimitMs{400};
    static constexpr float DeadzoneThreshold{0.08f};
    static constexpr float DriftSpeedThreshold{1.5f};

    struct Result {
        ConsistencyStatus status{ConsistencyStatus::Ok};
        std::string_view message{"OK"};
    };

    Result evaluate(FlightMode mode,
                    const RcSticks& rc,
                    const VelocityEstimate& vel,
                    uint32_t now_ms) noexcept {
        // 1. Виявлення активної боротьби з траєкторією в RTH
        if (mode == FlightMode::AutoRth) {
            if (rc.magnitude() > StickFightThreshold && vel.speed() > 0.5f) {
                float dot = (rc.pitch * vel.vx) + (rc.roll * vel.vy);
                if (dot < 0.0f) {
                    if (fight_timer_ms_ == 0) {
                        fight_timer_ms_ = now_ms;
                    } else if (now_ms - fight_timer_ms_ > FightTimeLimitMs) {
                        return {ConsistencyStatus::TriggerOverride, "STICK_FIGHTING_RTH"};
                    }
                } else {
                    fight_timer_ms_ = 0;
                }
            } else {
                fight_timer_ms_ = 0;
            }
        } else {
            fight_timer_ms_ = 0;
        }

        // 2. Непомічений дрейф у режимі утримання лише висоти
        if (mode == FlightMode::AltHold) {
            if (rc.magnitude() < DeadzoneThreshold && vel.speed() > DriftSpeedThreshold) {
                if (drift_timer_ms_ == 0) {
                    drift_timer_ms_ = now_ms;
                } else if (now_ms - drift_timer_ms_ > 1000) {
                    return {ConsistencyStatus::WarnMismatch, "UNNOTICED_DRIFT_IN_ALTHOLD"};
                }
            } else {
                drift_timer_ms_ = 0;
            }
        } else {
            drift_timer_ms_ = 0;
        }

        return {ConsistencyStatus::Ok, "OK"};
    }

    void reset() noexcept {
        fight_timer_ms_ = 0;
        drift_timer_ms_ = 0;
    }

private:
    uint32_t fight_timer_ms_{0};
    uint32_t drift_timer_ms_{0};
};

} // namespace FlightSafety
