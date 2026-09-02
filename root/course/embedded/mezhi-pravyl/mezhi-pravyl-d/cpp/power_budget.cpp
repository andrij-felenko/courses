#include "power_budget.hpp"

#include <algorithm>
#include <cmath>

namespace rover::power {

float drag_force(const Params& p, float v) noexcept
{
    if (v <= 0.0f) {
        return 0.0f;
    }
    return p.roll_resist_n + p.drag_coeff * v * v;
}

float yaw_torque(const Params& p, const VehicleState& st,
                 float yaw_rate_cmd, float dt) noexcept
{
    const float yaw_accel = (yaw_rate_cmd - st.yaw_rate) / dt;
    // Знак збурення вже приведений спостерігачем до «що мусять дати мотори».
    return p.yaw_inertia * yaw_accel
         + p.yaw_damping * yaw_rate_cmd
         + st.yaw_disturbance_nm;
}

float yaw_rate_for_torque(const Params& p, const VehicleState& st,
                          float torque_nm, float dt) noexcept
{
    const float a = p.yaw_inertia / dt + p.yaw_damping;
    const float b = torque_nm + p.yaw_inertia * st.yaw_rate / dt
                  - st.yaw_disturbance_nm;
    return b / a;
}

float yaw_current(const Params& p, float torque_nm) noexcept
{
    // |F| = |τ| / колія на КОЖНОМУ борту, і обидва борти беруть струм.
    const float f_side = std::fabs(torque_nm) / p.track_m;
    return 2.0f * f_side / p.force_per_amp;
}

Draw predict(const Params& p, const VehicleState& st, Setpoint cmd, float dt) noexcept
{
    const float accel  = (cmd.vx - st.vx) / dt;
    const float f_long = p.mass_kg * accel + drag_force(p, st.vx);

    Draw d;
    // Гальмування вибігом струму не бере: бар'єр не сміє розраховувати на рекуперацію.
    d.propulsion_a = (f_long > 0.0f) ? f_long / p.force_per_amp : 0.0f;
    d.yaw_a        = yaw_current(p, yaw_torque(p, st, cmd.yaw_rate, dt));
    d.total_a      = d.propulsion_a + d.yaw_a + p.idle_current_a;
    d.terminal_v   = st.pack_ocv_v - d.total_a * st.pack_esr_ohm;
    return d;
}

float budget(const Limits& lim, const VehicleState& st) noexcept
{
    if (st.pack_esr_ohm <= 1e-4f) {
        return lim.pack_max_current_a;
    }
    const float by_voltage = (st.pack_ocv_v - lim.pack_min_v) / st.pack_esr_ohm;
    return std::clamp(by_voltage, 0.0f, lim.pack_max_current_a);
}

} // namespace rover::power
