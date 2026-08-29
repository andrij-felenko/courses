#include "deny.hpp"

#include <format>

namespace fm {

std::string_view describe(Deny deny) noexcept
{
    switch (deny) {
    case Deny::InvalidMode:      return "unknown mode id";
    case Deny::Imu:              return "requires healthy gyro";
    case Deny::Attitude:         return "requires attitude estimate";
    case Deny::AltEstimate:      return "requires altitude estimate";
    case Deny::NoGnssFix:        return "requires 3D Fix & HDOP < 1.5";
    case Deny::BadDop:           return "requires 3D Fix & HDOP < 1.5";
    case Deny::EkfInnovation:    return "requires EKF innovations in gate";
    case Deny::EkfGlitch:        return "blocked by EKF variance glitch";
    case Deny::Compass:          return "requires healthy compass heading";
    case Deny::GuardUnstable:    return "guard not stable yet";
    case Deny::NoMission:        return "requires loaded mission";
    case Deny::BadMission:       return "mission failed validation";
    case Deny::NoHome:           return "requires Home position";
    case Deny::GuidedLink:       return "requires live setpoint stream";
    case Deny::ThrottleMismatch: return "match throttle stick first";
    case Deny::FailsafeLock:     return "blocked by active failsafe";
    case Deny::InAir:            return "not allowed while airborne";
    }
    return "denied";
}

std::string denyText(Mode target, Deny deny)
{
    std::string text = std::format("Mode change failed: {} {}", name(target), describe(deny));

    if (text.size() > kStatusTextLen) {
        text.resize(kStatusTextLen);   // довше поле протокол однаково відкине
    }
    return text;
}

}  // namespace fm
