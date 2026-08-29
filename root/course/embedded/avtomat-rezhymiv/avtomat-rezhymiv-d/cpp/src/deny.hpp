#pragma once

#include <cstdint>
#include <string>
#include <string_view>

#include "mode.hpp"

namespace fm {

/* Причина відмови — окремий тип, а не «нуль чи не нуль». Разом зі
   std::expected це дає властивість, якої в сішному варіанті немає:
   результат охоронця неможливо мовчки проігнорувати. */
enum class Deny : std::uint8_t {
    InvalidMode,
    Imu,
    Attitude,
    AltEstimate,
    NoGnssFix,
    BadDop,
    EkfInnovation,
    EkfGlitch,
    Compass,
    GuardUnstable,
    NoMission,
    BadMission,
    NoHome,
    GuidedLink,
    ThrottleMismatch,
    FailsafeLock,
    InAir
};

/* Коди MAVLink — справжні значення з протоколу. */
enum class MavResult : std::uint8_t {
    Accepted            = 0,
    TemporarilyRejected = 1,
    Denied              = 2,
    Unsupported         = 3,
    Failed              = 4
};

enum class Severity : std::uint8_t {
    Emergency = 0,
    Alert     = 1,
    Critical  = 2,
    Error     = 3,
    Warning   = 4,
    Notice    = 5,
    Info      = 6
};

inline constexpr std::uint16_t kMavCmdDoSetMode = 176;
inline constexpr std::size_t   kStatusTextLen   = 50;   // поле STATUSTEXT

[[nodiscard]] std::string_view describe(Deny deny) noexcept;

/* Готовий рядок для STATUSTEXT, обрізаний до довжини поля протоколу. */
[[nodiscard]] std::string denyText(Mode target, Deny deny);

/* Минущі перешкоди дістають TemporarilyRejected: станція має право повторити
   запит, коли пілот зведе стік або витримка добіжить. */
[[nodiscard]] constexpr MavResult toMavResult(Deny deny) noexcept
{
    switch (deny) {
    case Deny::InvalidMode:
        return MavResult::Unsupported;
    case Deny::ThrottleMismatch:
    case Deny::GuardUnstable:
    case Deny::GuidedLink:
    case Deny::EkfInnovation:
    case Deny::BadDop:
        return MavResult::TemporarilyRejected;
    default:
        return MavResult::Denied;
    }
}

}  // namespace fm
