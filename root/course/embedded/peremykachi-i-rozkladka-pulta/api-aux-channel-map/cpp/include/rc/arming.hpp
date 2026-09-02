#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <utility>

#include "rc/switches.hpp"

// Бітова маска причин блокування запуску двигунів (розділ 7)
namespace rc {

enum class ArmBlock : std::uint16_t {
    None               = 0x0000,
    ThrottleNotZero    = 0x0001,
    FailsafeActive     = 0x0002,
    PrearmNotEngaged   = 0x0004,
    SwitchActiveAtBoot = 0x0008,
    Calibrating        = 0x0010,
    TiltAngle          = 0x0020,
    NoCompassLock      = 0x0040,
    NoGnssFix          = 0x0080,
};

[[nodiscard]] constexpr ArmBlock operator|(ArmBlock a, ArmBlock b) noexcept
{
    return static_cast<ArmBlock>(std::to_underlying(a) | std::to_underlying(b));
}
constexpr ArmBlock& operator|=(ArmBlock& a, ArmBlock b) noexcept { return a = a | b; }
[[nodiscard]] constexpr ArmBlock operator&(ArmBlock a, ArmBlock b) noexcept
{
    return static_cast<ArmBlock>(std::to_underlying(a) & std::to_underlying(b));
}
[[nodiscard]] constexpr bool any(ArmBlock f) noexcept { return std::to_underlying(f) != 0; }

inline constexpr std::uint16_t kArmThrottleMinUs = 1050;  // вище — газ піднято
inline constexpr float kArmMaxTiltDeg = 25.0f;
inline constexpr float kArmMaxHdop    = 1.5f;

struct VehicleState {
    std::uint16_t throttleUs{kUsMin};  // газ ПІСЛЯ застосування розкладки
    bool  failsafeActive{false};
    bool  prearmEngaged{false};
    bool  armSwitch{false};
    bool  calibrating{false};
    float tiltDeg{0.0f};
    bool  compassHealthy{true};
    bool  gnssFix3d{false};
    float hdop{99.0f};
    FlightMode mode{FlightMode::Stabilize};
};

class ArmingChecker {
public:
    explicit ArmingChecker(bool armSwitchAtBoot) noexcept;

    [[nodiscard]] ArmBlock evaluate(const VehicleState& state) noexcept;
    bool update(const VehicleState& state, ArmBlock& blocks) noexcept;  // повертає armed
    [[nodiscard]] bool armed() const noexcept { return armed_; }

private:
    bool bootLatch_;
    bool armed_{false};
};

[[nodiscard]] std::string_view describe(ArmBlock singleBit) noexcept;
[[nodiscard]] std::string_view flagName(ArmBlock singleBit) noexcept;
[[nodiscard]] std::string statusText(ArmBlock blocks);  // рядок у стилі STATUSTEXT

}  // namespace rc
