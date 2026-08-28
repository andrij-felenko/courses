#include <cstdint>
#include <algorithm>
#include <chrono>
#include <span>

namespace flight_safety {

constexpr int16_t kRcDeadbandNorm = 50;          // 5% deadband
constexpr uint32_t kGcsTimeoutDegradeMs = 250;  // Поріг м'якої деградації
constexpr uint32_t kGcsTimeoutFailsafeMs = 1000;// Поріг аварійного таймауту
constexpr float kMaxAxisSlewPerSec = 4000.0f;   // Одиниць на секунду

enum class ArbiterState : uint8_t {
    Disarmed = 0,
    RcActive,
    GcsActive,
    GcsDegraded,
    Failsafe
};

struct ControlAxes {
    int16_t roll{0};      // [-1000 .. 1000]
    int16_t pitch{0};     // [-1000 .. 1000]
    int16_t throttle{0};  // [0 .. 1000]
    int16_t yaw{0};       // [-1000 .. 1000]
    uint16_t buttons{0};

    [[nodiscard]] constexpr bool isDeflected() const noexcept {
        return (std::abs(roll) > kRcDeadbandNorm) ||
               (std::abs(pitch) > kRcDeadbandNorm) ||
               (std::abs(yaw) > kRcDeadbandNorm) ||
               (throttle > 100);
    }
};

class SafeControlArbiter {
public:
    constexpr SafeControlArbiter() noexcept = default;

    void feedDirectRc(const ControlAxes& rc, uint32_t now_ms) noexcept {
        raw_rc_ = rc;
        last_rc_time_ms_ = now_ms;
        rc_link_lost_ = false;
    }

    void feedMavlinkManualControl(int16_t x, int16_t y, int16_t z, int16_t r, 
                                 uint16_t buttons, uint32_t now_ms) noexcept {
        raw_gcs_.pitch = std::clamp<int16_t>(x, -1000, 1000);
        raw_gcs_.roll = std::clamp<int16_t>(y, -1000, 1000);
        raw_gcs_.throttle = std::clamp<int16_t>(z, 0, 1000);
        raw_gcs_.yaw = std::clamp<int16_t>(r, -1000, 1000);
        raw_gcs_.buttons = buttons;
        last_gcs_time_ms_ = now_ms;
    }

    void update(uint32_t now_ms, float dt_sec) noexcept {
        const uint32_t gcs_age = now_ms - last_gcs_time_ms_;
        const uint32_t rc_age = now_ms - last_rc_time_ms_;

        if (rc_age > 100) {
            rc_link_lost_ = true;
        }

        // 1. Апаратне перехоплення фізичним пультом пілота
        if (!rc_link_lost_ && raw_rc_.isDeflected()) {
            state_ = ArbiterState::RcActive;
            current_output_ = raw_rc_;
            return;
        }

        // 2. Лінійка станів таймауту від станції
        if (gcs_age < kGcsTimeoutDegradeMs) {
            state_ = ArbiterState::GcsActive;
            current_output_.roll = applySlew(current_output_.roll, raw_gcs_.roll, dt_sec);
            current_output_.pitch = applySlew(current_output_.pitch, raw_gcs_.pitch, dt_sec);
            current_output_.yaw = applySlew(current_output_.yaw, raw_gcs_.yaw, dt_sec);
            current_output_.throttle = applySlew(current_output_.throttle, raw_gcs_.throttle, dt_sec);
            current_output_.buttons = raw_gcs_.buttons;
        } else if (gcs_age < kGcsTimeoutFailsafeMs) {
            state_ = ArbiterState::GcsDegraded;
            current_output_.roll = applySlew(current_output_.roll, 0, dt_sec);
            current_output_.pitch = applySlew(current_output_.pitch, 0, dt_sec);
            current_output_.yaw = applySlew(current_output_.yaw, 0, dt_sec);
            current_output_.throttle = applySlew(current_output_.throttle, 500, dt_sec);
        } else {
            state_ = ArbiterState::Failsafe;
            current_output_ = ControlAxes{};
        }
    }

    [[nodiscard]] constexpr ArbiterState state() const noexcept { return state_; }
    [[nodiscard]] constexpr const ControlAxes& output() const noexcept { return current_output_; }

private:
    [[nodiscard]] static int16_t applySlew(int16_t current, int16_t target, float dt_sec) noexcept {
        const float max_delta = kMaxAxisSlewPerSec * dt_sec;
        const float diff = static_cast<float>(target - current);
        if (diff > max_delta) return current + static_cast<int16_t>(max_delta);
        if (diff < -max_delta) return current - static_cast<int16_t>(max_delta);
        return target;
    }

    ArbiterState state_{ArbiterState::Disarmed};
    ControlAxes current_output_{};
    ControlAxes raw_rc_{};
    ControlAxes raw_gcs_{};
    uint32_t last_rc_time_ms_{0};
    uint32_t last_gcs_time_ms_{0};
    bool rc_link_lost_{true};
};

} // namespace flight_safety
