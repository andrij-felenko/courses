#include "safety_filter.hpp"

#include <algorithm>
#include <cmath>

namespace rover {

float SafetyFilter::barrier_value(const VehicleState& st) const noexcept
{
    const float d_eff = st.range_ahead_m - limits_.obstacle_margin_m;
    const float v     = std::max(st.vx, 0.0f);
    return d_eff - (v * v) / (2.0f * limits_.brake_accel);
}

void SafetyFilter::braking_barrier(const VehicleState& st, Setpoint& u, Verdict& v,
                                   float h, float dt) const noexcept
{
    if (h < 0.0f) {
        // Стан уже поза безпечною множиною — торгів із планувальником немає.
        u.vx = 0.0f;
        v = worse(v, Verdict::EmergencyStop);
        return;
    }

    // Дискретна умова бар'єра h_{k+1} ≥ (1 − γ·dt)·h_k, розкрита через швидкість.
    const float d_eff   = st.range_ahead_m - limits_.obstacle_margin_m;
    const float slack   = d_eff - (1.0f - limits_.cbf_gamma * dt) * h;
    const float v_allow = (slack > 0.0f)
                          ? std::min(std::sqrt(2.0f * limits_.brake_accel * slack),
                                     limits_.v_max)
                          : 0.0f;
    if (u.vx > v_allow) {
        u.vx = v_allow;
        v = worse(v, Verdict::SpeedClamped);
    }
}

void SafetyFilter::traction_limit(Setpoint& u) const noexcept
{
    // Зчеплення в повороті: |ω| ≤ a_lat / v.
    float cap = limits_.yaw_rate_max;
    if (u.vx > 0.2f) {
        cap = std::min(cap, limits_.lat_accel_max / u.vx);
    }
    u.yaw_rate = std::clamp(u.yaw_rate, -cap, cap);
}

void SafetyFilter::spend_current(const VehicleState& st, Setpoint& u, Verdict& v,
                                 float dt) const noexcept
{
    const float i_motion = power::budget(limits_, st) - params_.idle_current_a;

    if (i_motion <= 0.0f) {
        // Пакет не тягне навіть утримання курсу — це вже безпечний стан.
        u = Setpoint{};
        v = worse(v, Verdict::PowerLimited);
        return;
    }

    const float tau_req = power::yaw_torque(params_, st, u.yaw_rate, dt);
    const float i_yaw   = power::yaw_current(params_, tau_req);

    if (i_yaw > i_motion) {
        // Момент рискання оплачується першим: без нього апарат не відвернеться
        // від огорожі. Тяги після цього не лишається зовсім.
        const float sign      = (tau_req >= 0.0f) ? 1.0f : -1.0f;
        const float tau_allow = sign * i_motion * params_.track_m
                              * params_.force_per_amp * 0.5f;
        const float w_allow   = power::yaw_rate_for_torque(params_, st, tau_allow, dt);

        u.yaw_rate = (u.yaw_rate >= 0.0f)
                     ? std::clamp(w_allow, 0.0f, u.yaw_rate)
                     : std::clamp(w_allow, u.yaw_rate, 0.0f);

        const float v_coast = std::max(
            st.vx - power::drag_force(params_, st.vx) / params_.mass_kg * dt, 0.0f);
        u.vx = std::min(u.vx, v_coast);
        v = worse(v, Verdict::YawLimited);
        return;
    }

    const float f_max = (i_motion - i_yaw) * params_.force_per_amp;
    const float a_cap = std::min(
        (f_max - power::drag_force(params_, st.vx)) / params_.mass_kg,
        limits_.accel_max);
    const float v_cap = std::max(st.vx + a_cap * dt, 0.0f);

    if (u.vx > v_cap) {
        u.vx = v_cap;
        v = worse(v, Verdict::PowerLimited);
    }
}

Decision SafetyFilter::enforce(const VehicleState& st, Setpoint candidate,
                               float dt) const noexcept
{
    VehicleState view = st;
    // Недовірений далекомір: невідомий простір попереду вважається зайнятим.
    if (!view.range_valid) {
        view.range_ahead_m = limits_.obstacle_margin_m;
    }

    Setpoint u = candidate;
    Verdict  v = Verdict::Pass;
    const float h = barrier_value(view);

    braking_barrier(view, u, v, h, dt);
    u.vx = std::max(u.vx, 0.0f); // задній хід цим контуром не керується

    if (view.tilt_rad > limits_.tilt_max_rad) {
        u.vx = 0.0f;
        v = worse(v, Verdict::TiltLimited);
    }

    traction_limit(u);
    spend_current(view, u, v, dt);

    const auto draw = power::predict(params_, view, u, dt);
    return Decision{u, v, h, power::budget(limits_, view), draw.total_a};
}

} // namespace rover
