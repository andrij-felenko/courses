#include "bumpless/plant.hpp"

#include "bumpless/ramp.hpp"

#include <algorithm>
#include <cmath>

namespace bumpless {

QuadPlant::QuadPlant(float mass_kg, float hover_throttle, float altitude_m) noexcept
    : mass_{mass_kg}
    // 1.8 кг * 9.81 / 0.52 ~= 34 Н повної тяги: газ висіння 52 % точно
    // врівноважує 17.66 Н ваги — саме це число й тримає інтегратор.
    , thrust_max_{mass_kg * kGravity / hover_throttle}
    , altitude_{altitude_m}
{
}

void QuadPlant::step(float throttle, float dt) noexcept
{
    const float thrust = std::clamp(throttle, 0.0f, 1.0f) * thrust_max_;
    const float drag = drag_ * vz_;

    accel_ = (thrust - drag) / mass_ - kGravity;
    vz_ += accel_ * dt;
    altitude_ += vz_ * dt;

    if (altitude_ < 0.0f) {
        // Земля. Далі падати нікуди, і симуляція не має права це приховати.
        altitude_ = 0.0f;
        vz_ = std::max(vz_, 0.0f);
    }
}

void LateralPlant::step(float actuator, float dt) noexcept
{
    const float u = std::clamp(actuator, -1.0f, 1.0f);

    // Команда приводу задає кутову швидкість; trim_bias — паразитний момент,
    // який доводиться постійно парирувати ненульовою командою.
    angle_ = std::clamp(angle_ + params_.rate_gain * (u + params_.trim_bias) * dt,
                        -0.6f, 0.6f);

    const float accel = kGravity * std::tan(angle_) + params_.wind_accel
                        - params_.drag * velocity_;
    velocity_ += accel * dt;
    position_ += velocity_ * dt;
}

float Servo::step(float command_deg, float dt) noexcept
{
    // Люфт трансмісії: поки команда не вийшла із зони нечутливості, вал стоїть,
    // і автопілот про це не дізнається — він бачить лише власну команду.
    if (std::abs(command_deg - position_) <= deadband_) {
        return position_;
    }

    position_ = slew_step(position_, command_deg, rate_max_ * dt);
    return position_;
}

} // namespace bumpless
