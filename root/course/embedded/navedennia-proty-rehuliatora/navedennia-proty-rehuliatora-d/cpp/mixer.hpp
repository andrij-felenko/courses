#pragma once

// Мікшер квадрокоптера в схемі X — і єдине місце, де народжується
// прапорець насичення актуаторів, без якого анти-вінд-ап неможливий.

#include <algorithm>
#include <array>
#include <span>

#include "geometry.hpp"

namespace flight {

inline constexpr std::size_t kMotorCount = 4;
inline constexpr float kMotorIdle = 0.05F;

// Внесок tx, ty, tz у кожен мотор. Порядок: 0 — передній правий,
// 1 — задній лівий, 2 — передній лівий, 3 — задній правий.
inline constexpr std::array<Vec3, kMotorCount> kMixMatrix{
    Vec3{-1.0F, +1.0F, +1.0F},
    Vec3{+1.0F, -1.0F, +1.0F},
    Vec3{+1.0F, +1.0F, -1.0F},
    Vec3{-1.0F, -1.0F, -1.0F},
};

struct MotorOutputs {
    std::array<float, kMotorCount> motors{};
    bool saturated{false};
};

[[nodiscard]] inline MotorOutputs mixQuadX(const Vec3& torque, float thrust) noexcept {
    MotorOutputs out{};
    std::array<float, kMotorCount> mix{};

    for (std::size_t i = 0; i < kMotorCount; ++i) {
        mix[i] = dot(kMixMatrix[i], torque);
    }

    auto [lo, hi] = std::ranges::minmax(mix);

    // Розмах моментів ширший за весь діапазон ШІМ — момент не вміщується взагалі.
    // Ріжемо його пропорційно: краще менший, але неспотворений момент.
    if (const float span = hi - lo; span > 1.0F) {
        const float gain = 1.0F / span;
        for (float& m : mix) {
            m *= gain;
        }
        lo *= gain;
        hi *= gain;
        out.saturated = true;
    }

    // Зсуваємо колективний газ так, щоб момент дійшов до рами цілим.
    // Момент важливіший за тягу: втрата висоти — це метри, втрата моменту — падіння.
    const float adjusted = std::clamp(thrust, -lo, 1.0F - hi);
    if (adjusted != thrust) {
        out.saturated = true;
    }

    for (std::size_t i = 0; i < kMotorCount; ++i) {
        out.motors[i] = std::clamp(adjusted + mix[i], kMotorIdle, 1.0F);
    }
    return out;
}

struct Wrench {
    Vec3 torque{};
    float thrust{0.0F};
};

// Зворотне перетворення команд у момент і тягу: що НАСПРАВДІ дісталося рамі.
[[nodiscard]] inline Wrench motorsToWrench(std::span<const float, kMotorCount> motors) noexcept {
    Wrench w{};
    for (std::size_t i = 0; i < kMotorCount; ++i) {
        w.torque += kMixMatrix[i] * motors[i];
        w.thrust += motors[i];
    }
    w.torque = w.torque * 0.25F;
    w.thrust *= 0.25F;
    return w;
}

}  // namespace flight
