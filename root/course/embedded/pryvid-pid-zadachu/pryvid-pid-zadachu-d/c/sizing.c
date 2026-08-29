#include "sizing.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

/* Запас моменту, менше за який привід не беруть. */
static double required_margin(MotorFamily family)
{
    switch (family) {
    case MOTOR_STEPPER: return 2.0;   /* open-loop: зрив кроку нікому помітити */
    case MOTOR_SERVO:   return 1.5;   /* пластик редуктора й нагрів у стопорі */
    default:            return 1.3;   /* є зворотний зв'язок — досить 30% */
    }
}

static const char *task_problem(const MotionTask *t)
{
    if (t == NULL || t->label == NULL) {
        return "задача не задана";
    }
    if (t->target_speed_rpm <= 0.0) {
        return "цільова швидкість має бути додатною";
    }
    if (t->accel_time_s <= 0.0) {
        return "час розгону має бути додатним";
    }
    if (t->load_torque_nm < 0.0 || t->load_inertia_kgm2 < 0.0) {
        return "від'ємне навантаження";
    }
    if (t->move_duty < 0.0 || t->move_duty > 1.0) {
        return "частка часу в русі поза межами 0..1";
    }
    if (t->insulation_limit_c <= t->ambient_temp_c) {
        return "межа ізоляції не вища за температуру середовища";
    }
    return NULL;
}

bool sizing_evaluate(const MotorSpecs *m, const Gearbox *g,
                     const MotionTask *task, SizingReport *out)
{
    const char *problem;
    double omega_load, alpha_load, omega_motor, alpha_motor;
    double inertia_total, hold_torque, mech_output_w, mech_motor_w, hot_threshold_c;

    if (out == NULL) {
        return false;
    }
    memset(out, 0, sizeof *out);
    out->output_resolution_deg = -1.0;

    problem = motor_specs_problem(m);
    if (problem == NULL) {
        problem = gearbox_problem(g);
    }
    if (problem == NULL) {
        problem = task_problem(task);
    }
    if (problem != NULL) {
        out->fail = SZ_BAD_INPUT;
        out->input_problem = problem;
        return false;
    }

    omega_load = rpm_to_rad_s(task->target_speed_rpm);
    alpha_load = omega_load / task->accel_time_s;
    omega_motor = omega_load * g->ratio;
    alpha_motor = alpha_load * g->ratio;
    out->motor_speed_rpm = rad_s_to_rpm(omega_motor);

    /* T_motor = T_load / (N * eta) + (J_rotor + J_load / N^2) * alpha_motor */
    out->cruise_torque_nm = gearbox_reflect_torque(g, task->load_torque_nm);
    inertia_total = m->rotor_inertia_kgm2 + gearbox_reflect_inertia(g, task->load_inertia_kgm2);
    out->peak_torque_nm = out->cruise_torque_nm + inertia_total * alpha_motor;

    out->available_torque_nm = motor_available_torque(m, omega_motor);
    out->required_margin = required_margin(m->family);
    out->margin = (out->peak_torque_nm > 0.0)
                ? out->available_torque_nm / out->peak_torque_nm
                : INFINITY;

    if (out->motor_speed_rpm > m->no_load_speed_rpm) {
        out->fail |= SZ_SPEED_EXCEEDED;
    }
    if (out->margin < out->required_margin) {
        out->fail |= (m->family == MOTOR_STEPPER) ? SZ_STEP_LOSS : SZ_TORQUE_SHORT;
    }
    if (m->family == MOTOR_STEPPER && out->available_torque_nm < 0.5 * m->rated_torque_nm) {
        out->warn |= SZ_W_TORQUE_FADE;
    }

    /* Драйвер добирають за піком розгону, а не за середнім струмом. */
    out->peak_current_a = motor_current_for_torque(m, out->peak_torque_nm);
    out->stall_current_a = motor_stall_current(m);
    if (m->family != MOTOR_STEPPER && out->stall_current_a > 4.0 * m->rated_current_a) {
        out->warn |= SZ_W_INRUSH;
    }

    /* Тепло: у русі гріє крейсерський момент, у паузі — утримання. Розгін
       короткий і в середню потужність не входить: він задає струм драйвера.
       Кроковий гріється в паузі завжди — фази лишаються під струмом. */
    hold_torque = task->holds_under_load ? out->cruise_torque_nm : 0.0;
    out->copper_move_w = motor_copper_loss_w(m, out->cruise_torque_nm, false);
    out->copper_hold_w = (task->holds_under_load || m->family == MOTOR_STEPPER)
                       ? motor_copper_loss_w(m, hold_torque, true)
                       : 0.0;
    out->copper_average_w = task->move_duty * out->copper_move_w
                          + (1.0 - task->move_duty) * out->copper_hold_w;

    /* Втрати передачі гріють корпус редуктора, а не обмотку, тож у температуру
       обмотки не входять — але з бюджету живлення їх ніхто не викреслює. */
    mech_output_w = task->load_torque_nm * omega_load;
    out->gear_loss_w = gearbox_heat_loss_w(g, mech_output_w);
    out->winding_temp_c = motor_winding_temp_c(m, out->copper_average_w, task->ambient_temp_c);

    hot_threshold_c = task->ambient_temp_c
                    + 0.85 * (task->insulation_limit_c - task->ambient_temp_c);
    if (out->winding_temp_c > task->insulation_limit_c) {
        out->fail |= SZ_OVERHEAT;
    } else if (out->winding_temp_c > hot_threshold_c) {
        out->warn |= SZ_W_RUNS_HOT;
    }

    /* Оцінка входу: механіка на валу мотора (втрати передачі вже всередині
       cruise_torque_nm) плюс мідні втрати. */
    mech_motor_w = out->cruise_torque_nm * omega_motor;
    out->electrical_power_w = mech_motor_w * task->move_duty + out->copper_average_w;
    if (task->power_budget_w > 0.0 && out->electrical_power_w > task->power_budget_w) {
        out->fail |= SZ_POWER_BUDGET;
    }

    /* Дискрет на вихідному валу: редуктор ділить крок, але додає свій люфт. */
    if (m->step_resolution_deg > 0.0) {
        out->output_resolution_deg = m->step_resolution_deg / g->ratio + g->backlash_deg;
    }
    if (task->position_tolerance_deg > 0.0) {
        if (m->step_resolution_deg <= 0.0) {
            out->fail |= SZ_NO_FEEDBACK;
        } else if (out->output_resolution_deg > task->position_tolerance_deg) {
            out->fail |= SZ_PRECISION;
        }
    }

    return out->fail == 0u;
}

size_t sizing_describe(unsigned flags, char *buf, size_t size)
{
    static const struct {
        unsigned bit;
        const char *text;
    } NAMES[] = {
        { SZ_BAD_INPUT,      "суперечливі вхідні дані" },
        { SZ_TORQUE_SHORT,   "бракує моменту" },
        { SZ_STEP_LOSS,      "ризик зриву кроків" },
        { SZ_SPEED_EXCEEDED, "перевищено межу обертів" },
        { SZ_OVERHEAT,       "перегрів обмотки" },
        { SZ_POWER_BUDGET,   "не вкладається в бюджет живлення" },
        { SZ_NO_FEEDBACK,    "немає давача положення" },
        { SZ_PRECISION,      "дискрет із люфтом грубші за допуск" },
        { SZ_W_INRUSH,       "пусковий струм треба обмежувати драйвером" },
        { SZ_W_TORQUE_FADE,  "працює в зоні обвалу моменту" },
        { SZ_W_RUNS_HOT,     "температура близька до межі" }
    };
    size_t used = 0;
    size_t i;

    if (buf == NULL || size == 0) {
        return 0;
    }
    buf[0] = '\0';

    for (i = 0; i < sizeof NAMES / sizeof NAMES[0]; ++i) {
        int written;

        if ((flags & NAMES[i].bit) == 0u) {
            continue;
        }
        written = snprintf(buf + used, size - used, "%s%s",
                           (used > 0) ? ", " : "", NAMES[i].text);
        if (written < 0) {
            break;
        }
        if ((size_t)written >= size - used) {   /* більше не влазить — обрізаємо чесно */
            used = size - 1;
            break;
        }
        used += (size_t)written;
    }
    return used;
}
