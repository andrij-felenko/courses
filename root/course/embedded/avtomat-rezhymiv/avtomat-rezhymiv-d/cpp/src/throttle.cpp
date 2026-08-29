#include "throttle.hpp"

#include <algorithm>
#include <cmath>

namespace fm {

float throttleMismatch(const VehicleState& s) noexcept
{
    return std::fabs(s.sticks.throttle - s.propulsion.motorOutput);
}

GuardResult throttleInterlock(Mode current, Mode target,
                              const VehicleState& s, const Params& p,
                              bool inAir) noexcept
{
    // На землі стрибок газу нічим не загрожує: тяга й так на холостому ходу,
    // а вимагати від пілота зводити ручку перед зльотом — марно дратувати.
    if (!inAir || !s.propulsion.armed) {
        return {};
    }
    if (!traits(current).autoThrottle || !manualThrottle(target)) {
        return {};
    }
    if (throttleMismatch(s) > p.throttleDeadband) {
        return std::unexpected(Deny::ThrottleMismatch);
    }
    return {};
}

float SlewLimiter::step(float target, Seconds dt, float ratePerS) noexcept
{
    if (!primed_) {
        reset(target);
        return output_;
    }
    if (dt.count() <= 0.0F || ratePerS <= 0.0F) {
        // Нульовий такт або вимкнене обмеження: пропускаємо як є, але стан
        // оновлюємо, щоб наступний крок рахувався від правди.
        output_ = target;
        return output_;
    }

    const float maxStep = ratePerS * dt.count();

    output_ = std::clamp(target, output_ - maxStep, output_ + maxStep);
    output_ = std::clamp(output_, 0.0F, 1.0F);
    return output_;
}

}  // namespace fm
