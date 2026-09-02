#include "control/plant.hpp"

#include <limits>

namespace demo {

// Лінійний конгруентний генератор: детермінований, без залежностей.
float ClimbRatePlant::white() noexcept
{
    rng_ = rng_ * 1664525u + 1013904223u;
    return static_cast<float>((rng_ >> 8) & 0xFFFFu) / 32767.5f - 1.0f;
}

float ClimbRatePlant::step(float throttle, float dt) noexcept
{
    const float accel = (throttle - hover_throttle_) * thrust_gain_
                        - drag_ * climb_rate_
                        + gust_;

    climb_rate_ += accel * dt;
    altitude_ += climb_rate_ * dt;

    // Земля: нижче нуля апарат не опускається, швидкість гасне.
    if (altitude_ < 0.0f) {
        altitude_ = 0.0f;
        if (climb_rate_ < 0.0f) {
            climb_rate_ = 0.0f;
        }
    }
    return climb_rate_;
}

float ClimbRatePlant::sample(bool fault) noexcept
{
    // Шум фільтрованої оцінки швидкості — вузькосмуговий, не білий.
    noise_ = 0.9f * noise_ + 0.1f * (0.01f * white());

    if (fault) {
        return std::numeric_limits<float>::quiet_NaN();
    }
    return climb_rate_ + noise_;
}

} // namespace demo
