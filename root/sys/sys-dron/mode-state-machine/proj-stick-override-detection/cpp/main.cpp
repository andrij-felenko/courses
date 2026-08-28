#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>
#include <string_view>

namespace autopilot::rc_override {

enum class ChannelAxis : uint8_t {
    Roll = 0,
    Pitch = 1,
    Yaw = 2,
    Throttle = 3,
    Count = 4
};

enum class OverrideState : uint8_t {
    Idle = 0,
    Qualifying,
    Active,
    ReleaseHold
};

enum class FallbackFlightMode : uint8_t {
    Stabilize = 0,
    AltHold = 1,
    PosHold = 2,
    Acro = 3
};

struct ChannelMask {
    static constexpr uint32_t Roll     = 1u << 0;
    static constexpr uint32_t Pitch    = 1u << 1;
    static constexpr uint32_t Yaw      = 1u << 2;
    static constexpr uint32_t Throttle = 1u << 3;
    static constexpr uint32_t RollPitch = Roll | Pitch;
    static constexpr uint32_t All = Roll | Pitch | Yaw | Throttle;
};

struct SensorFlags {
    static constexpr uint32_t AhrsAttitude = 1u << 1;
    static constexpr uint32_t EkfVertPos   = 1u << 3;
    static constexpr uint32_t EkfHorizPos  = 1u << 4;
};

// Конфігурація окремого фізичного каналу радіокерування
struct ChannelCalibration {
    uint16_t pwm_min{1000};
    uint16_t pwm_trim{1500};
    uint16_t pwm_max{2000};
    float deadband_norm{0.05f};    // 5% радіус мертвої зони
    float threshold_norm{0.15f};   // 15% поріг детектування втручання

    [[nodiscard]] constexpr float normalize(uint16_t pwm_raw) const noexcept {
        const uint16_t clamped_pwm = std::clamp(pwm_raw, pwm_min, pwm_max);
        float raw_norm = 0.0f;

        if (clamped_pwm >= pwm_trim) {
            const float span = static_cast<float>(pwm_max - pwm_trim);
            if (span > 1.0f) {
                raw_norm = static_cast<float>(clamped_pwm - pwm_trim) / span;
            }
        } else {
            const float span = static_cast<float>(pwm_trim - pwm_min);
            if (span > 1.0f) {
                raw_norm = -static_cast<float>(pwm_trim - clamped_pwm) / span;
            }
        }

        const float abs_val = std::abs(raw_norm);
        if (abs_val <= deadband_norm) {
            return 0.0f;
        }

        const float scaled = (abs_val - deadband_norm) / (1.0f - deadband_norm);
        const float clamped_scaled = std::clamp(scaled, 0.0f, 1.0f);
        return (raw_norm >= 0.0f) ? clamped_scaled : -clamped_scaled;
    }
};

// Нормалізовані польотні вектори керування
struct NormalizedChannels {
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
    float throttle{0.0f};
    bool is_valid{false};

    [[nodiscard]] constexpr float get(ChannelAxis axis) const noexcept {
        switch (axis) {
            case ChannelAxis::Roll: return roll;
            case ChannelAxis::Pitch: return pitch;
            case ChannelAxis::Yaw: return yaw;
            case ChannelAxis::Throttle: return throttle;
            default: return 0.0f;
        }
    }
};

// Повний конфігураційний профіль модуля
struct Config {
    std::array<ChannelCalibration, static_cast<size_t>(ChannelAxis::Count)> channels{};
    uint32_t channel_mask{ChannelMask::RollPitch | ChannelMask::Throttle};
    uint32_t activation_delay_ms{100};
    uint32_t release_hold_ms{1000};
    float euclidean_threshold_rp{0.18f};
    bool use_euclidean_norm{true};

    constexpr Config() noexcept {
        channels[static_cast<size_t>(ChannelAxis::Throttle)].threshold_norm = 0.20f;
        channels[static_cast<size_t>(ChannelAxis::Yaw)].threshold_norm = 0.25f;
    }
};

// Клас детектора втручання пілота
class StickOverrideDetector {
public:
    explicit constexpr StickOverrideDetector(const Config& config = Config{}) noexcept
        : config_(config) {}

    void reset() noexcept {
        state_ = OverrideState::Idle;
        state_entry_ms_ = 0;
        last_update_ms_ = 0;
        current_max_deflection_ = 0.0f;
        override_active_ = false;
        latched_transition_event_ = false;
        recommended_mode_ = FallbackFlightMode::PosHold;
    }

    [[nodiscard]] NormalizedChannels process_raw_channels(std::span<const uint16_t> raw_pwm) const noexcept {
        NormalizedChannels out{};
        if (raw_pwm.size() < static_cast<size_t>(ChannelAxis::Count)) {
            return out;
        }

        out.roll = config_.channels[static_cast<size_t>(ChannelAxis::Roll)].normalize(raw_pwm[0]);
        out.pitch = config_.channels[static_cast<size_t>(ChannelAxis::Pitch)].normalize(raw_pwm[1]);
        out.yaw = config_.channels[static_cast<size_t>(ChannelAxis::Yaw)].normalize(raw_pwm[2]);
        out.throttle = config_.channels[static_cast<size_t>(ChannelAxis::Throttle)].normalize(raw_pwm[3]);
        out.is_valid = true;
        return out;
    }

    void update(const NormalizedChannels& rc, uint32_t sensor_flags, uint32_t current_time_ms) noexcept {
        if (!rc.is_valid) {
            return;
        }

        last_update_ms_ = current_time_ms;
        latched_transition_event_ = false;

        const bool threshold_exceeded = evaluate_deflection(rc);

        switch (state_) {
            case OverrideState::Idle:
                override_active_ = false;
                if (threshold_exceeded) {
                    state_ = OverrideState::Qualifying;
                    state_entry_ms_ = current_time_ms;
                }
                break;

            case OverrideState::Qualifying:
                override_active_ = false;
                if (!threshold_exceeded) {
                    state_ = OverrideState::Idle;
                } else if ((current_time_ms - state_entry_ms_) >= config_.activation_delay_ms) {
                    state_ = OverrideState::Active;
                    state_entry_ms_ = current_time_ms;
                    override_active_ = true;
                    latched_transition_event_ = true;
                    recommended_mode_ = resolve_fallback(sensor_flags);
                }
                break;

            case OverrideState::Active:
                override_active_ = true;
                recommended_mode_ = resolve_fallback(sensor_flags);
                if (!threshold_exceeded) {
                    state_ = OverrideState::ReleaseHold;
                    state_entry_ms_ = current_time_ms;
                }
                break;

            case OverrideState::ReleaseHold:
                override_active_ = false;
                if (threshold_exceeded) {
                    state_ = OverrideState::Active;
                    state_entry_ms_ = current_time_ms;
                    override_active_ = true;
                } else if ((current_time_ms - state_entry_ms_) >= config_.release_hold_ms) {
                    state_ = OverrideState::Idle;
                }
                break;
        }
    }

    [[nodiscard]] constexpr bool is_override_active() const noexcept { return override_active_; }
    [[nodiscard]] constexpr bool has_triggered_transition() const noexcept { return latched_transition_event_; }
    [[nodiscard]] constexpr OverrideState state() const noexcept { return state_; }
    [[nodiscard]] constexpr FallbackFlightMode recommended_mode() const noexcept { return recommended_mode_; }
    [[nodiscard]] constexpr float current_deflection() const noexcept { return current_max_deflection_; }
    [[nodiscard]] const Config& config() const noexcept { return config_; }
    void set_config(const Config& cfg) noexcept { config_ = cfg; }

private:
    [[nodiscard]] bool evaluate_deflection(const NormalizedChannels& rc) noexcept {
        bool exceeded = false;
        float max_d = 0.0f;

        auto check_axis = [&](ChannelAxis axis, uint32_t mask_bit, float val) {
            if ((config_.channel_mask & mask_bit) != 0) {
                const float abs_v = std::abs(val);
                const float th = config_.channels[static_cast<size_t>(axis)].threshold_norm;
                if (abs_v >= th) {
                    exceeded = true;
                    max_d = std::max(max_d, abs_v);
                }
            }
        };

        check_axis(ChannelAxis::Roll, ChannelMask::Roll, rc.roll);
        check_axis(ChannelAxis::Pitch, ChannelMask::Pitch, rc.pitch);
        check_axis(ChannelAxis::Yaw, ChannelMask::Yaw, rc.yaw);
        check_axis(ChannelAxis::Throttle, ChannelMask::Throttle, rc.throttle);

        if (config_.use_euclidean_norm && ((config_.channel_mask & ChannelMask::RollPitch) == ChannelMask::RollPitch)) {
            const float euclidean_rp = std::sqrt(rc.roll * rc.roll + rc.pitch * rc.pitch);
            if (euclidean_rp >= config_.euclidean_threshold_rp) {
                exceeded = true;
                max_d = std::max(max_d, euclidean_rp);
            }
        }

        current_max_deflection_ = max_d;
        return exceeded;
    }

    [[nodiscard]] static constexpr FallbackFlightMode resolve_fallback(uint32_t sensor_flags) noexcept {
        if ((sensor_flags & SensorFlags::EkfHorizPos) != 0) {
            return FallbackFlightMode::PosHold;
        }
        if ((sensor_flags & SensorFlags::EkfVertPos) != 0) {
            return FallbackFlightMode::AltHold;
        }
        if ((sensor_flags & SensorFlags::AhrsAttitude) != 0) {
            return FallbackFlightMode::Stabilize;
        }
        return FallbackFlightMode::Stabilize;
    }

    Config config_{};
    OverrideState state_{OverrideState::Idle};
    uint32_t state_entry_ms_{0};
    uint32_t last_update_ms_{0};
    float current_max_deflection_{0.0f};
    bool override_active_{false};
    bool latched_transition_event_{false};
    FallbackFlightMode recommended_mode_{FallbackFlightMode::PosHold};
};

} // namespace autopilot::rc_override
