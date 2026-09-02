#include "power.h"

#include <math.h>

float power_drag_force(const RoverParams *p, float v)
{
    if (v <= 0.0f) {
        return 0.0f;
    }
    return p->roll_resist_n + p->drag_coeff * v * v;
}

float power_yaw_torque(const RoverParams *p, const VehicleState *st,
                       float yaw_rate_cmd, float dt)
{
    const float yaw_accel = (yaw_rate_cmd - st->yaw_rate) / dt;
    /* Знак збурення вже приведений спостерігачем до «що мусять дати мотори». */
    return p->yaw_inertia * yaw_accel
         + p->yaw_damping * yaw_rate_cmd
         + st->yaw_disturbance_nm;
}

float power_yaw_rate_for_torque(const RoverParams *p, const VehicleState *st,
                                float torque_nm, float dt)
{
    /* Розв'язок power_yaw_torque() відносно yaw_rate_cmd. */
    const float a = p->yaw_inertia / dt + p->yaw_damping;
    const float b = torque_nm + p->yaw_inertia * st->yaw_rate / dt
                  - st->yaw_disturbance_nm;
    return b / a;
}

float power_yaw_current(const RoverParams *p, float torque_nm)
{
    /* Диференційна тяга: |F| = |τ| / колія на КОЖНОМУ борту, і обидва борти
     * тягнуть струм — один уперед, другий назад. */
    const float f_side = fabsf(torque_nm) / p->track_m;
    return 2.0f * f_side / p->force_per_amp;
}

PowerDraw power_predict(const RoverParams *p, const VehicleState *st,
                        Setpoint cmd, float dt)
{
    PowerDraw d;
    const float accel  = (cmd.vx - st->vx) / dt;
    const float f_long = p->mass_kg * accel + power_drag_force(p, st->vx);

    /* Гальмування йде вибігом і механічним гальмом — струму не бере.
     * Це навмисно консервативно: бар'єр не має права розраховувати на рекуперацію. */
    d.propulsion_a = (f_long > 0.0f) ? f_long / p->force_per_amp : 0.0f;
    d.yaw_a        = power_yaw_current(p, power_yaw_torque(p, st, cmd.yaw_rate, dt));
    d.total_a      = d.propulsion_a + d.yaw_a + p->idle_current_a;
    d.terminal_v   = st->pack_ocv_v - d.total_a * st->pack_esr_ohm;
    return d;
}

float power_budget_a(const SafetyLimits *lim, const VehicleState *st)
{
    float by_voltage = lim->pack_max_current_a;

    if (st->pack_esr_ohm > 1e-4f) {
        by_voltage = (st->pack_ocv_v - lim->pack_min_v) / st->pack_esr_ohm;
    }
    if (by_voltage > lim->pack_max_current_a) {
        by_voltage = lim->pack_max_current_a;
    }
    if (by_voltage < 0.0f) {
        by_voltage = 0.0f; /* пакет уже під порогом: рухового струму нема взагалі */
    }
    return by_voltage;
}
