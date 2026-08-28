#include <cmath>
#include <cstdint>
#include <string_view>
#include <algorithm>

namespace FlightSafety {

enum class FlightMode : uint8_t {
    Manual = 0,
    Stabilize,
    AltHold,
    PosHold,
    AutoMission,
    AutoRth,
    EmergencyLand
};

enum class MismatchSeverity : uint8_t {
    Normal = 0,
    WarningAnnunciation,
    OverrideTakeover
};

struct PilotSticks {
    float roll{0.0f};      // [-1.0 .. +1.0]
    float pitch{0.0f};
    float yaw{0.0f};
    float throttle{0.0f}; // [0.0 .. 1.0]

    [[nodiscard]] constexpr float magnitude() const noexcept {
        return std::sqrt(roll * roll + pitch * pitch);
    }
};

struct NavVector {
    float vel_x{0.0f}; // Північ, м/с
    float vel_y{0.0f}; // Схід, м/с
    float vel_z{0.0f}; // Вниз, м/с

    [[nodiscard]] constexpr float horizontal_speed() const noexcept {
        return std::sqrt(vel_x * vel_x + vel_y * vel_y);
    }
};

class ModeConsistencyMonitor {
public:
    static constexpr float StickDeadzone{0.08f};
    static constexpr float StickFightThreshold{0.35f};
    static constexpr float ThrottleLowThreshold{0.05f};
    static constexpr float DriftSpeedThreshold{1.5f};
    static constexpr float StirDerivativeThresh{2.5f};

    static constexpr uint32_t FightingTimeLimitMs{400};
    static constexpr uint32_t ThrottleTimeLimitMs{800};
    static constexpr uint32_t DriftTimeLimitMs{1200};
    static constexpr uint32_t StirWindowMs{600};
    static constexpr int StirMaxReversals{4};

    struct AssessmentResult {
        MismatchSeverity severity{MismatchSeverity::Normal};
        std::string_view reason{"OK"};
    };

    AssessmentResult update(FlightMode active_mode,
                            const PilotSticks& sticks,
                            const NavVector& nav,
                            uint32_t now_ms) noexcept {
        float dt = (last_update_ms_ == 0) ? 0.02f : static_cast<float>(now_ms - last_update_ms_) / 1000.0f;
        if (dt <= 0.0f) dt = 0.02f;
        last_update_ms_ = now_ms;

        // 1. Боротьба з автопілотом в автономних режимах
        if (is_autonomous(active_mode)) {
            if (sticks.magnitude() > StickFightThreshold && nav.horizontal_speed() > 0.5f) {
                float dot_product = (sticks.pitch * nav.vel_x) + (sticks.roll * nav.vel_y);
                if (dot_product < 0.0f) {
                    if (fight_start_time_ms_ == 0) {
                        fight_start_time_ms_ = now_ms;
                    } else if (now_ms - fight_start_time_ms_ > FightingTimeLimitMs) {
                        return {MismatchSeverity::OverrideTakeover, "STICK_FIGHTING_RTH"};
                    }
                } else {
                    fight_start_time_ms_ = 0;
                }
            } else {
                fight_start_time_ms_ = 0;
            }
        } else {
            fight_start_time_ms_ = 0;
        }

        // 2. Пастка нульового газу в режимах утримання висоти
        if (holds_altitude(active_mode) && sticks.throttle < ThrottleLowThreshold) {
            if (throttle_panic_start_ms_ == 0) {
                throttle_panic_start_ms_ = now_ms;
            } else if (now_ms - throttle_panic_start_ms_ > ThrottleTimeLimitMs) {
                return {MismatchSeverity::WarningAnnunciation, "ZERO_THROTTLE_IN_ALTHOLD"};
            }
        } else {
            throttle_panic_start_ms_ = 0;
        }

        // 3. Дрейф після тихого скидання PosHold -> AltHold
        if (active_mode == FlightMode::AltHold) {
            if (sticks.magnitude() < StickDeadzone && nav.horizontal_speed() > DriftSpeedThreshold) {
                if (drift_start_time_ms_ == 0) {
                    drift_start_time_ms_ = now_ms;
                } else if (now_ms - drift_start_time_ms_ > DriftTimeLimitMs) {
                    return {MismatchSeverity::WarningAnnunciation, "UNNOTICED_DRIFT_IN_ALTHOLD"};
                }
            } else {
                drift_start_time_ms_ = 0;
            }
        } else {
            drift_start_time_ms_ = 0;
        }

        // 4. Панічне сіпання стіками
        float d_roll = (sticks.roll - last_roll_) / dt;
        float current_sign = (d_roll > 0.1f) ? 1.0f : ((d_roll < -0.1f) ? -1.0f : 0.0f);

        if (now_ms - stir_window_start_ms_ > StirWindowMs) {
            stir_window_start_ms_ = now_ms;
            reversal_count_ = 0;
        }

        if (current_sign != 0.0f && last_sign_ != 0.0f && current_sign != last_sign_) {
            if (std::abs(d_roll) > StirDerivativeThresh) {
                if (++reversal_count_ >= StirMaxReversals) {
                    return {MismatchSeverity::WarningAnnunciation, "PANIC_STICK_STIRRING"};
                }
            }
        }

        last_sign_ = current_sign;
        last_roll_ = sticks.roll;
        last_pitch_ = sticks.pitch;

        return {MismatchSeverity::Normal, "OK"};
    }

    void reset() noexcept {
        fight_start_time_ms_ = 0;
        throttle_panic_start_ms_ = 0;
        drift_start_time_ms_ = 0;
        last_roll_ = 0.0f;
        last_pitch_ = 0.0f;
        last_update_ms_ = 0;
        reversal_count_ = 0;
        stir_window_start_ms_ = 0;
        last_sign_ = 0.0f;
    }

private:
    static constexpr bool is_autonomous(FlightMode mode) noexcept {
        return mode == FlightMode::AutoMission || mode == FlightMode::AutoRth;
    }

    static constexpr bool holds_altitude(FlightMode mode) noexcept {
        return mode == FlightMode::AltHold || mode == FlightMode::PosHold || is_autonomous(mode);
    }

    uint32_t fight_start_time_ms_{0};
    uint32_t throttle_panic_start_ms_{0};
    uint32_t drift_start_time_ms_{0};

    float last_roll_{0.0f};
    float last_pitch_{0.0f};
    uint32_t last_update_ms_{0};

    int reversal_count_{0};
    uint32_t stir_window_start_ms_{0};
    float last_sign_{0.0f};
};

} // namespace FlightSafety
