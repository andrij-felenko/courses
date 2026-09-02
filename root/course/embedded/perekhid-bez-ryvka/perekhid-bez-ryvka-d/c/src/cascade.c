#include "cascade.h"

#include "portable_irq.h"

void cascade_init(cascade_t *c, const cascade_config_t *cfg)
{
    bumpless_pid_init(&c->pos, &cfg->pos);
    bumpless_pid_init(&c->vel, &cfg->vel);
    bumpless_pid_init(&c->ang, &cfg->ang);

    c->vel_from_pos_gain = cfg->vel_from_pos_gain;
    c->ang_from_vel_gain = cfg->ang_from_vel_gain;
    c->pos_div = cfg->pos_div;
    c->vel_div = cfg->vel_div;

    c->tick = 0u;
    c->vel_sp = 0.0f;
    c->ang_sp = 0.0f;
    c->last_actuator = 0.0f;
}

void cascade_load_inner(cascade_t *c, const cascade_meas_t *m, float prev_actuator)
{
    /* Найнижчий поверх: I_rate = поточна команда на моторах. Це єдине число,
       яке справді врівноважує паразитний момент апарата. */
    bumpless_pid_handover(&c->ang, m->angle_rad, m->angle_rad, prev_actuator);
    c->ang_sp = m->angle_rad;
    c->last_actuator = prev_actuator;
}

void cascade_load_outer(cascade_t *c, const cascade_meas_t *m, float target_position)
{
    /* Проміжний поверх: виходом контуру швидкості є уставка кута, тому
       передзавантаження ділимо на передавальний коефіцієнт — це і є
       I_velocity = Angle_actual / Kp_angle зі статті. */
    bumpless_pid_handover(&c->vel, m->velocity_mps, m->velocity_mps,
                          m->angle_rad / c->ang_from_vel_gain);

    /* Верхній поверх: уставка позиції сідає на поточний вимір GNSS, а роль
       «попереднього виходу» грає фактична швидкість за інерціальною системою. */
    bumpless_pid_handover(&c->pos, m->position_m, target_position,
                          m->velocity_mps / c->vel_from_pos_gain);

    c->vel_sp = m->velocity_mps;
}

void cascade_handover(cascade_t *c, const cascade_meas_t *m,
                      float target_position, float prev_actuator)
{
    /* Уся передача повноважень — один неподільний блок. Швидкий контур не
       має шансу відпрацювати такт на напівзавантаженому каскаді. */
    const irq_state_t saved = irq_lock();

    cascade_load_inner(c, m, prev_actuator);
    cascade_load_outer(c, m, target_position);
    c->tick = 0u;

    irq_unlock(saved);
}

void cascade_start_naive(cascade_t *c, float target_position)
{
    bumpless_pid_start_naive(&c->pos, target_position);
    bumpless_pid_start_naive(&c->vel, 0.0f);
    bumpless_pid_start_naive(&c->ang, 0.0f);

    c->tick = 0u;
    c->vel_sp = 0.0f;
    c->ang_sp = 0.0f;
}

float cascade_update(cascade_t *c, const cascade_meas_t *m, float dt_fast)
{
    /* Зовнішній контур позиції: рідкісний, зі своїм повним dt. */
    if (c->pos_div > 0u && (c->tick % c->pos_div) == 0u) {
        const float v = bumpless_pid_update(&c->pos, m->position_m,
                                            dt_fast * (float)c->pos_div);
        c->vel_sp = v * c->vel_from_pos_gain;
    }

    /* Проміжний контур швидкості: між його тактами уставка кута тримається
       зафіксованою (звичайна екстраполяція нульового порядку). */
    if (c->vel_div > 0u && (c->tick % c->vel_div) == 0u) {
        bumpless_pid_set_target(&c->vel, c->vel_sp);
        const float a = bumpless_pid_update(&c->vel, m->velocity_mps,
                                            dt_fast * (float)c->vel_div);
        c->ang_sp = a * c->ang_from_vel_gain;
    }

    /* Внутрішній швидкий контур — на кожному такті. */
    bumpless_pid_set_target(&c->ang, c->ang_sp);
    c->last_actuator = bumpless_pid_update(&c->ang, m->angle_rad, dt_fast);

    c->tick++;
    return c->last_actuator;
}
