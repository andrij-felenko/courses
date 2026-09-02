#include "channel.hpp"

#include <cmath>
#include <format>
#include <stdexcept>

namespace gcs {

Channel::Channel(std::string name, std::string unit, Danger danger, Limits limits)
    : name_{std::move(name)}, unit_{std::move(unit)}, danger_{danger}, limits_{limits} {
    const bool ordered = (danger_ == Danger::Rising) ? (limits_.warn < limits_.crit)
                                                     : (limits_.warn > limits_.crit);
    if (!ordered) {
        throw std::invalid_argument{
            std::format("канал {}: попереджувальний ліміт {} стоїть по той бік критичного {}",
                        name_, limits_.warn, limits_.crit)};
    }
    if (limits_.hysteresis < 0.0f || limits_.maxDriftRate < 0.0f) {
        throw std::invalid_argument{std::format("канал {}: від'ємний гістерезис або поріг дрейфу", name_)};
    }
}

bool Channel::beyond(float v, float limit) const noexcept {
    return danger_ == Danger::Rising ? (v >= limit) : (v <= limit);
}

// Униз рівень іде лише через гістерезис — інакше на самій межі колір блимає
// щосекунди, а мигтіння втомлює око швидше за будь-який шум.
bool Channel::released(float v, float limit) const noexcept {
    return danger_ == Danger::Rising ? (v < limit - limits_.hysteresis)
                                     : (v > limit + limits_.hysteresis);
}

Severity Channel::rawLevel() const noexcept {
    if (beyond(value_, limits_.crit)) {
        return Severity::Critical;
    }
    // Тихий дрейф: цифра ще в нормі, але ліміт буде за дві хвилини. Саме цього
    // випадку око не бачить — похідна яскравості нижча за поріг магноцелюлярних клітин.
    if (toLimit_ && toLimit_->count() <= kCritHorizonS) {
        return Severity::Critical;
    }
    if (beyond(value_, limits_.warn)) {
        return Severity::Warning;
    }
    if (limits_.maxDriftRate > 0.0f && driftRate_ >= limits_.maxDriftRate) {
        return Severity::Warning;
    }
    return Severity::Normal;
}

void Channel::applyHysteresis(Severity next) noexcept {
    if (next >= severity_) {
        severity_ = next;
        return;
    }
    if (severity_ == Severity::Critical && beyond(value_, limits_.crit) &&
        !released(value_, limits_.crit)) {
        return;
    }
    if (next == Severity::Normal && beyond(value_, limits_.warn) &&
        !released(value_, limits_.warn)) {
        return;
    }
    severity_ = next;
}

std::expected<Severity, SampleError> Channel::update(float raw, Millis now) {
    if (!std::isfinite(raw)) {
        return std::unexpected{SampleError::NotFinite};  // NaN із побитого кадру
    }
    if (lastUpdate_ && now < *lastUpdate_) {
        lastUpdate_.reset();                             // джерело перезапустилось
        return std::unexpected{SampleError::TimeWentBackwards};
    }

    if (lastUpdate_) {
        const float dt = std::chrono::duration<float>(now - *lastUpdate_).count();
        if (dt >= kMinDt) {
            const float toward = danger_ == Danger::Rising ? (raw - value_) : (value_ - raw);
            driftRate_ = kEmaAlpha * (toward / dt) + (1.0f - kEmaAlpha) * driftRate_;
        }
    }

    value_ = raw;
    lastUpdate_ = now;
    stale_ = false;

    // Прогноз: скільки лишилось до критичного ліміту за поточним трендом.
    const float margin = danger_ == Danger::Rising ? (limits_.crit - value_) : (value_ - limits_.crit);
    if (margin <= 0.0f) {
        toLimit_ = std::chrono::duration<float>{0.0f};
    } else if (driftRate_ <= 1e-6f) {
        toLimit_.reset();
    } else {
        toLimit_ = std::chrono::duration<float>{margin / driftRate_};
    }

    applyHysteresis(rawLevel());
    return severity_;
}

void Channel::tick(Millis now) noexcept {
    if (!lastUpdate_ || limits_.staleAfter.count() == 0) {
        return;
    }
    stale_ = silence(now) >= limits_.staleAfter;
}

std::optional<std::chrono::duration<float>> Channel::timeToLimit() const noexcept {
    return toLimit_;
}

Millis Channel::silence(Millis now) const noexcept {
    return lastUpdate_ ? now - *lastUpdate_ : Millis{0};
}

Severity Channel::effectiveSeverity() const noexcept {
    if (stale_ && severity_ == Severity::Normal) {
        return Severity::Warning;
    }
    return severity_;
}

std::string_view severityName(Severity s) noexcept {
    switch (s) {
    case Severity::Critical: return "КРИТИЧНО";
    case Severity::Warning:  return "УВАГА";
    default:                 return "норма";
    }
}

} // namespace gcs
