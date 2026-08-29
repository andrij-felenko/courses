#include "vehicle.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace hitl {

Airframe::Airframe(float inertia, float damping, float torque_gain)
    : inertia_{inertia}, damping_{damping}, torque_gain_{torque_gain} {
    if (inertia <= 0.0f) {
        throw std::invalid_argument{"момент інерції має бути додатним"};
    }
}

void Airframe::Step(float control, float disturbance, float dt) noexcept {
    const float torque =
        control * torque_gain_ + disturbance - damping_ * rate_rad_s_;
    const float accel = torque / inertia_;

    // Напівнеявний крок (Ейлер–Кромер): на 500 Гц він тримає фазу точніше
    // за прямий Ейлер, а фаза тут — головна вимірювана величина.
    rate_rad_s_ += accel * dt;
    angle_rad_ += rate_rad_s_ * dt;
}

Autopilot::Autopilot(ControlMode mode, float dt) noexcept
    : mode_{mode}, stick_monitor_{dt} {}

void Autopilot::EnableSuppression(bool on) noexcept {
    suppression_ = on;
    // Разом із демпфуванням вмикається й жорсткий обмежувач крутизни.
    slew_limit_ = on ? 5.0f : 25.0f;
}

float Autopilot::Update(float stick, const Airframe& air, float dt) noexcept {
    ++steps_;

    // 1. Динамічне демпфування стіка: якщо сама команда коливається в смузі
    //    0.5–2.5 Гц, чутливість пульта тимчасово падає. Це знімає підсилення
    //    контуру саме там, де людина підняла його з переляку.
    stick_monitor_.Update(stick);
    const float target_sens =
        (suppression_ && stick_monitor_.IsPio(0.10f)) ? 0.45f : 1.0f;
    sensitivity_ += (target_sens - sensitivity_) * (dt / 0.20f);
    const float shaped = stick * sensitivity_;

    // 2. Обмеження крутизни уставки: панічний перекид стіка з краю в край не
    //    має вимагати від машини швидкості, якої вона фізично не має.
    const float max_step = slew_limit_ * dt;
    setpoint_ += std::clamp(shaped - setpoint_, -max_step, max_step);

    // 3. Зовнішній контур: у Rate стік задає кутову швидкість, у Angle — кут,
    //    і тоді швидкий контур замикається вже на борту.
    float rate_cmd = 0.0f;
    if (mode_ == ControlMode::Rate) {
        rate_cmd = setpoint_ * max_rate_;
    } else {
        const float angle_cmd = setpoint_ * max_angle_;
        rate_cmd = std::clamp(kp_angle_ * (angle_cmd - air.angle()), -max_rate_,
                              max_rate_);
    }

    // 4. Внутрішній ПІ-контур швидкості на локальному гіроскопі.
    const float err = rate_cmd - air.rate();
    const float unsaturated = kp_rate_ * err + integral_;
    const float out = std::clamp(unsaturated, -torque_limit_, torque_limit_);

    const bool saturated = std::abs(unsaturated - out) > 1e-6f;
    if (saturated) {
        ++saturated_;
    }
    // Анти-віндап: поки вихід уперся в межу, інтегратор має право рухатися
    // лише в бік виходу з насичення.
    const bool unwinding = saturated && ((err > 0.0f) != (out > 0.0f));
    if (!saturated || unwinding) {
        integral_ = std::clamp(integral_ + ki_rate_ * err * dt, -torque_limit_,
                               torque_limit_);
    }
    return out;
}

ObjectDynamics Autopilot::Describe(const Airframe& air) const noexcept {
    const float loop = kp_rate_ * air.torque_gain();  // жорсткість контуру швидкості
    const float inner_tc = air.inertia() / (loop + air.damping());

    if (mode_ == ControlMode::Rate) {
        // Стік задає швидкість, кут набігає інтегруванням: Y_c = G/s.
        return ObjectDynamics{max_rate_ * loop / (loop + air.damping()), inner_tc,
                              true};
    }
    // Стік задає кут: Y_c = G/(T*s + 1).
    return ObjectDynamics{max_angle_, 1.0f / kp_angle_ + inner_tc, false};
}

float Autopilot::saturation_ratio() const noexcept {
    return steps_ > 0 ? static_cast<float>(saturated_) / static_cast<float>(steps_)
                      : 0.0f;
}

}  // namespace hitl
