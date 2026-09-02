#include "arbiter.hpp"

#include <algorithm>
#include <cmath>
#include <cstdlib>

namespace manual_control {
namespace {

// Мітка «нескінченно давно» для каналу, з якого не прийшло ще жодного кадру.
constexpr Millis kNeverAge = Millis{1'000'000};

[[nodiscard]] Millis ageOf(bool seen, Millis now, Millis stamp) noexcept
{
    return seen ? (now - stamp) : kNeverAge;
}

[[nodiscard]] std::int16_t clampAxis(std::int32_t v, std::int32_t lo, std::int32_t hi) noexcept
{
    return static_cast<std::int16_t>(std::clamp(v, lo, hi));
}

}  // namespace

bool Axes::deflected() const noexcept
{
    return std::abs(static_cast<int>(roll)) > kRcDeadband ||
           std::abs(static_cast<int>(pitch)) > kRcDeadband ||
           std::abs(static_cast<int>(yaw)) > kRcDeadband ||
           throttle > kRcThrottleDeadband;
}

std::int16_t SlewLimiter::step(std::int16_t target, Seconds dt) noexcept
{
    const float maxDelta = kAxisSlewPerSec * dt.count();
    const float diff     = static_cast<float>(target) - value_;
    value_ += std::clamp(diff, -maxDelta, maxDelta);
    return static_cast<std::int16_t>(std::lround(value_));
}

void Arbiter::latchOutput(const Axes& axes) noexcept
{
    out_ = axes;
    slewRoll_.reset(axes.roll);
    slewPitch_.reset(axes.pitch);
    slewYaw_.reset(axes.yaw);
    slewThrottle_.reset(axes.throttle);
}

void Arbiter::driveTo(const Axes& target, Seconds dt) noexcept
{
    out_.roll     = slewRoll_.step(target.roll, dt);
    out_.pitch    = slewPitch_.step(target.pitch, dt);
    out_.yaw      = slewYaw_.step(target.yaw, dt);
    out_.throttle = slewThrottle_.step(target.throttle, dt);
    out_.buttons  = target.buttons;
}

void Arbiter::feedRc(const Axes& rc, Millis now) noexcept
{
    rc_         = rc;
    lastRc_     = now;
    rcSeen_     = true;
    rcLinkLost_ = false;
}

void Arbiter::feedManualControl(std::int16_t x, std::int16_t y, std::int16_t z,
                                std::int16_t r, std::uint16_t buttons, Millis now) noexcept
{
    // Межі полів — зі специфікації MANUAL_CONTROL; z тримаємо в [0..1000],
    // бо саме так QGC шле тягу мультикоптера.
    gcs_.pitch    = clampAxis(x, -1000, 1000);
    gcs_.roll     = clampAxis(y, -1000, 1000);
    gcs_.throttle = clampAxis(z, 0, 1000);
    gcs_.yaw      = clampAxis(r, -1000, 1000);
    gcs_.buttons  = buttons;
    lastGcs_      = now;
    gcsSeen_      = true;
}

ArmVerdict Arbiter::requestArm(bool arm, bool confirmed, Millis now) noexcept
{
    if (!arm) {
        // Роззброєння — аварійна зупинка, умов не має.
        armed_    = false;
        failsafe_ = FailsafeAction::None;
        state_    = State::Disarmed;
        latchOutput(Axes{});
        return ArmVerdict::Disarmed;
    }

    if (armed_)
        return ArmVerdict::Accepted;
    if (failsafe_ != FailsafeAction::None)
        return ArmVerdict::InFailsafe;

    // Армитися «наосліп» — коли команда пройшла, а потік осей ні — не можна.
    const Millis gcsAge = ageOf(gcsSeen_, now, lastGcs_);
    const Millis rcAge  = ageOf(rcSeen_, now, lastRc_);
    if (gcsAge > kGcsDegrade && rcAge > kRcLinkTimeout)
        return ArmVerdict::NoLink;

    if ((gcsSeen_ && gcs_.deflected()) || (!rcLinkLost_ && rc_.deflected()))
        return ArmVerdict::StickNotNeutral;

    if (!confirmed)
        return ArmVerdict::NeedsConfirmation;

    armed_ = true;
    latchOutput(Axes{});
    state_ = State::GcsActive;
    return ArmVerdict::Accepted;
}

void Arbiter::update(Millis now, Seconds dt) noexcept
{
    const Millis rcAge  = ageOf(rcSeen_, now, lastRc_);
    const Millis gcsAge = ageOf(gcsSeen_, now, lastGcs_);

    rcLinkLost_ = rcAge > kRcLinkTimeout;

    if (!armed_) {
        state_    = State::Disarmed;
        failsafe_ = FailsafeAction::None;
        latchOutput(Axes{});
        return;
    }

    // Бар'єр 1. Пілот безпеки відхилив стік — станція відключається тієї ж
    // ітерації, без лімітера: миттєвість реакції пульта тут і є вся суть.
    if (!rcLinkLost_ && rc_.deflected()) {
        if (state_ != State::RcActive)
            ++counters_.preemptions;
        state_    = State::RcActive;
        failsafe_ = FailsafeAction::None;  // пілот перебрав керування
        latchOutput(rc_);
        return;
    }

    const Axes neutralHover{.roll = 0, .pitch = 0, .throttle = kHoverThrottle, .yaw = 0, .buttons = 0};

    // Розпочату аварійну процедуру свіжі пакети станції не скасовують:
    // її знімає перехоплення пультом або дизарм.
    if (failsafe_ != FailsafeAction::None) {
        state_ = State::Failsafe;
        driveTo(neutralHover, dt);
        return;
    }

    if (gcsAge < kGcsDegrade) {
        // Бар'єр 3: пачка затриманих пакетів лягає на осі похилою, не сходинкою.
        state_ = State::GcsActive;
        driveTo(gcs_, dt);
        return;
    }

    if (gcsAge < kGcsFailsafe) {
        // Бар'єр 2, перший поріг: кути в нуль, тяга на зависання.
        if (state_ != State::GcsDegraded)
            ++counters_.degradations;
        state_ = State::GcsDegraded;
        driveTo(neutralHover, dt);
        return;
    }

    // Бар'єр 2, другий поріг. Тяга лишається на зависанні: керування забирає
    // автономний режим, а нуль на тязі означав би падіння з висоти.
    state_    = State::Failsafe;
    failsafe_ = homeValid_ ? FailsafeAction::ReturnToLaunch : FailsafeAction::Land;
    ++counters_.failsafes;
    driveTo(neutralHover, dt);
}

std::string_view toString(State s) noexcept
{
    switch (s) {
    case State::Disarmed:    return "DISARMED";
    case State::RcActive:    return "RC_ACTIVE";
    case State::GcsActive:   return "GCS_ACTIVE";
    case State::GcsDegraded: return "GCS_DEGRADED";
    case State::Failsafe:    return "FAILSAFE";
    }
    return "?";
}

std::string_view toString(FailsafeAction f) noexcept
{
    switch (f) {
    case FailsafeAction::None:           return "-";
    case FailsafeAction::ReturnToLaunch: return "RTL";
    case FailsafeAction::Land:           return "LAND";
    }
    return "?";
}

std::string_view toString(ArmVerdict v) noexcept
{
    switch (v) {
    case ArmVerdict::Accepted:          return "ACCEPTED";
    case ArmVerdict::NeedsConfirmation: return "NEEDS_CONFIRMATION";
    case ArmVerdict::NoLink:            return "NO_LINK";
    case ArmVerdict::StickNotNeutral:   return "STICK_NOT_NEUTRAL";
    case ArmVerdict::InFailsafe:        return "IN_FAILSAFE";
    case ArmVerdict::Disarmed:          return "DISARMED";
    }
    return "?";
}

}  // namespace manual_control
