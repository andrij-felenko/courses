// FlightModeFSM.hpp
#pragma once
#include <cstdint>
#include <string_view>
#include <optional>
#include <array>

namespace autopilot {

enum class FlightModeId : uint8_t {
    Manual = 0,
    Acro,
    Stabilize,
    AltHold,
    PosHold,
    Auto,
    FailsafeLand
};

enum class SensorFlag : uint32_t {
    ImuHealthy   = 1 << 0,
    AhrsValid    = 1 << 1,
    BaroHealthy  = 1 << 2,
    EkfVertOk    = 1 << 3,
    EkfHorizOk   = 1 << 4,
    Gps3DFix     = 1 << 5,
    HomeSet      = 1 << 6
};

inline constexpr uint32_t operator|(SensorFlag a, SensorFlag b) noexcept {
    return static_cast<uint32_t>(a) | static_cast<uint32_t>(b);
}

struct FlightContext {
    uint32_t sensor_flags{0};
    float current_alt_m{0.0f};
    std::array<float, 3> current_pos_ned{0.0f, 0.0f, 0.0f};
    float current_yaw_rad{0.0f};
    float estimated_hover_thrust{0.45f};

    // Вихідні уставки для внутрішніх регуляторів
    float target_alt_m{0.0f};
    std::array<float, 3> target_pos_ned{0.0f, 0.0f, 0.0f};
    float target_yaw_rad{0.0f};
    float target_thrust{0.0f};
    bool reset_rate_integrators{false};

    [[nodiscard]] constexpr bool has_sensors(uint32_t mask) const noexcept {
        return (sensor_flags & mask) == mask;
    }
};

// Абстрактний базовий клас режиму
class FlightModeBase {
public:
    virtual ~FlightModeBase() = default;
    [[nodiscard]] virtual FlightModeId id() const noexcept = 0;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual uint32_t required_sensors() const noexcept = 0;

    virtual bool on_enter(FlightContext& ctx) = 0;
    virtual void on_update(FlightContext& ctx, float dt) = 0;
    virtual void on_exit(FlightContext& ctx) = 0;
};

// Режим стабілізації кута
class StabilizeMode final : public FlightModeBase {
public:
    [[nodiscard]] FlightModeId id() const noexcept override { return FlightModeId::Stabilize; }
    [[nodiscard]] std::string_view name() const noexcept override { return "STABILIZE"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuHealthy | SensorFlag::AhrsValid;
    }

    bool on_enter(FlightContext& ctx) override {
        ctx.reset_rate_integrators = true;
        return true;
    }

    void on_update(FlightContext& ctx, float dt) override {
        (void)ctx; (void)dt;
        // Розрахунок кутових уставок
    }

    void on_exit(FlightContext& ctx) override {
        (void)ctx;
    }
};

// Режим утримання висоти з безвузловою передачею (Bumpless Transfer)
class AltHoldMode final : public FlightModeBase {
public:
    [[nodiscard]] FlightModeId id() const noexcept override { return FlightModeId::AltHold; }
    [[nodiscard]] std::string_view name() const noexcept override { return "ALT_HOLD"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuHealthy | SensorFlag::AhrsValid | 
               SensorFlag::BaroHealthy | SensorFlag::EkfVertOk;
    }

    bool on_enter(FlightContext& ctx) override {
        ctx.target_alt_m = ctx.current_alt_m;            // Захоплення поточної висоти
        ctx.target_thrust = ctx.estimated_hover_thrust;  // Предзавантаження інтегратора тяги
        ctx.reset_rate_integrators = true;
        return true;
    }

    void on_update(FlightContext& ctx, float dt) override {
        (void)ctx; (void)dt;
        // Каскад керування висотою
    }

    void on_exit(FlightContext& ctx) override {
        (void)ctx;
    }
};

// Менеджер ієрархічного автомату режимів
class FlightModeManager {
public:
    explicit FlightModeManager(FlightContext& ctx) noexcept : ctx_(ctx) {
        current_mode_ = &stabilize_mode_;
        current_mode_->on_enter(ctx_);
    }

    bool request_mode(FlightModeId mode_id) {
        FlightModeBase* target = find_mode(mode_id);
        if (!target) return false;

        // Перевірка Guard-умов доступності сенсорів
        if (!ctx_.has_sensors(target->required_sensors())) {
            return false;
        }

        current_mode_->on_exit(ctx_);
        if (!target->on_enter(ctx_)) {
            // Безпечний відкат у режим стабілізації
            current_mode_ = &stabilize_mode_;
            current_mode_->on_enter(ctx_);
            return false;
        }

        current_mode_ = target;
        return true;
    }

    void update(float dt) {
        // Перевірка втрати сенсорів на льоту (каскадна деградація)
        if (!ctx_.has_sensors(current_mode_->required_sensors())) {
            handle_sensor_loss_degradation();
        }
        current_mode_->on_update(ctx_, dt);
    }

    [[nodiscard]] FlightModeId current_mode_id() const noexcept {
        return current_mode_->id();
    }

private:
    void handle_sensor_loss_degradation() {
        if (current_mode_->id() == FlightModeId::AltHold) {
            // Втрата барометра -> деградація в Stabilize
            (void)request_mode(FlightModeId::Stabilize);
        }
    }

    FlightModeBase* find_mode(FlightModeId id) noexcept {
        if (id == FlightModeId::Stabilize) return &stabilize_mode_;
        if (id == FlightModeId::AltHold) return &alt_hold_mode_;
        return nullptr;
    }

    FlightContext& ctx_;
    StabilizeMode stabilize_mode_{};
    AltHoldMode alt_hold_mode_{};
    FlightModeBase* current_mode_{nullptr};
};

} // namespace autopilot
