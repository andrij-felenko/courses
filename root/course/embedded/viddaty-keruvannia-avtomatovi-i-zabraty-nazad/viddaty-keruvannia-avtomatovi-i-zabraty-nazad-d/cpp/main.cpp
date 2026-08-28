#include <cstdint>
#include <cmath>
#include <algorithm>
#include <array>

class TakeoverManager {
public:
    enum class State : uint8_t {
        AutoNav = 0,
        OverrideIn,
        ManualHold,
        HandbackWait,
        BlendingOut
    };

    struct StickInput {
        float roll{0.0f};     // [-1.0 ... +1.0]
        float pitch{0.0f};
        float yaw{0.0f};
        float throttle{0.5f}; // [0.0 ... 1.0]
    };

    struct ControlCommand {
        float roll{0.0f};
        float pitch{0.0f};
        float yaw{0.0f};
        float throttle{0.0f};
    };

    struct Config {
        float stick_deadband{0.12f};
        float blend_in_time_sec{0.20f};
        float blend_out_time_sec{0.40f};
        float handback_hold_sec{1.50f};
    };

    explicit TakeoverManager(Config config = {}) : cfg_(config) {}

    void update(const StickInput& sticks,
                const ControlCommand& cmd_auto,
                const ControlCommand& cmd_pilot,
                ControlCommand& cmd_out,
                float dt_sec) noexcept {
        const bool sticks_deflected = is_deflected(sticks);

        switch (state_) {
            case State::AutoNav:
                alpha_ = 0.0f;
                if (sticks_deflected) {
                    state_ = State::OverrideIn;
                    annunciation_pending_ = true;
                }
                break;

            case State::OverrideIn:
                alpha_ += dt_sec / cfg_.blend_in_time_sec;
                if (alpha_ >= 1.0f) {
                    alpha_ = 1.0f;
                    state_ = State::ManualHold;
                }
                break;

            case State::ManualHold:
                alpha_ = 1.0f;
                if (!sticks_deflected) {
                    state_ = State::HandbackWait;
                    hold_timer_sec_ = 0.0f;
                }
                break;

            case State::HandbackWait:
                alpha_ = 1.0f;
                if (sticks_deflected) {
                    state_ = State::ManualHold;
                    hold_timer_sec_ = 0.0f;
                } else {
                    hold_timer_sec_ += dt_sec;
                    if (hold_timer_sec_ >= cfg_.handback_hold_sec) {
                        state_ = State::BlendingOut;
                    }
                }
                break;

            case State::BlendingOut:
                if (sticks_deflected) {
                    state_ = State::OverrideIn;
                } else {
                    alpha_ -= dt_sec / cfg_.blend_out_time_sec;
                    if (alpha_ <= 0.0f) {
                        alpha_ = 0.0f;
                        state_ = State::AutoNav;
                    }
                }
                break;
        }

        blend_commands(cmd_auto, cmd_pilot, cmd_out);
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] float alpha() const noexcept { return alpha_; }
    [[nodiscard]] bool check_and_clear_annunciation() noexcept {
        bool result = annunciation_pending_;
        annunciation_pending_ = false;
        return result;
    }

private:
    [[nodiscard]] bool is_deflected(const StickInput& sticks) const noexcept {
        return (std::abs(sticks.roll) > cfg_.stick_deadband) ||
               (std::abs(sticks.pitch) > cfg_.stick_deadband) ||
               (std::abs(sticks.yaw) > cfg_.stick_deadband) ||
               (std::abs(sticks.throttle - 0.5f) > cfg_.stick_deadband);
    }

    void blend_commands(const ControlCommand& a,
                        const ControlCommand& p,
                        ControlCommand& out) const noexcept {
        const float w_pilot = std::clamp(alpha_, 0.0f, 1.0f);
        const float w_auto  = 1.0f - w_pilot;

        out.roll     = w_auto * a.roll     + w_pilot * p.roll;
        out.pitch    = w_auto * a.pitch    + w_pilot * p.pitch;
        out.yaw      = w_auto * a.yaw      + w_pilot * p.yaw;
        out.throttle = w_auto * a.throttle + w_pilot * p.throttle;
    }

    Config cfg_;
    State state_{State::AutoNav};
    float alpha_{0.0f};
    float hold_timer_sec_{0.0f};
    bool annunciation_pending_{false};
};
