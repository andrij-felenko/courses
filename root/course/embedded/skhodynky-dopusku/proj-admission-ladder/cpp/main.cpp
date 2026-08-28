#include <cstdint>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>

namespace embedded::autonomy {

enum class AdmissionMode : uint8_t {
    Shadow = 0,
    Advisory,
    Supervised,
    BoundedAutonomous,
    ManualOverride,
    FailsafeRth
};

struct Setpoint {
    float roll_deg{0.0f};      // [-45.0 .. +45.0]
    float pitch_deg{0.0f};     // [-45.0 .. +45.0]
    float yaw_rate_dps{0.0f};  // [deg/s]
    float throttle_norm{0.0f}; // [0.0 .. 1.0]

    [[nodiscard]] constexpr Setpoint blend_to(const Setpoint& target, float alpha) const noexcept {
        if (alpha >= 1.0f) return target;
        if (alpha <= 0.0f) return *this;

        return Setpoint{
            roll_deg      + alpha * (target.roll_deg      - roll_deg),
            pitch_deg     + alpha * (target.pitch_deg     - pitch_deg),
            yaw_rate_dps  + alpha * (target.yaw_rate_dps  - yaw_rate_dps),
            throttle_norm + alpha * (target.throttle_norm - throttle_norm)
        };
    }
};

struct TelemetrySnapshot {
    float distance_to_fence_m{100.0f};
    float wind_speed_mps{0.0f};
    float ekf_uncertainty_m{0.2f};
    bool  link_alive{true};
    bool  deadman_switch{false};
    bool  confirm_button{false};
};

class AdmissionArbiter {
public:
    static constexpr uint32_t kBlendDurationMs      = 200;
    static constexpr uint32_t kDeadmanTimeoutMs     = 300;
    static constexpr uint32_t kSuggestionTtlMs      = 1500;
    static constexpr float    kStickTakeoverRatio   = 0.15f;

    explicit constexpr AdmissionArbiter(AdmissionMode initial_mode) noexcept
        : current_mode_(initial_mode),
          target_mode_(initial_mode) {}

    [[nodiscard]] AdmissionMode current_mode() const noexcept { return current_mode_; }
    [[nodiscard]] float average_divergence() const noexcept {
        return sample_count_ > 0 ? (divergence_sum_ / static_cast<float>(sample_count_)) : 0.0f;
    }

    void submit_suggestion(uint32_t timestamp_ms) noexcept {
        suggestion_time_ms_ = timestamp_ms;
        pending_suggestion_ = true;
    }

    Setpoint update(const Setpoint& pilot_sp,
                    const Setpoint& algo_sp,
                    const TelemetrySnapshot& telem,
                    uint32_t now_ms) noexcept
    {
        Setpoint target_sp = pilot_sp;

        if (telem.deadman_switch) {
            last_deadman_ping_ms_ = now_ms;
        }

        switch (current_mode_) {
            case AdmissionMode::Shadow:
                target_sp = pilot_sp;
                accumulate_shadow_divergence(pilot_sp, algo_sp);
                break;

            case AdmissionMode::Advisory:
                target_sp = pilot_sp;
                if (pending_suggestion_) {
                    if (now_ms - suggestion_time_ms_ > kSuggestionTtlMs) {
                        pending_suggestion_ = false; // Вичерпано TTL
                    } else if (telem.confirm_button) {
                        target_sp = algo_sp;
                        pending_suggestion_ = false;
                    }
                }
                break;

            case AdmissionMode::Supervised:
                if (!telem.deadman_switch || is_stick_deflected(pilot_sp)) {
                    trigger_override(pilot_sp);
                    target_sp = pilot_sp;
                } else {
                    target_sp = algo_sp;
                }
                break;

            case AdmissionMode::BoundedAutonomous:
                if (is_outside_odd(telem)) {
                    current_mode_ = AdmissionMode::FailsafeRth;
                    blend_progress_ = 0.0f;
                    target_sp = pilot_sp;
                } else if (is_stick_deflected(pilot_sp)) {
                    trigger_override(pilot_sp);
                    target_sp = pilot_sp;
                } else {
                    target_sp = algo_sp;
                }
                break;

            case AdmissionMode::ManualOverride:
            case AdmissionMode::FailsafeRth:
            default:
                target_sp = pilot_sp;
                break;
        }

        return apply_bumpless_blending(target_sp);
    }

private:
    AdmissionMode current_mode_;
    AdmissionMode target_mode_;
    Setpoint      last_output_sp_{};
    uint32_t      last_deadman_ping_ms_{0};
    uint32_t      suggestion_time_ms_{0};
    bool          pending_suggestion_{false};
    float         blend_progress_{1.0f};

    float         divergence_sum_{0.0f};
    uint32_t      sample_count_{0};

    [[nodiscard]] static bool is_stick_deflected(const Setpoint& sp) noexcept {
        return (std::abs(sp.roll_deg) > kStickTakeoverRatio * 45.0f) ||
               (std::abs(sp.pitch_deg) > kStickTakeoverRatio * 45.0f);
    }

    [[nodiscard]] static bool is_outside_odd(const TelemetrySnapshot& telem) noexcept {
        return (telem.distance_to_fence_m < 15.0f) ||
               (telem.wind_speed_mps > 12.0f) ||
               (telem.ekf_uncertainty_m > 2.5f) ||
               (!telem.link_alive);
    }

    void trigger_override(const Setpoint& pilot_sp) noexcept {
        current_mode_ = AdmissionMode::ManualOverride;
        blend_progress_ = 0.0f;
        last_output_sp_ = pilot_sp;
    }

    void accumulate_shadow_divergence(const Setpoint& pilot_sp, const Setpoint& algo_sp) noexcept {
        const float d_roll = pilot_sp.roll_deg - algo_sp.roll_deg;
        const float d_pitch = pilot_sp.pitch_deg - algo_sp.pitch_deg;
        divergence_sum_ += std::sqrt(d_roll * d_roll + d_pitch * d_pitch);
        sample_count_++;
    }

    Setpoint apply_bumpless_blending(const Setpoint& desired_sp) noexcept {
        if (blend_progress_ < 1.0f) {
            constexpr float kDtRatio = 20.0f / static_cast<float>(kBlendDurationMs);
            blend_progress_ = std::min(1.0f, blend_progress_ + kDtRatio);
            last_output_sp_ = last_output_sp_.blend_to(desired_sp, blend_progress_);
        } else {
            last_output_sp_ = desired_sp;
        }
        return last_output_sp_;
    }
};

} // namespace embedded::autonomy
