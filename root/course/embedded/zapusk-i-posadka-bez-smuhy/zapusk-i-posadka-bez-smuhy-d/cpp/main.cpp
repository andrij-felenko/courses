#include <cstdint>
#include <algorithm>

enum class FlightFsmState : uint8_t {
    Idle = 0,
    TakeoffWaitTrigger,
    TakeoffRampup,
    TakeoffClimb,
    MissionNav,
    LandApproach,
    LandGlideslope,
    LandFlare,
    LandTouchdown,
    LandAbort
};

struct FlightFsmConfig {
    float accel_launch_threshold_g{2.2f};
    float safe_climb_alt_m{25.0f};
    float flare_alt_m{1.2f};
    float approach_airspeed_ms{14.0f};
    float climb_pitch_deg{14.0f};
    float flare_pitch_deg{6.0f};
};

struct FlightFsmOutput {
    float target_pitch_deg{0.0f};
    float target_roll_deg{0.0f};
    float throttle_cmd{0.0f};
    bool esc_brake_enable{false};
    bool is_disarmed{false};
};

class FlightFsm {
public:
    constexpr explicit FlightFsm(const FlightFsmConfig& config = {}) noexcept
        : config_(config) {}

    void start_takeoff() noexcept {
        state_ = FlightFsmState::TakeoffWaitTrigger;
        state_timer_ms_ = 0;
        current_throttle_ = 0.0f;
    }

    void start_landing() noexcept {
        if (state_ == FlightFsmState::MissionNav) {
            state_ = FlightFsmState::LandApproach;
            state_timer_ms_ = 0;
        }
    }

    [[nodiscard]] FlightFsmOutput update(float accel_x_g,
                                         float alt_agl_m,
                                         float airspeed_ms,
                                         bool abort_requested,
                                         uint32_t dt_ms) noexcept {
        FlightFsmOutput out{};
        state_timer_ms_ += dt_ms;

        switch (state_) {
        case FlightFsmState::Idle:
            out.is_disarmed = true;
            break;

        case FlightFsmState::TakeoffWaitTrigger:
            out.target_pitch_deg = config_.climb_pitch_deg;
            out.target_roll_deg = 0.0f;
            out.throttle_cmd = 0.0f;
            if (accel_x_g >= config_.accel_launch_threshold_g) {
                state_ = FlightFsmState::TakeoffRampup;
                state_timer_ms_ = 0;
            }
            break;

        case FlightFsmState::TakeoffRampup: {
            out.target_pitch_deg = config_.climb_pitch_deg;
            out.target_roll_deg = 0.0f;
            if (state_timer_ms_ > 250) {
                current_throttle_ += 2.0f * (static_cast<float>(dt_ms) * 0.001f);
                if (current_throttle_ >= 0.90f) {
                    current_throttle_ = 0.90f;
                    state_ = FlightFsmState::TakeoffClimb;
                    state_timer_ms_ = 0;
                }
            }
            out.throttle_cmd = current_throttle_;
            break;
        }

        case FlightFsmState::TakeoffClimb:
            out.target_pitch_deg = config_.climb_pitch_deg;
            out.target_roll_deg = 0.0f;
            out.throttle_cmd = 0.90f;
            if (alt_agl_m >= config_.safe_climb_alt_m) {
                state_ = FlightFsmState::MissionNav;
                state_timer_ms_ = 0;
            }
            break;

        case FlightFsmState::MissionNav:
            out.target_pitch_deg = 2.0f;
            out.target_roll_deg = 0.0f;
            out.throttle_cmd = 0.60f;
            break;

        case FlightFsmState::LandApproach:
            out.target_pitch_deg = -3.0f;
            out.target_roll_deg = 0.0f;
            out.throttle_cmd = (airspeed_ms < config_.approach_airspeed_ms) ? 0.45f : 0.20f;
            if (alt_agl_m <= 10.0f) {
                state_ = FlightFsmState::LandGlideslope;
                state_timer_ms_ = 0;
            }
            if (abort_requested) {
                state_ = FlightFsmState::LandAbort;
                state_timer_ms_ = 0;
            }
            break;

        case FlightFsmState::LandGlideslope:
            out.target_pitch_deg = -3.5f;
            out.target_roll_deg = 0.0f;
            out.throttle_cmd = 0.25f;
            if (alt_agl_m <= config_.flare_alt_m) {
                state_ = FlightFsmState::LandFlare;
                state_timer_ms_ = 0;
            }
            if (abort_requested) {
                state_ = FlightFsmState::LandAbort;
                state_timer_ms_ = 0;
            }
            break;

        case FlightFsmState::LandFlare:
            out.target_pitch_deg = config_.flare_pitch_deg;
            out.target_roll_deg = 0.0f;
            out.throttle_cmd = 0.0f;
            out.esc_brake_enable = true;
            if (alt_agl_m <= 0.2f || state_timer_ms_ > 2500) {
                state_ = FlightFsmState::LandTouchdown;
                state_timer_ms_ = 0;
            }
            break;

        case FlightFsmState::LandTouchdown:
            out.target_pitch_deg = 0.0f;
            out.target_roll_deg = 0.0f;
            out.throttle_cmd = 0.0f;
            out.esc_brake_enable = true;
            out.is_disarmed = true;
            break;

        case FlightFsmState::LandAbort:
            out.target_pitch_deg = config_.climb_pitch_deg;
            out.target_roll_deg = 0.0f;
            out.throttle_cmd = 1.0f;
            if (alt_agl_m >= config_.safe_climb_alt_m) {
                state_ = FlightFsmState::MissionNav;
                state_timer_ms_ = 0;
            }
            break;
        }

        return out;
    }

    [[nodiscard]] FlightFsmState state() const noexcept { return state_; }

private:
    FlightFsmConfig config_{};
    FlightFsmState state_{FlightFsmState::Idle};
    uint32_t state_timer_ms_{0};
    float current_throttle_{0.0f};
};
