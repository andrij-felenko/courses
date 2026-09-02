#include "safety_arbiter.hpp"

#include <algorithm>
#include <limits>

namespace nav::safety {
namespace {

constexpr float secondsOf(std::chrono::milliseconds span) noexcept
{
    return std::chrono::duration<float>(span).count();
}

std::uint32_t ticksOf(std::chrono::milliseconds span,
                      std::chrono::milliseconds tick) noexcept
{
    const auto count = span / tick;  // ділення тривалостей дає ціле число тактів
    return static_cast<std::uint32_t>(std::max<decltype(count)>(count, 1));
}

[[nodiscard]] constexpr Zone instantZone(float dist, float rStop, float rWarn) noexcept
{
    if (dist <= rStop) {
        return Zone::EmergencyStop;
    }
    if (dist <= rWarn) {
        return Zone::Warning;
    }
    return Zone::Observation;
}

}  // namespace

BodyVec toBody(OdomVec v, float yawRad) noexcept
{
    const float c = std::cos(yawRad);
    const float s = std::sin(yawRad);
    return { c * v.x + s * v.y, -s * v.x + c * v.y };
}

OdomVec toOdom(BodyVec v, float yawRad) noexcept
{
    const float c = std::cos(yawRad);
    const float s = std::sin(yawRad);
    return { c * v.x - s * v.y, s * v.x + c * v.y };
}

std::string_view zoneName(Zone zone) noexcept
{
    switch (zone) {
        case Zone::EmergencyStop: return "ESTOP";
        case Zone::Warning:       return "WARNING";
        default:                  return "OBSERVATION";
    }
}

std::string_view describe(ConfigError error) noexcept
{
    switch (error) {
        case ConfigError::NonPositiveDeceleration: return "сповільнення має бути додатним";
        case ConfigError::NegativeMargin:          return "від'ємний запас або гістерезис";
        default:                                    return "негодящі періоди такту й планувальника";
    }
}

Arbiter::Arbiter(const Config& cfg, std::uint32_t holdTicks, std::uint32_t watchdogTicks) noexcept
    : cfg_(cfg), holdTicks_(holdTicks), watchdogTicks_(watchdogTicks), holdCounter_(holdTicks)
{
}

std::expected<Arbiter, ConfigError> Arbiter::create(const Config& cfg) noexcept
{
    // Порівняння «> 0.05f» відсіює нуль, від'ємне і NaN одним рухом.
    if (!(cfg.maxDecel > 0.05f)) {
        return std::unexpected(ConfigError::NonPositiveDeceleration);
    }
    if (!(cfg.stopMargin >= 0.0f) || !(cfg.warnBuffer >= 0.0f) || !(cfg.hystDistance >= 0.0f)) {
        return std::unexpected(ConfigError::NegativeMargin);
    }
    if (cfg.tick <= std::chrono::milliseconds::zero() || cfg.plannerPeriod < cfg.tick
        || cfg.holdTime < cfg.tick) {
        return std::unexpected(ConfigError::BadTiming);
    }

    // Поріг сторожа — 2.5 періоди планувальника: менше, і джитер USB-CDC
    // чи завантаженого CAN систематично даватиме хибні спрацювання.
    const auto watchdogSpan = (cfg.plannerPeriod * 5) / 2;
    return Arbiter(cfg, ticksOf(cfg.holdTime, cfg.tick), ticksOf(watchdogSpan, cfg.tick));
}

float Arbiter::tickSeconds() const noexcept
{
    return secondsOf(cfg_.tick);
}

void Arbiter::submitPlan(BodyVec planBody) noexcept
{
    plan_ = planBody.finite() ? planBody : BodyVec{};
    sinceLastPlan_ = 0;
    plannerStale_ = false;
}

void Arbiter::stepStateMachine(Zone instant, float dist, float rStop, float rWarn) noexcept
{
    if (instant > zone_) {
        // Ескалація миттєва: у бік більшої небезпеки не зволікаємо ніколи.
        zone_ = instant;
        holdCounter_ = holdTicks_;
        return;
    }

    if (instant < zone_) {
        // Деескалація: спершу просторовий запас понад поріг, з якого виходимо.
        const bool hysteresisPassed =
            (zone_ == Zone::EmergencyStop) ? (dist > rStop + cfg_.hystDistance)
                                           : (dist > rWarn + cfg_.hystDistance);
        if (!hysteresisPassed) {
            holdCounter_ = holdTicks_;
            return;
        }
        // А тоді ще й витримка часом: шум давача дає «чисті» такти пачками.
        if (holdCounter_ > 0) {
            --holdCounter_;
        } else {
            zone_ = instant;
            holdCounter_ = holdTicks_;
        }
        return;
    }

    holdCounter_ = holdTicks_;
}

Decision Arbiter::update(BodyVec reactBody, const Sensing& sensing) noexcept
{
    // 0. Сторож планувальника рахує такти від останнього прийнятого плану.
    if (sinceLastPlan_ < std::numeric_limits<std::uint32_t>::max()) {
        ++sinceLastPlan_;
    }
    plannerStale_ = sinceLastPlan_ > watchdogTicks_;
    const BodyVec planVel = plannerStale_ ? BodyVec{} : plan_;
    const BodyVec reactVel = reactBody.finite() ? reactBody : BodyVec{};

    // 1. Санітарний фільтр входів. Мовчання давача трактуємо як перешкоду
    //    впритул: це єдине безпечне прочитання відсутніх даних.
    const bool rangeOk = sensing.minRange.has_value()
                         && std::isfinite(*sensing.minRange)
                         && *sensing.minRange >= 0.0f;
    const float dist = rangeOk ? *sensing.minRange : 0.0f;
    const float speed = std::isfinite(sensing.speed) ? std::max(0.0f, sensing.speed) : 0.0f;

    // 2. Динамічні межі зон за гальмівною кінематикою.
    const float dBrake = (speed * speed) / (2.0f * cfg_.maxDecel);
    const float rStop = dBrake + speed * secondsOf(cfg_.reactionTime) + cfg_.stopMargin;
    const float rWarn = rStop + speed * secondsOf(cfg_.plannerPeriod) + cfg_.warnBuffer;

    // 3. Автомат із просторово-часовим гістерезисом.
    stepStateMachine(instantZone(dist, rStop, rWarn), dist, rStop, rWarn);

    Decision decision{};
    decision.zone = zone_;
    decision.rStop = rStop;
    decision.rWarn = rWarn;
    decision.plannerStale = plannerStale_;

    switch (zone_) {
        case Zone::EmergencyStop:
            // Прапорець читає не лише силовий тракт: за ним низовий ПІ-регулятор
            // обнуляє інтеграл, інакше на виході з аварії мотори смикне.
            decision.overrideActive = true;
            decision.alpha = 1.0f;
            decision.command = {};
            break;

        case Zone::Warning: {
            decision.overrideActive = false;
            const float span = rWarn - rStop;
            decision.alpha = (span > 1e-3f)
                                 ? std::clamp((rWarn - dist) / span, 0.0f, 1.0f)
                                 : 1.0f;

            decision.command = planVel * (1.0f - decision.alpha) + reactVel * decision.alpha;

            const float distToStop = dist - rStop;
            if (distToStop > 0.0f) {
                decision.vSafe = std::sqrt(2.0f * cfg_.maxDecel * distToStop);
                const float len = decision.command.length();
                // Зрізаємо модуль, зберігаючи напрямок: інакше зникає сам маневр.
                if (len > decision.vSafe && len > 1e-3f) {
                    decision.command = decision.command * (decision.vSafe / len);
                }
            } else {
                decision.command = {};
            }
            break;
        }

        case Zone::Observation:
        default:
            decision.overrideActive = false;
            decision.alpha = 0.0f;
            decision.command = planVel;
            break;
    }

    return decision;
}

}  // namespace nav::safety
