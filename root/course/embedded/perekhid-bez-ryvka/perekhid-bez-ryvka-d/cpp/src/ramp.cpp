#include "bumpless/ramp.hpp"

#include <algorithm>
#include <cmath>

namespace bumpless {

float slew_step(float current, float target, float max_step) noexcept
{
    if (!(max_step > 0.0f)) {
        return target; // ремпінг вимкнено: уставка стрибає одразу
    }
    return std::clamp(target, current - max_step, current + max_step);
}

float lpf_step(float current, float target, float dt, float tau) noexcept
{
    if (!(tau > 0.0f) || !(dt > 0.0f)) {
        return target;
    }
    const float alpha = dt / (dt + tau);
    return current + alpha * (target - current);
}

SCurve::SCurve(float start, float goal, float v_max, float a_max, float j_max) noexcept
    : start_{start}, delta_{goal - start}, position_{start}
{
    const float distance = std::abs(delta_);
    if (distance < 1e-6f || !(v_max > 0.0f) || !(a_max > 0.0f) || !(j_max > 0.0f)) {
        // Рухатися нікуди або межі задані безглуздо — профілю немає.
        position_ = goal;
        return;
    }

    // Кожна межа диктує свою мінімальну тривалість; беремо найдовшу.
    const float t_vel = 1.875f * distance / v_max;
    const float t_acc = std::sqrt(5.7735f * distance / a_max);
    const float t_jerk = std::cbrt(60.0f * distance / j_max);

    duration_ = std::max({t_vel, t_acc, t_jerk});
    active_ = true;
}

bool SCurve::step(float dt) noexcept
{
    if (!active_) {
        return false;
    }

    t_ += dt;
    float x = t_ / duration_;
    if (x >= 1.0f) {
        x = 1.0f;
        active_ = false;
    }

    const float x2 = x * x;
    const float x3 = x2 * x;
    const float x4 = x3 * x;
    const float x5 = x4 * x;

    position_ = start_ + delta_ * (10.0f * x3 - 15.0f * x4 + 6.0f * x5);
    velocity_ = delta_ * (30.0f * x2 - 60.0f * x3 + 30.0f * x4) / duration_;
    acceleration_ = delta_ * (60.0f * x - 180.0f * x2 + 120.0f * x3) / (duration_ * duration_);

    if (!active_) {
        // На кінці профілю всі похідні нульові; дочищаємо заокруглення.
        velocity_ = 0.0f;
        acceleration_ = 0.0f;
    }
    return active_;
}

} // namespace bumpless
