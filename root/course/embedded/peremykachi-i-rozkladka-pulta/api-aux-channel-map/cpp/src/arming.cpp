#include "rc/arming.hpp"

#include <array>

#include "rc/channels.hpp"

namespace rc {
namespace {

struct FlagDesc {
    ArmBlock bit;
    std::string_view name;
    std::string_view reason;
};

constexpr std::array<FlagDesc, 8> kFlags{{
    {ArmBlock::ThrottleNotZero,    "ARM_BLOCK_THROTTLE_NOT_ZERO",  "Throttle above minimum"},
    {ArmBlock::FailsafeActive,     "ARM_BLOCK_FAILSAFE_ACTIVE",    "Failsafe active or RC link lost"},
    {ArmBlock::PrearmNotEngaged,   "ARM_BLOCK_PREARM_NOT_ENGAGED", "Pre-Arm not engaged"},
    {ArmBlock::SwitchActiveAtBoot, "ARM_BLOCK_SWITCH_ACTIVE_BOOT", "Arm switch was on at boot"},
    {ArmBlock::Calibrating,        "ARM_BLOCK_CALIBRATING",        "Gyro or baro calibration in progress"},
    {ArmBlock::TiltAngle,          "ARM_BLOCK_TILT_ANGLE",         "Tilt angle above limit"},
    {ArmBlock::NoCompassLock,      "ARM_BLOCK_NO_COMPASS_LOCK",    "Compass not consistent"},
    {ArmBlock::NoGnssFix,          "ARM_BLOCK_NO_GNSS_FIX",        "Need 3D fix for this mode"},
}};

}  // namespace

ArmingChecker::ArmingChecker(bool armSwitchAtBoot) noexcept
    : bootLatch_{armSwitchAtBoot}
{
    // Тумблер, увімкнений до подачі живлення, ставить засувку: доки пілот
    // не переведе його в Disarm, запуск заборонено.
}

ArmBlock ArmingChecker::evaluate(const VehicleState& state) noexcept
{
    if (bootLatch_ && !state.armSwitch) {
        bootLatch_ = false;  // засувку знімає лише повне повернення в Disarm
    }

    ArmBlock blocks = ArmBlock::None;

    if (state.throttleUs > kArmThrottleMinUs) {
        blocks |= ArmBlock::ThrottleNotZero;
    }
    if (state.failsafeActive) {
        blocks |= ArmBlock::FailsafeActive;
    }
    if (!state.prearmEngaged) {
        blocks |= ArmBlock::PrearmNotEngaged;
    }
    if (bootLatch_) {
        blocks |= ArmBlock::SwitchActiveAtBoot;
    }
    if (state.calibrating) {
        blocks |= ArmBlock::Calibrating;
    }
    if (state.tiltDeg > kArmMaxTiltDeg || state.tiltDeg < -kArmMaxTiltDeg) {
        blocks |= ArmBlock::TiltAngle;
    }
    if (!state.compassHealthy) {
        blocks |= ArmBlock::NoCompassLock;
    }
    if (requiresGnss(state.mode) && (!state.gnssFix3d || state.hdop >= kArmMaxHdop)) {
        blocks |= ArmBlock::NoGnssFix;
    }
    return blocks;
}

bool ArmingChecker::update(const VehicleState& state, ArmBlock& blocks) noexcept
{
    blocks = evaluate(state);

    if (!state.armSwitch) {
        armed_ = false;  // Disarm діє завжди й негайно
        return false;
    }
    if (armed_) {
        // Уже в повітрі: причини запуску не перевіряємо повторно, інакше
        // перший же стрибок HDOP глушив би мотори в польоті.
        return true;
    }
    armed_ = !any(blocks);
    return armed_;
}

std::string_view flagName(ArmBlock singleBit) noexcept
{
    for (const auto& flag : kFlags) {
        if (flag.bit == singleBit) {
            return flag.name;
        }
    }
    return "ARM_BLOCK_UNKNOWN";
}

std::string_view describe(ArmBlock singleBit) noexcept
{
    for (const auto& flag : kFlags) {
        if (flag.bit == singleBit) {
            return flag.reason;
        }
    }
    return "unknown";
}

std::string statusText(ArmBlock blocks)
{
    std::string text;
    for (const auto& flag : kFlags) {
        if (!any(blocks & flag.bit)) {
            continue;
        }
        if (!text.empty()) {
            text += "; ";
        }
        text += "PreArm: ";
        text += flag.reason;
    }
    return text;
}

}  // namespace rc
