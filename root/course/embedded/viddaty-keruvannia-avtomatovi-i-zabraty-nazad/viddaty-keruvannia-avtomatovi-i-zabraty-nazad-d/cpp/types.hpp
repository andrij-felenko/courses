#pragma once

#include <chrono>

// Спільні типи керівного тракту. Час скрізь типізований: у польотному циклі
// плутанина «секунди чи мілісекунди» коштує дорожче за будь-який шаблон.

namespace fc {

using Seconds = std::chrono::duration<float>;

inline constexpr float kDeg2Rad = 0.01745329f;
inline constexpr float kRad2Deg = 57.2957795f;

struct ControlCommand {
    float roll{};     // градуси, + = правий крен
    float pitch{};    // градуси, + = кабрування
    float yaw{};      // градуси/с
    float throttle{}; // 0.0 ... 1.0
};

struct VehicleState {
    float x{};           // м, уздовж початкового курсу
    float y{};           // м, вліво від нього
    float alt{};         // м
    float heading_deg{}; // курс (напрямок носа)
    float airspeed{};    // м/с
};

// Зведення кута до діапазону -180…+180.
constexpr float wrap180(float deg) noexcept {
    while (deg > 180.0f) deg -= 360.0f;
    while (deg < -180.0f) deg += 360.0f;
    return deg;
}

} // namespace fc
