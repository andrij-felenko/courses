#pragma once

#include <cstdint>
#include <expected>
#include <optional>

#include "blackbox.hpp"

namespace safety {

// Фізичні інваріанти апарата: межі заліза, а не налаштування місії.
namespace limits {
inline constexpr float   kSafetyMarginM{0.35f};      // геометричний буфер до перешкоди, м
inline constexpr float   kMaxBrakeAccel{3.0f};       // що реально дають гальма, м/с²
inline constexpr float   kMaxAccel{1.5f};            // стеля розгону при повній батареї, м/с²
inline constexpr float   kLatencyPadSec{0.04f};      // затримка тракту: давач + утримання + ESC
inline constexpr float   kMaxSpeedMps{2.5f};         // стеля лінійної швидкості, м/с
inline constexpr float   kMaxYawRateRadps{1.8f};     // стеля рискання, рад/с
inline constexpr float   kCriticalVoltageV{13.8f};   // нижче — ризик скидання МК
inline constexpr float   kNominalVoltageV{16.0f};    // повна батарея, В
inline constexpr Seconds kWatchdogMaxAge{0.100f};    // скільки терпимо мовчання планувальника
inline constexpr Seconds kSensorHoldMax{0.050f};     // скільки терпимо числення замість виміру
inline constexpr float   kTiltWarnFraction{0.8f};    // із якої частки крену починаємо тиснути
} // namespace limits

struct Command {
    float vx{0.0f};       // лінійна швидкість уперед, м/с
    float vy{0.0f};       // бічна швидкість, м/с (для ровера завжди 0)
    float yaw_rate{0.0f}; // кутова швидкість рискання, рад/с
};

// Порожній optional — давач не дав достовірного виміру (шина, CRC, діапазон).
// Прапорця «valid» поруч зі значенням тут не треба: тип сам не дає прочитати сміття.
struct Sensors {
    std::optional<float> obstacle_dist_m{};
    std::optional<float> battery_voltage{};
    float tilt_rad{0.0f};
    float tilt_limit_rad{0.52f};
    bool  emergency_stop{false};
};

// Помилка виклику, а не стан машини: аварійні режими — це Status, не Fault.
enum class Fault : std::uint8_t {
    InvalidTimeStep, // такт нечисловий або недодатний
    NonFiniteCommand // у пакеті уставки NaN або нескінченність
};

struct Outcome {
    Command cmd{};
    Status  status{Status::PassThrough};
    Reason  reason{Reason::None};
};

class Supervisor {
public:
    using Log = BlackBox<48>;

    // Повільний потік: планувальник приніс уставку. Хибний пакет не оновлює
    // позначку свіжості — сторож рано чи пізно забере керування.
    std::expected<void, Fault> submit_plan(const Command& cmd) noexcept;

    // Один такт швидкого циклу: O(1), без динамічної памʼяті, без блокувань.
    std::expected<Outcome, Fault> step(const Sensors& sensors, Seconds dt) noexcept;

    [[nodiscard]] const Command& held_plan() const noexcept { return candidate_; }
    [[nodiscard]] const Log& log() const noexcept { return log_; }

private:
    Outcome engage_brake(Seconds dt, Reason reason, float value) noexcept;
    float   update_distance_estimate(const std::optional<float>& measured, Seconds dt) noexcept;

    Command candidate_{};
    Seconds uptime_{};
    Seconds plan_age_{};      // скільки минуло від останньої придатної уставки
    Seconds blind_for_{limits::kSensorHoldMax}; // до першого виміру простір вважаємо зайнятим
    float   last_out_vx_{0.0f};
    float   dr_dist_m_{0.0f}; // оцінка дистанції за інерціальним численням, м
    bool    dist_trusted_{false};
    Log     log_{};
};

} // namespace safety
