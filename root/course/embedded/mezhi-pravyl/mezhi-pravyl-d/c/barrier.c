#include "barrier.h"

#include <math.h>

#include "power.h"

static float clampf(float v, float lo, float hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

/* Вердикти впорядковані за тяжкістю: назовні йде найважчий за такт. */
static int severity(BarrierVerdict v)
{
    switch (v) {
    case BARRIER_PASS:            return 0;
    case BARRIER_SPEED_CLAMPED:   return 1;
    case BARRIER_POWER_LIMITED:   return 2;
    case BARRIER_YAW_LIMITED:     return 3;
    case BARRIER_TILT_LIMITED:    return 4;
    case BARRIER_EMERGENCY_STOP:  return 5;
    }
    return 0;
}

static BarrierVerdict worse(BarrierVerdict a, BarrierVerdict b)
{
    return (severity(b) > severity(a)) ? b : a;
}

float barrier_h(const SafetyLimits *lim, const VehicleState *st)
{
    const float d_eff = st->range_ahead_m - lim->obstacle_margin_m;
    const float v     = (st->vx > 0.0f) ? st->vx : 0.0f;
    return d_eff - (v * v) / (2.0f * lim->brake_accel);
}

BarrierResult barrier_enforce(const RoverParams *p, const SafetyLimits *lim,
                              const VehicleState *st, Setpoint candidate, float dt)
{
    BarrierResult  r;
    VehicleState   view = *st;
    Setpoint       u = candidate;
    BarrierVerdict verdict = BARRIER_PASS;

    /* 0. Недовірене вимірювання далекоміра. Бар'єр не гадає: невідомий
     *    простір попереду вважається зайнятим. */
    if (!view.range_valid) {
        view.range_ahead_m = lim->obstacle_margin_m;
    }

    const float h     = barrier_h(lim, &view);
    const float d_eff = view.range_ahead_m - lim->obstacle_margin_m;

    if (h < 0.0f) {
        /* 1. Ми вже поза безпечною множиною — жодних торгів із планувальником. */
        u.vx = 0.0f;
        verdict = BARRIER_EMERGENCY_STOP;
    } else {
        /* 2. Дискретна умова бар'єра: h_{k+1} ≥ (1 − γ·dt)·h_k.
         *    Розкриваючи h через швидкість, дістаємо замкнену формулу насичення. */
        const float slack   = d_eff - (1.0f - lim->cbf_gamma * dt) * h;
        float       v_allow = (slack > 0.0f)
                              ? sqrtf(2.0f * lim->brake_accel * slack)
                              : 0.0f;
        if (v_allow > lim->v_max) {
            v_allow = lim->v_max;
        }
        if (u.vx > v_allow) {
            u.vx = v_allow;
            verdict = worse(verdict, BARRIER_SPEED_CLAMPED);
        }
    }
    if (u.vx < 0.0f) {
        u.vx = 0.0f; /* задній хід цим контуром не керується */
    }

    /* 3. Нахил платформи: за межею перекидання рух заборонено взагалі. */
    if (view.tilt_rad > lim->tilt_max_rad) {
        u.vx = 0.0f;
        verdict = worse(verdict, BARRIER_TILT_LIMITED);
    }

    /* 4. Зчеплення в повороті: |ω| ≤ a_lat / v. */
    float yaw_cap = lim->yaw_rate_max;
    if (u.vx > 0.2f) {
        const float traction_cap = lim->lat_accel_max / u.vx;
        if (traction_cap < yaw_cap) {
            yaw_cap = traction_cap;
        }
    }
    u.yaw_rate = clampf(u.yaw_rate, -yaw_cap, yaw_cap);

    /* 5. Струмовий бюджет пакета. Тут і живе конфлікт «обійти vs зберегти
     *    осередки», і розв'язується він не пріоритетом правил, а фізикою:
     *    момент рискання оплачується першим, бо без нього апарат не
     *    відвернеться від огорожі; тяга бере тільки те, що лишилось. */
    const float budget   = power_budget_a(lim, &view);
    const float i_motion = budget - p->idle_current_a;

    if (i_motion <= 0.0f) {
        /* Пакет не тягне навіть утримання курсу — це вже безпечний стан. */
        u.vx = 0.0f;
        u.yaw_rate = 0.0f;
        verdict = worse(verdict, BARRIER_POWER_LIMITED);
    } else {
        const float tau_req = power_yaw_torque(p, &view, u.yaw_rate, dt);
        const float i_yaw   = power_yaw_current(p, tau_req);

        if (i_yaw > i_motion) {
            /* Весь руховий струм віддаємо рисканню, тяги не лишається. */
            const float sign      = (tau_req >= 0.0f) ? 1.0f : -1.0f;
            const float tau_allow = sign * i_motion * p->track_m
                                  * p->force_per_amp * 0.5f;
            const float w_allow   = power_yaw_rate_for_torque(p, &view, tau_allow, dt);

            if (u.yaw_rate >= 0.0f) {
                u.yaw_rate = clampf(w_allow, 0.0f, u.yaw_rate);
            } else {
                u.yaw_rate = clampf(w_allow, u.yaw_rate, 0.0f);
            }

            /* Без тяги швидкість може лише спадати вибігом. */
            float v_coast = view.vx - power_drag_force(p, view.vx) / p->mass_kg * dt;
            if (v_coast < 0.0f) {
                v_coast = 0.0f;
            }
            if (u.vx > v_coast) {
                u.vx = v_coast;
            }
            verdict = worse(verdict, BARRIER_YAW_LIMITED);
        } else {
            const float i_prop = i_motion - i_yaw;
            const float f_max  = i_prop * p->force_per_amp;
            float a_cap = (f_max - power_drag_force(p, view.vx)) / p->mass_kg;

            if (a_cap > lim->accel_max) {
                a_cap = lim->accel_max;
            }
            float v_cap = view.vx + a_cap * dt;
            if (v_cap < 0.0f) {
                v_cap = 0.0f;
            }
            if (u.vx > v_cap) {
                u.vx = v_cap;
                verdict = worse(verdict, BARRIER_POWER_LIMITED);
            }
        }
    }

    const PowerDraw draw = power_predict(p, &view, u, dt);

    r.out         = u;
    r.verdict     = verdict;
    r.h_value     = h;
    r.budget_a    = budget;
    r.predicted_a = draw.total_a;
    return r;
}

const char *barrier_verdict_name(BarrierVerdict v)
{
    switch (v) {
    case BARRIER_PASS:           return "пропущено";
    case BARRIER_SPEED_CLAMPED:  return "швидкість обрізано";
    case BARRIER_POWER_LIMITED:  return "струмовий бюджет";
    case BARRIER_YAW_LIMITED:    return "момент обрізано";
    case BARRIER_TILT_LIMITED:   return "нахил";
    case BARRIER_EMERGENCY_STOP: return "АВАРІЙНИЙ СТОП";
    }
    return "?";
}
