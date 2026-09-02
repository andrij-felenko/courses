#include "controller.hpp"

#include <algorithm>
#include <cmath>

namespace cart {

std::string_view describe(State s) noexcept {
    switch (s) {
    case State::Online:           return "ONLINE";
    case State::HoldPhase1:       return "HOLD (фаза 1)";
    case State::AutonomousPhase2: return "AUTONOMOUS (фаза 2)";
    case State::SafeStatePhase3:  return "SAFE STATE (фаза 3)";
    case State::Reconnecting:     return "RECONNECTING";
    }
    return "?";
}

std::string_view event::describe(std::uint8_t code) noexcept {
    switch (code) {
    case kLinkLost:      return "зв'язок зник";
    case kPhase2:        return "перехід у фазу 2";
    case kSafeState:     return "безпечний стан";
    case kDeadReckoning: return "числення шляху обірвано";
    case kReconnect:     return "рукостискання";
    case kOnline:        return "контроль повернуто";
    case kEventSample:   return "пачка телеметрії";
    default:             return "?";
    }
}

FallbackController::FallbackController(Board& board, std::uint32_t key)
    : board_{board},
      clock_{board.now()},
      deadman_{board, kDeadmanTimeout, kHeartbeat},
      link_{key},
      log_{board},
      stateSince_{board.now()},
      lastFrame_{board.now()},
      offlineSince_{board.now()},
      lastRaw_{board.now()} {
    board_.setSoftwareEnable(true);
    board_.setBrake(false);
}

// Рампа з обмеженням і прискорення, і ривка: уставка не може ні стрибнути,
// ні різко змінити темп — саме це рятує шестерні під час повернення контролю.
void FallbackController::rampThrottle(float target, float dt) {
    if (dt <= 0.0f) return;
    const float err = target - throttle_;
    const float wantRate = std::clamp(err / dt, -kMaxAccel, kMaxAccel);
    const float dRate = std::clamp(wantRate - throttleRate_, -kMaxJerk * dt, kMaxJerk * dt);

    throttleRate_ += dRate;
    throttle_ += throttleRate_ * dt;

    if ((err > 0.0f && throttle_ > target) || (err < 0.0f && throttle_ < target)) {
        throttle_ = target;      // ціль досягнуто, темп скидаємо
        throttleRate_ = 0.0f;
    }
    throttle_ = std::clamp(throttle_, -1.0f, 1.0f);
}

void FallbackController::rampSteering(float target, float dt) {
    const float step = kSteerRate * dt;
    steering_ = std::clamp(target, steering_ - step, steering_ + step);
}

void FallbackController::enter(State next, Millis now, std::uint8_t code, bool critical) {
    state_ = next;
    stateSince_ = now;
    log_.event(now, code, critical);

    switch (next) {
    case State::AutonomousPhase2:
        // Тиша затягнулася: сесію анулюємо. Тепер жодна команда не діє,
        // поки пульт не пройде рукостискання наново.
        link_.dropSession();
        break;
    case State::SafeStatePhase3:
        throttle_ = 0.0f;
        throttleRate_ = 0.0f;
        steering_ = 0.0f;
        board_.setActuators(0.0f, 0.0f);
        board_.setSoftwareEnable(false);
        board_.setBrake(true);
        board_.setLowPower(true);
        break;
    case State::Reconnecting:
        board_.setSoftwareEnable(true);
        board_.setLowPower(false);
        board_.setBeacon(false);
        board_.setBrake(false);
        break;
    default:
        break;
    }
}

std::expected<void, LinkError> FallbackController::handleFrame(std::span<const std::byte> frame) {
    const auto raw = board_.now();
    const auto now = clock_.now(raw);

    auto decoded = link_.accept(frame, now);
    if (!decoded) return std::unexpected(decoded.error());   // не кадр — не дозвіл

    lastFrame_ = now;
    deadman_.feed(now);

    if (decoded->type == FrameType::Hello) {
        // Крок 2 порядку відновлення: еталон часу лише ставимо в чергу на
        // підтягування. Стрибок годинника назад заборонений.
        clock_.setReference(raw, decoded->stamp);
        if (state_ == State::AutonomousPhase2 || state_ == State::SafeStatePhase3)
            enter(State::Reconnecting, now, event::kReconnect, false);
        return {};
    }

    cached_ = *decoded;
    if (state_ == State::HoldPhase1) enter(State::Online, now, event::kOnline, false);
    return {};
}

void FallbackController::tick(float sensorValue) {
    const auto raw = board_.now();
    clock_.tick(raw);
    const auto now = clock_.now(raw);
    const auto dtMs = raw - lastRaw_;
    lastRaw_ = raw;
    const float dt = static_cast<float>(dtMs.count()) / 1000.0f;

    deadman_.service(now);   // поки дозвіл живий — тактуємо ENABLE
    const auto silence = now - lastFrame_;

    switch (state_) {
    case State::Online:
        if (deadman_.expired(now)) {
            offlineSince_ = now;
            drPos_ = 0.0f;
            drSigma_ = 0.0f;
            enter(State::HoldPhase1, now, event::kLinkLost, false);
        } else {
            rampThrottle(cached_.throttle, dt);
            rampSteering(cached_.steering, dt);
        }
        break;

    case State::HoldPhase1: {
        // Екстраполюємо рух за одометрією й одразу рахуємо, як росте похибка.
        drPos_ += std::fabs(throttle_) * kMaxSpeed * dt;
        drSigma_ += (kSigmaBase + kSigmaGain * std::fabs(throttle_)) * dt;

        if (drSigma_ > kSigmaLimit) {
            // Невизначеність вийшла за радіус безпеки — числення обриваємо
            // примусово, не чекаючи п'яти секунд.
            enter(State::AutonomousPhase2, now, event::kDeadReckoning, true);
            break;
        }
        if (silence > kPhase1Timeout) {
            enter(State::AutonomousPhase2, now, event::kPhase2, false);
            break;
        }
        // Утримання уставки: наростання заборонене, дозволене лише збереження
        // або згасання, тому ціль не більша за модулем від поточної тяги.
        const float hold = std::fabs(cached_.throttle) < std::fabs(throttle_) ? cached_.throttle : throttle_;
        rampThrottle(hold, dt);
        rampSteering(steering_, dt);
        break;
    }

    case State::AutonomousPhase2: {
        if (silence > kPhase2Timeout) {
            enter(State::SafeStatePhase3, now, event::kSafeState, true);
            break;
        }
        // Локальний регулятор: рівномірне сповільнення до нуля, кермо в центр,
        // а на зупинці — механічне гальмо.
        const float step = kDecel * dt;
        const float target = std::fabs(throttle_) > step ? throttle_ - std::copysign(step, throttle_) : 0.0f;

        rampThrottle(target, dt);
        rampSteering(0.0f, dt);

        if (std::fabs(throttle_) < 0.01f) {
            throttle_ = 0.0f;
            throttleRate_ = 0.0f;
            board_.setBrake(true);
        }
        break;
    }

    case State::SafeStatePhase3:
        // Енергію знято безумовно; рампи тут немає й бути не може.
        throttle_ = 0.0f;
        throttleRate_ = 0.0f;
        steering_ = 0.0f;
        beaconPhase_ = (beaconPhase_ + dtMs) % kBeaconPeriod;
        board_.setBeacon(beaconPhase_ < kBeaconFlash);
        break;

    case State::Reconnecting:
        if (deadman_.expired(now)) {
            // Рукостискання було, а команди знову зникли — назад у фазу 1.
            offlineSince_ = now;
            drSigma_ = 0.0f;
            enter(State::HoldPhase1, now, event::kLinkLost, false);
            break;
        }
        rampThrottle(cached_.throttle, dt);
        rampSteering(cached_.steering, dt);
        if (now - stateSince_ >= kReconnectHold && std::fabs(cached_.throttle - throttle_) < 0.02f)
            enter(State::Online, now, event::kOnline, false);
        break;
    }

    if (state_ != State::SafeStatePhase3) {
        board_.setActuators(throttle_, steering_);
        if (std::fabs(throttle_) > 0.01f) board_.setBrake(false);
    }

    log_.sample(now, sensorValue, state_ == State::Online ? Millis{0} : now - offlineSince_);
    log_.backgroundErase();

    if (state_ == State::Online || state_ == State::Reconnecting) {
        drainCredit_ = std::min(drainCredit_ + kDrainCreditPerTick, kDrainCreditMax);
        drainCredit_ -= log_.drain(drainCredit_);
    }
}

Millis FallbackController::offlineFor() const noexcept {
    if (state_ == State::Online) return Millis{0};
    return clock_.now(lastRaw_) - offlineSince_;
}

}  // namespace cart
