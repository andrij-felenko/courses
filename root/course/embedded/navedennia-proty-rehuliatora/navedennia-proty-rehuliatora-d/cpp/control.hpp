#pragma once

#include <optional>

#include "geometry.hpp"
#include "setpoint.hpp"

namespace flight {

// Внутрішній контур: 500–1000 Гц, зазвичай із переривання Data Ready гіроскопа.
// Знає лише зв'язану систему координат — і нічого про світ навколо.
class AttitudeController {
public:
    struct ImuSample {
        Quat attitude{};   // оцінка орієнтації з комплексування давачів
        Vec3 gyro{};       // рад/с, зв'язана система
    };

    struct Command {
        Vec3 torque{};            // нормовані моменти -1..1
        float thrust{0.0F};       // 0..1
        bool fallback{false};     // уставка протухла — тримаємо горизонт
    };

    [[nodiscard]] Command update(const ImuSample& imu,
                                 const std::optional<Setpoint>& incoming,
                                 bool actuatorsSaturated,
                                 float dt,
                                 Micros now) noexcept;

private:
    static constexpr Micros kSetpointTimeout{100'000};   // 100 мс
    static constexpr float kLandingThrust = 0.35F;
    static constexpr float kLandingRampPerSecond = 0.60F;

    static constexpr float kKpAttitude = 6.5F;
    static constexpr float kKpAttitudeYaw = kKpAttitude * 0.6F;
    static constexpr float kMaxRateXY = 4.0F;   // рад/с
    static constexpr float kMaxRateZ = 2.0F;

    static constexpr float kKpRate = 0.15F;
    static constexpr float kKiRate = 0.25F;
    static constexpr float kKdRate = 0.0035F;
    static constexpr float kMaxRateIntegral = 0.30F;
    static constexpr float kDerivativeCutoffHz = 60.0F;

    Vec3 rateIntegral_{};
    Vec3 previousGyro_{};
    Vec3 filteredDerivative_{};
    std::optional<Setpoint> lastGood_{};
    float thrustCommand_{0.0F};
};

}  // namespace flight
