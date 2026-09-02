#include "bumpless/cascade.hpp"

#include "bumpless/irq_guard.hpp"

namespace bumpless {

CascadeMeasurement measure(const LateralPlant& plant) noexcept
{
    return CascadeMeasurement{plant.position(), plant.velocity(), plant.angle()};
}

void CascadeController::load_inner(const CascadeMeasurement& m, float prev_actuator) noexcept
{
    // Найнижчий поверх: I_rate = поточна команда на моторах. Це єдине число,
    // яке справді врівноважує паразитний момент апарата.
    angle_.handover(m.angle, m.angle, prev_actuator);
    angle_sp_ = m.angle;
    last_actuator_ = prev_actuator;
}

void CascadeController::load_outer(const CascadeMeasurement& m, float target_position) noexcept
{
    // Проміжний поверх: виходом контуру швидкості є уставка кута, тому
    // передзавантаження ділимо на передавальний коефіцієнт — це і є
    // I_velocity = Angle_actual / Kp_angle зі статті.
    velocity_.handover(m.velocity, m.velocity, m.angle / cfg_.angle_from_velocity_gain);

    // Верхній поверх: уставка позиції сідає на поточний вимір GNSS, а роль
    // «попереднього виходу» грає фактична швидкість за інерціальною системою.
    position_.handover(m.position, target_position,
                       m.velocity / cfg_.velocity_from_position_gain);

    velocity_sp_ = m.velocity;
}

void CascadeController::handover(const CascadeMeasurement& m, float target_position,
                                 float prev_actuator) noexcept
{
    // Уся передача повноважень — один неподільний блок. Швидкий контур не
    // має шансу відпрацювати такт на напівзавантаженому каскаді.
    const IrqGuard guard;

    load_inner(m, prev_actuator);
    load_outer(m, target_position);
    tick_ = 0u;
}

void CascadeController::start_naive(float target_position) noexcept
{
    position_.start_naive(target_position);
    velocity_.start_naive(0.0f);
    angle_.start_naive(0.0f);

    tick_ = 0u;
    velocity_sp_ = 0.0f;
    angle_sp_ = 0.0f;
}

float CascadeController::update(const CascadeMeasurement& m, float dt_fast) noexcept
{
    // Зовнішній контур позиції: рідкісний, зі своїм повним dt.
    if (cfg_.position_divider > 0u && (tick_ % cfg_.position_divider) == 0u) {
        const float v = position_.update(m.position,
                                         dt_fast * static_cast<float>(cfg_.position_divider));
        velocity_sp_ = v * cfg_.velocity_from_position_gain;
    }

    // Проміжний контур швидкості: між його тактами уставка кута тримається
    // зафіксованою (звичайна екстраполяція нульового порядку).
    if (cfg_.velocity_divider > 0u && (tick_ % cfg_.velocity_divider) == 0u) {
        velocity_.set_target(velocity_sp_);
        const float a = velocity_.update(m.velocity,
                                         dt_fast * static_cast<float>(cfg_.velocity_divider));
        angle_sp_ = a * cfg_.angle_from_velocity_gain;
    }

    // Внутрішній швидкий контур — на кожному такті.
    angle_.set_target(angle_sp_);
    last_actuator_ = angle_.update(m.angle, dt_fast);

    ++tick_;
    return last_actuator_;
}

} // namespace bumpless
