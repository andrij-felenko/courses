#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>
#include <chrono>

namespace embedded::control {

using Microseconds = std::chrono::microseconds;
using TimePoint = std::chrono::time_point<std::chrono::steady_clock, Microseconds>;

/**
 * @brief Ідентифікатори джерел керування в порядку спадання авторитету.
 */
enum class SourceId : uint8_t {
    Failsafe = 0,    ///< Аварійний контур безпеки (найвищий авторитет)
    RcPilot = 1,     ///< Ручний пульт пілота (ручне перехоплення)
    Offboard = 2,    ///< Бортовий комп'ютер / AI-планувальник
    GcsMission = 3,  ///< Наземна станція / польотна місія
    None = 255       ///< Жодне джерело не обрано
};

constexpr size_t SourceCount = 4;

/**
 * @brief Стан активності джерела.
 */
enum class SourceState : uint8_t {
    Inactive = 0,
    Active = 1 << 0,
    TimedOut = 1 << 1,
    Preempted = 1 << 2,
    StickActive = 1 << 3
};

inline constexpr SourceState operator|(SourceState a, SourceState b) {
    return static_cast<SourceState>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

inline constexpr bool has_flag(SourceState val, SourceState flag) {
    return (static_cast<uint8_t>(val) & static_cast<uint8_t>(flag)) != 0;
}

/**
 * @brief Типи уставок стабілізації.
 */
enum class SetpointType : uint8_t {
    AttitudeRate,
    AttitudeAngle,
    VelocityNed,
    PositionNed
};

/**
 * @brief Уніфікована уставка керування.
 */
struct Setpoint {
    Microseconds timestamp{0};
    SetpointType type{SetpointType::AttitudeAngle};
    std::array<float, 4> channels{0.0f, 0.0f, 0.0f, 0.0f}; // Roll, Pitch, Yaw, Thrust
    bool valid{false};
};

/**
 * @brief Конфігураційні параметри джерела.
 */
struct SourceConfig {
    Microseconds timeout{std::chrono::milliseconds(500)};
    float stick_deadband{0.08f};
    std::array<float, 4> max_slew_rate{6.0f, 6.0f, 10.0f, 3.0f}; // од/с на канал
    bool allow_stick_override{true};
};

} // namespace embedded::control
