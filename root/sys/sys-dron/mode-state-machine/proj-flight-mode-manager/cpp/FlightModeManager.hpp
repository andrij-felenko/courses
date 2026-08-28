// ============================================================================
// FlightModeManager.hpp (Реалізація на C++20)
// ============================================================================
#pragma once
#include <cstdint>
#include <string_view>
#include <array>
#include <expected>

namespace sys_dron::fmm {

enum class FlightMode : uint8_t {
    Manual = 0,
    Acro,
    Stabilize,
    AltHold,
    PosHold,
    Auto,
    Rtl,
    FailsafeLand,
    Count
};

enum class CommandSource : uint8_t {
    Offboard = 0,
    Navigator,
    GcsCommand,
    RcSwitch,
    StickOverride,
    Failsafe
};

enum class TransitionError : uint8_t {
    LowerPriorityThanActive,
    MissingRequiredSensors,
    InitializationFailed,
    InvalidMode
};

enum class SensorFlag : uint32_t {
    ImuOk        = 1 << 0,
    AhrsOk       = 1 << 1,
    BaroOk       = 1 << 2,
    EkfZOk       = 1 << 3,
    EkfXyOk      = 1 << 4,
    Gps3DFix     = 1 << 5,
    HomeValid    = 1 << 6,
    MissionValid = 1 << 7
};

inline constexpr uint32_t operator|(SensorFlag a, SensorFlag b) noexcept {
    return static_cast<uint32_t>(a) | static_cast<uint32_t>(b);
}

struct FlightContext {
    uint32_t sensor_flags{0};
    bool is_armed{false};
    bool is_flying{false};

    float current_alt_m{0.0f};
    std::array<float, 3> current_vel_ned{0.0f, 0.0f, 0.0f};
    std::array<float, 3> current_pos_ned{0.0f, 0.0f, 0.0f};
    float current_yaw_rad{0.0f};
    float estimated_hover_thrust{0.45f};

    // Сетопоінти
    float target_alt_m{0.0f};
    std::array<float, 3> target_vel_ned{0.0f, 0.0f, 0.0f};
    std::array<float, 3> target_pos_ned{0.0f, 0.0f, 0.0f};
    float target_yaw_rad{0.0f};
    float target_thrust{0.0f};
    bool reset_pid_integrators{false};

    [[nodiscard]] constexpr bool has_sensors(uint32_t mask) const noexcept {
        return (sensor_flags & mask) == mask;
    }
};

class ModeBase {
public:
    virtual ~ModeBase() = default;
    [[nodiscard]] virtual FlightMode id() const noexcept = 0;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual uint32_t required_sensors() const noexcept = 0;

    virtual bool on_enter(FlightContext& ctx) = 0;
    virtual void on_update(FlightContext& ctx, float dt) = 0;
    virtual void on_exit(FlightContext& ctx) = 0;
};

class StabilizeMode final : public ModeBase {
public:
    [[nodiscard]] FlightMode id() const noexcept override { return FlightMode::Stabilize; }
    [[nodiscard]] std::string_view name() const noexcept override { return "STABILIZE"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuOk | SensorFlag::AhrsOk;
    }
    bool on_enter(FlightContext& ctx) override {
        ctx.reset_pid_integrators = true;
        return true;
    }
    void on_update(FlightContext&, float) override {}
    void on_exit(FlightContext&) override {}
};

class AltHoldMode final : public ModeBase {
public:
    [[nodiscard]] FlightMode id() const noexcept override { return FlightMode::AltHold; }
    [[nodiscard]] std::string_view name() const noexcept override { return "ALT_HOLD"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuOk | SensorFlag::AhrsOk | SensorFlag::BaroOk | SensorFlag::EkfZOk;
    }
    bool on_enter(FlightContext& ctx) override {
        ctx.target_alt_m = ctx.current_alt_m;
        ctx.target_vel_ned[2] = 0.0f;
        ctx.target_thrust = ctx.estimated_hover_thrust;
        ctx.reset_pid_integrators = true;
        return true;
    }
    void on_update(FlightContext&, float) override {}
    void on_exit(FlightContext&) override {}
};

class PosHoldMode final : public ModeBase {
public:
    [[nodiscard]] FlightMode id() const noexcept override { return FlightMode::PosHold; }
    [[nodiscard]] std::string_view name() const noexcept override { return "POS_HOLD"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuOk | SensorFlag::AhrsOk | SensorFlag::BaroOk | 
               SensorFlag::EkfZOk | SensorFlag::EkfXyOk | SensorFlag::Gps3DFix;
    }
    bool on_enter(FlightContext& ctx) override {
        ctx.target_alt_m = ctx.current_alt_m;
        ctx.target_pos_ned = ctx.current_pos_ned;
        ctx.target_vel_ned = {0.0f, 0.0f, 0.0f};
        ctx.target_yaw_rad = ctx.current_yaw_rad;
        ctx.target_thrust = ctx.estimated_hover_thrust;
        ctx.reset_pid_integrators = true;
        return true;
    }
    void on_update(FlightContext&, float) override {}
    void on_exit(FlightContext&) override {}
};

class AutoMode final : public ModeBase {
public:
    [[nodiscard]] FlightMode id() const noexcept override { return FlightMode::Auto; }
    [[nodiscard]] std::string_view name() const noexcept override { return "AUTO"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuOk | SensorFlag::AhrsOk | SensorFlag::BaroOk | 
               SensorFlag::EkfZOk | SensorFlag::EkfXyOk | SensorFlag::Gps3DFix | 
               SensorFlag::MissionValid;
    }
    bool on_enter(FlightContext& ctx) override {
        ctx.reset_pid_integrators = true;
        return true;
    }
    void on_update(FlightContext&, float) override {}
    void on_exit(FlightContext&) override {}
};

class FlightModeManager {
public:
    explicit FlightModeManager(FlightContext& ctx) noexcept : ctx_(ctx) {
        current_mode_ = &stabilize_mode_;
        current_mode_->on_enter(ctx_);
    }

    std::expected<void, TransitionError> request_mode(FlightMode mode, CommandSource source) {
        ModeBase* target = resolve_mode(mode);
        if (!target) return std::unexpected(TransitionError::InvalidMode);

        if (source < current_source_ && current_source_ == CommandSource::Failsafe) {
            return std::unexpected(TransitionError::LowerPriorityThanActive);
        }

        if (!ctx_.has_sensors(target->required_sensors())) {
            return std::unexpected(TransitionError::MissingRequiredSensors);
        }

        current_mode_->on_exit(ctx_);
        if (!target->on_enter(ctx_)) {
            current_mode_ = &stabilize_mode_;
            current_source_ = CommandSource::Failsafe;
            current_mode_->on_enter(ctx_);
            return std::unexpected(TransitionError::InitializationFailed);
        }

        current_mode_ = target;
        current_source_ = source;
        return {};
    }

    void update(float dt) {
        handle_sensor_loss();
        current_mode_->on_update(ctx_, dt);
    }

    void handle_stick_override(float stick_deflection) {
        if (stick_deflection < 0.15f) return;
        if (current_mode_->id() == FlightMode::Auto) {
            if (ctx_.has_sensors(pos_hold_mode_.required_sensors())) {
                (void)request_mode(FlightMode::PosHold, CommandSource::StickOverride);
            } else {
                (void)request_mode(FlightMode::AltHold, CommandSource::StickOverride);
            }
        }
    }

    [[nodiscard]] FlightMode current_mode_id() const noexcept {
        return current_mode_->id();
    }

private:
    void handle_sensor_loss() {
        if (!ctx_.has_sensors(current_mode_->required_sensors())) {
            if (current_mode_->id() == FlightMode::Auto || current_mode_->id() == FlightMode::PosHold) {
                if (ctx_.has_sensors(alt_hold_mode_.required_sensors())) {
                    (void)request_mode(FlightMode::AltHold, CommandSource::Failsafe);
                } else {
                    (void)request_mode(FlightMode::Stabilize, CommandSource::Failsafe);
                }
            } else if (current_mode_->id() == FlightMode::AltHold) {
                (void)request_mode(FlightMode::Stabilize, CommandSource::Failsafe);
            }
        }
    }

    ModeBase* resolve_mode(FlightMode mode) noexcept {
        switch (mode) {
            case FlightMode::Stabilize: return &stabilize_mode_;
            case FlightMode::AltHold:   return &alt_hold_mode_;
            case FlightMode::PosHold:   return &pos_hold_mode_;
            case FlightMode::Auto:      return &auto_mode_;
            default:                    return nullptr;
        }
    }

    FlightContext& ctx_;
    StabilizeMode stabilize_mode_{};
    AltHoldMode alt_hold_mode_{};
    PosHoldMode pos_hold_mode_{};
    AutoMode auto_mode_{};

    ModeBase* current_mode_{&stabilize_mode_};
    CommandSource current_source_{CommandSource::RcSwitch};
};

} // namespace sys_dron::fmm
