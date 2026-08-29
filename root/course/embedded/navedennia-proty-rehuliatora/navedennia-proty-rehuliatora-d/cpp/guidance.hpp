#pragma once

#include "geometry.hpp"
#include "setpoint.hpp"

namespace flight {

// Зовнішній контур: 20–50 Гц, повільна навігаційна картина світу.
class Guidance {
public:
    struct NavState {
        Vec3 position{};   // NED, м (вісь Z вниз)
        Vec3 velocity{};   // м/с
        float yaw{0.0F};   // рад
    };

    [[nodiscard]] Setpoint step(const NavState& nav,
                                const Vec3& targetPosition,
                                float yawSetpoint,
                                float dt,
                                bool actuatorsSaturated,
                                Micros now) noexcept;

    void reset() noexcept {
        velIntegral_ = Vec3{};
        previousTarget_.reset();
    }

private:
    static constexpr float kMaxThrustAccel = 2.0F * kGravity;  // тягоозброєність 2:1
    static constexpr float kKpPosition = 1.0F;
    static constexpr float kMaxSpeed = 5.0F;
    static constexpr float kKpVelocity = 2.2F;
    static constexpr float kKiVelocity = 0.7F;
    static constexpr float kMaxIntegral = 3.0F;
    static constexpr float kMaxAccelXY = 6.0F;
    static constexpr float kMaxAccelZ = 5.0F;
    static constexpr float kMaxTilt = 0.610865F;   // 35 градусів
    static constexpr float kMaxSlewRate = kPi;     // 180 град/с
    static constexpr float kMinThrust = 0.05F;

    Vec3 velIntegral_{};
    // Порожній optional чесніше за прапорець "ще не ініціалізовано".
    std::optional<Quat> previousTarget_{};
};

}  // namespace flight
