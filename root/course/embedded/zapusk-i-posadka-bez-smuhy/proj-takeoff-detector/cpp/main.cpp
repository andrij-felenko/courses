#include <cstdint>
#include <algorithm>

enum class LaunchState : uint8_t {
    Idle = 0,
    WaitAccel,
    AccelDetected,
    MotorDelay,
    ThrottleRamp,
    Flying,
    Aborted
};

struct LaunchConfig {
    float accel_threshold_g{2.2f};      // Поріг прискорення кидка (g)
    uint32_t accel_time_ms{60};         // Мінімальний час розгону (мс)
    uint32_t motor_delay_ms{300};       // Затримка до вмикання мотора (мс)
    uint32_t launch_timeout_ms{3000};   // Аварійний тайм-аут процедури (мс)
    float throttle_ramp_rate{2.5f};     // Швидкість зростання тяги (1/с)
    float target_climb_throttle{0.85f}; // Тяга в наборі висоти (0..1)
};

class LaunchDetector {
public:
    constexpr explicit LaunchDetector(const LaunchConfig& config = {}) noexcept
        : config_(config) {}

    void arm() noexcept {
        is_armed_ = true;
        state_ = LaunchState::WaitAccel;
        state_timer_ms_ = 0;
        total_launch_timer_ms_ = 0;
        current_throttle_ = 0.0f;
    }

    void disarm() noexcept {
        is_armed_ = false;
        state_ = LaunchState::Idle;
        current_throttle_ = 0.0f;
        state_timer_ms_ = 0;
        total_launch_timer_ms_ = 0;
    }

    [[nodiscard]] float update(float accel_forward_g, float airspeed_ms, uint32_t dt_ms) noexcept {
        if (!is_armed_) {
            state_ = LaunchState::Idle;
            current_throttle_ = 0.0f;
            return 0.0f;
        }

        if (state_ != LaunchState::Idle && state_ != LaunchState::WaitAccel && state_ != LaunchState::Flying) {
            total_launch_timer_ms_ += dt_ms;
            if (total_launch_timer_ms_ > config_.launch_timeout_ms) {
                state_ = LaunchState::Aborted;
                current_throttle_ = 0.0f;
                return 0.0f;
            }
        }

        switch (state_) {
        case LaunchState::Idle:
        case LaunchState::Aborted:
            current_throttle_ = 0.0f;
            break;

        case LaunchState::WaitAccel:
            current_throttle_ = 0.0f;
            if (accel_forward_g >= config_.accel_threshold_g) {
                state_ = LaunchState::AccelDetected;
                state_timer_ms_ = 0;
            }
            break;

        case LaunchState::AccelDetected:
            current_throttle_ = 0.0f;
            state_timer_ms_ += dt_ms;
            if (accel_forward_g < config_.accel_threshold_g * 0.7f) {
                state_ = LaunchState::WaitAccel;
                state_timer_ms_ = 0;
            } else if (state_timer_ms_ >= config_.accel_time_ms) {
                state_ = LaunchState::MotorDelay;
                state_timer_ms_ = 0;
            }
            break;

        case LaunchState::MotorDelay:
            current_throttle_ = 0.0f;
            state_timer_ms_ += dt_ms;
            if (state_timer_ms_ >= config_.motor_delay_ms) {
                state_ = LaunchState::ThrottleRamp;
                state_timer_ms_ = 0;
            }
            break;

        case LaunchState::ThrottleRamp: {
            const float dt_sec = static_cast<float>(dt_ms) * 0.001f;
            current_throttle_ += config_.throttle_ramp_rate * dt_sec;
            if (current_throttle_ >= config_.target_climb_throttle) {
                current_throttle_ = config_.target_climb_throttle;
                state_ = LaunchState::Flying;
            }
            break;
        }

        case LaunchState::Flying:
            current_throttle_ = config_.target_climb_throttle;
            break;
        }

        return current_throttle_;
    }

    [[nodiscard]] LaunchState state() const noexcept { return state_; }
    [[nodiscard]] bool is_flying() const noexcept { return state_ == LaunchState::Flying; }
    [[nodiscard]] bool is_aborted() const noexcept { return state_ == LaunchState::Aborted; }
    [[nodiscard]] float throttle() const noexcept { return current_throttle_; }

private:
    LaunchConfig config_{};
    LaunchState state_{LaunchState::Idle};
    uint32_t state_timer_ms_{0};
    uint32_t total_launch_timer_ms_{0};
    float current_throttle_{0.0f};
    bool is_armed_{false};
};
