#include "supervisor.h"

#include <math.h>

void supervisor_init(Supervisor *s, const SafetyLimits *lim)
{
    s->candidate.vx = 0.0f;
    s->candidate.yaw_rate = 0.0f;
    s->have_candidate = false;
    s->candidate_age_s = 0.0f;
    s->max_candidate_age_s = 0.15f;  /* три періоди планувальника на 20 Гц */
    s->last_output.vx = 0.0f;
    s->last_output.yaw_rate = 0.0f;
    s->last_verdict = BARRIER_PASS;
    s->held_range_m = lim->obstacle_margin_m;
    s->dropouts = 0;
    s->max_dropouts = 40;            /* 0.2 с на 200 Гц */
    s->verdict_changes = 0;
    s->rejected_count = 0;
}

void supervisor_submit(Supervisor *s, Setpoint candidate)
{
    s->candidate = candidate;
    s->have_candidate = true;
    s->candidate_age_s = 0.0f;
}

/* Провал далекоміра не робить простір вільним: тримаємо останнє дійсне
 * значення й підсуваємо його на пройдений шлях, а після ліміту тактів
 * знімаємо довіру взагалі. */
static VehicleState sanitize_state(Supervisor *s, const VehicleState *raw, float dt)
{
    VehicleState st = *raw;

    if (raw->range_valid && isfinite(raw->range_ahead_m)) {
        s->dropouts = 0;
        s->held_range_m = raw->range_ahead_m;
    } else {
        s->dropouts++;
        s->held_range_m -= ((raw->vx > 0.0f) ? raw->vx : 0.0f) * dt;
        if (s->held_range_m < 0.0f) {
            s->held_range_m = 0.0f;
        }
        st.range_ahead_m = s->held_range_m;
        st.range_valid = (s->dropouts <= s->max_dropouts);
    }
    return st;
}

static CandidateStatus validate(const Supervisor *s, const SafetyLimits *lim)
{
    if (!s->have_candidate || s->candidate_age_s > s->max_candidate_age_s) {
        return CAND_STALE;
    }
    if (!isfinite(s->candidate.vx) || !isfinite(s->candidate.yaw_rate)) {
        return CAND_NOT_FINITE;
    }
    if (s->candidate.vx < -0.01f || s->candidate.vx > lim->v_max * 1.5f) {
        return CAND_OUT_OF_RANGE;
    }
    if (fabsf(s->candidate.yaw_rate) > lim->yaw_rate_max * 1.5f) {
        return CAND_OUT_OF_RANGE;
    }
    return CAND_OK;
}

/* Безударність: уставка змінюється не швидше, ніж апарат фізично може.
 * Розгін обмежений accel_max, гальмування — brake_accel (воно дозволене
 * більше, бо це рух у бік безпеки). */
static Setpoint slew(const Supervisor *s, const SafetyLimits *lim,
                     Setpoint want, float dt)
{
    const float up   = lim->accel_max * dt;
    const float down = lim->brake_accel * dt;
    const float dw   = lim->yaw_accel_max * dt;
    Setpoint out = s->last_output;

    if (want.vx > out.vx + up)        out.vx += up;
    else if (want.vx < out.vx - down) out.vx -= down;
    else                              out.vx = want.vx;

    if (want.yaw_rate > out.yaw_rate + dw)      out.yaw_rate += dw;
    else if (want.yaw_rate < out.yaw_rate - dw) out.yaw_rate -= dw;
    else                                        out.yaw_rate = want.yaw_rate;

    return out;
}

SupervisorTick supervisor_step(Supervisor *s, const RoverParams *p,
                               const SafetyLimits *lim,
                               const VehicleState *raw, float dt)
{
    SupervisorTick tick;
    const VehicleState st = sanitize_state(s, raw, dt);

    s->candidate_age_s += dt;
    tick.cand_status = validate(s, lim);

    Setpoint want;
    if (tick.cand_status == CAND_OK) {
        want = s->candidate;
    } else {
        /* Кандидата немає або він неприданий: власна безумовна поведінка —
         * рівне гальмування з утриманням курсу. */
        want.vx = s->last_output.vx - lim->brake_accel * dt;
        if (want.vx < 0.0f) {
            want.vx = 0.0f;
        }
        want.yaw_rate = 0.0f;
        s->rejected_count++;
    }

    const Setpoint smooth = slew(s, lim, want, dt);
    tick.barrier = barrier_enforce(p, lim, &st, smooth, dt);
    tick.out = tick.barrier.out;

    if (tick.barrier.verdict != s->last_verdict) {
        s->verdict_changes++;
        s->last_verdict = tick.barrier.verdict;
    }
    s->last_output = tick.out;
    return tick;
}

const char *supervisor_status_name(CandidateStatus s)
{
    switch (s) {
    case CAND_OK:            return "ок";
    case CAND_NOT_FINITE:    return "не число";
    case CAND_OUT_OF_RANGE:  return "поза обгорткою";
    case CAND_STALE:         return "протермінований";
    }
    return "?";
}
