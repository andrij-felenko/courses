#include "BenchRun.hpp"

#include <algorithm>
#include <cmath>

namespace compassmot {
namespace {

using millis = std::chrono::milliseconds;

// Регламент прогону — це протокол, а не налаштування.
constexpr millis kBaselineTime{2000};
constexpr float  kStepPct       = 10.0f;
constexpr millis kStepHold{1200};
constexpr float  kPeakPct       = 85.0f;
constexpr millis kPeakHold{1500};
constexpr millis kDownStep{300};
constexpr millis kSettle{400};      // поки перехідний процес не вщух — не міряємо

constexpr float       kZeroCurrentA  = 1.0f;    // при 0% газу більше = зсув нуля шунта
constexpr float       kAbortCurrentA = 200.0f;
constexpr std::size_t kBaseMinSamples = 50;

}  // namespace

std::string_view name(Phase phase) noexcept
{
    switch (phase) {
    case Phase::Idle:     return "IDLE";
    case Phase::Baseline: return "BASELINE";
    case Phase::RampUp:   return "RAMP UP";
    case Phase::PeakHold: return "PEAK HOLD";
    case Phase::RampDown: return "RAMP DOWN";
    case Phase::Solve:    return "OLS SOLVE";
    case Phase::Save:     return "FLASH SAVE";
    case Phase::Done:     return "DONE";
    case Phase::Failed:   return "FAILED";
    }
    return "?";
}

std::size_t BenchRun::collected() const noexcept
{
    return ols_ ? ols_->count() : 0;
}

void BenchRun::enter(Phase phase, millis now) noexcept
{
    phase_ = phase;
    t_phase_ = now;
    t_step_ = now;
}

void BenchRun::set_throttle(float pct) noexcept
{
    throttle_pct_ = std::clamp(pct, 0.0f, kPeakPct);
    rig_->set_throttle(throttle_pct_);
}

void BenchRun::fail(std::string_view reason, FitError err, millis now) noexcept
{
    set_throttle(0.0f);          // перше і головне: зняти газ
    failure_ = reason;
    outcome_ = std::unexpected(err);
    enter(Phase::Failed, now);
}

void BenchRun::abort(std::string_view reason) noexcept
{
    if (phase_ == Phase::Done || phase_ == Phase::Failed) {
        return;
    }
    fail(reason.empty() ? std::string_view{"зупинено оператором"} : reason,
         FitError::TooFewSamples, t_phase_);
}

bool BenchRun::guard_and_sample(millis now, bool collect)
{
    const float i = rig_->read_current();
    const Vector3 b = rig_->read_field();

    if (std::isfinite(i) && i > kAbortCurrentA) {
        fail("струм за межею стенда: глушимо прогін", FitError::NoCurrentSpan, now);
        return false;
    }
    if (collect && ols_ && (now - t_step_) >= kSettle) {
        ols_->add(Sample{i, b});
    }
    return true;
}

Phase BenchRun::step(millis now)
{
    switch (phase_) {

    case Phase::Idle:
        set_throttle(0.0f);
        base_sum_ = Vector3{};
        base_n_ = 0;
        ols_.reset();
        failure_ = {};
        enter(Phase::Baseline, now);
        break;

    case Phase::Baseline: {
        const float i = rig_->read_current();
        const Vector3 b = rig_->read_field();

        // Шунт із температурним зсувом нуля зсуне все калібрування —
        // ловимо це тут, поки мотори ще стоять.
        if (std::isfinite(i) && std::abs(i) > kZeroCurrentA) {
            fail("давач струму показує струм при зупинених моторах: "
                 "спершу відкалібрувати зсув нуля шунта",
                 FitError::NoCurrentSpan, now);
            break;
        }
        if (b.finite()) {
            base_sum_ = base_sum_ + b;
            ++base_n_;
        }
        if ((now - t_phase_) < kBaselineTime) {
            break;
        }
        if (base_n_ < kBaseMinSamples) {
            fail("магнітометр майже не віддає даних", FitError::NoBaseField, now);
            break;
        }

        ols_.emplace(base_sum_ * (1.0f / static_cast<float>(base_n_)));
        set_throttle(kStepPct);
        enter(Phase::RampUp, now);
        break;
    }

    case Phase::RampUp:
        if (!guard_and_sample(now, true)) {
            break;
        }
        if ((now - t_step_) < kStepHold) {
            break;
        }
        if (throttle_pct_ >= kPeakPct - 0.5f) {
            enter(Phase::PeakHold, now);
            break;
        }
        set_throttle(throttle_pct_ + kStepPct);
        t_step_ = now;                 // нова сходинка — нова пауза на усталення
        break;

    case Phase::PeakHold:
        if (!guard_and_sample(now, true)) {
            break;
        }
        if ((now - t_phase_) >= kPeakHold) {
            set_throttle(throttle_pct_ - kStepPct);
            enter(Phase::RampDown, now);
        }
        break;

    case Phase::RampDown:
        // На спуску вибірок не беремо: дроти й ключі прогрілися, і
        // гістерезис намагніченості додав би в дані систематичний зсув,
        // якого лінійна модель не описує.
        if (!guard_and_sample(now, false)) {
            break;
        }
        if ((now - t_step_) < kDownStep) {
            break;
        }
        if (throttle_pct_ <= 0.5f) {
            set_throttle(0.0f);
            enter(Phase::Solve, now);
            break;
        }
        set_throttle(throttle_pct_ - kStepPct);
        t_step_ = now;
        break;

    case Phase::Solve:
        outcome_ = ols_ ? ols_->solve()
                        : std::expected<Fit, FitError>{std::unexpect, FitError::TooFewSamples};
        if (!outcome_) {
            fail(describe(outcome_.error()), outcome_.error(), now);
            break;
        }
        enter(Phase::Save, now);
        break;

    case Phase::Save:
        if (!rig_->store(outcome_->k)) {
            fail(describe(FitError::StoreFailed), FitError::StoreFailed, now);
            break;
        }
        enter(Phase::Done, now);
        break;

    case Phase::Done:
    case Phase::Failed:
        break;
    }

    return phase_;
}

}  // namespace compassmot
