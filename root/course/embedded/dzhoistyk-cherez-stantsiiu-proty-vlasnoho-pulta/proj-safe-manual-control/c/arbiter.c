#include "arbiter.h"

#include <string.h>

static int16_t clamp_i16(int32_t v, int32_t lo, int32_t hi)
{
    if (v < lo) return (int16_t)lo;
    if (v > hi) return (int16_t)hi;
    return (int16_t)v;
}

static int16_t round_i16(float v)
{
    return (int16_t)(v >= 0.0f ? v + 0.5f : v - 0.5f);
}

/* Один крок лімітера: рухаємо стан не більш ніж на max_delta за виклик. */
static int16_t slew(float *state, int16_t target, float dt_sec)
{
    const float max_delta = AXIS_SLEW_PER_SEC * dt_sec;
    float diff = (float)target - *state;

    if (diff > max_delta)  diff = max_delta;
    if (diff < -max_delta) diff = -max_delta;
    *state += diff;
    return round_i16(*state);
}

/* Синхронізація лімітерів із виходом: після перехоплення пультом чи після
 * дизарму наступний перехід не має починатися зі старої точки. */
static void latch_output(arbiter_t *a, const control_axes_t *axes)
{
    a->out = *axes;
    a->out_f.roll     = (float)axes->roll;
    a->out_f.pitch    = (float)axes->pitch;
    a->out_f.yaw      = (float)axes->yaw;
    a->out_f.throttle = (float)axes->throttle;
}

static bool sticks_deflected(const control_axes_t *ax)
{
    if (ax->roll  < -RC_DEADBAND_NORM || ax->roll  > RC_DEADBAND_NORM) return true;
    if (ax->pitch < -RC_DEADBAND_NORM || ax->pitch > RC_DEADBAND_NORM) return true;
    if (ax->yaw   < -RC_DEADBAND_NORM || ax->yaw   > RC_DEADBAND_NORM) return true;
    if (ax->throttle > RC_THROTTLE_DEADBAND) return true;
    return false;
}

void arbiter_init(arbiter_t *a)
{
    memset(a, 0, sizeof(*a));
    a->state        = ARB_DISARMED;
    a->failsafe     = FS_NONE;
    a->rc_link_lost = true;
}

void arbiter_set_home_available(arbiter_t *a, bool ok)
{
    a->home_valid = ok;
}

void arbiter_feed_rc(arbiter_t *a, const control_axes_t *rc, uint32_t now_ms)
{
    a->rc           = *rc;
    a->rc_ms        = now_ms;
    a->rc_seen      = true;
    a->rc_link_lost = false;
}

void arbiter_feed_manual_control(arbiter_t *a, int16_t x, int16_t y, int16_t z,
                                 int16_t r, uint16_t buttons, uint32_t now_ms)
{
    /* Порядок полів MANUAL_CONTROL і межі — зі специфікації повідомлення.
     * z обмежуємо [0..1000]: QGC шле тягу мультикоптера саме так. */
    a->gcs.pitch    = clamp_i16(x, -1000, 1000);
    a->gcs.roll     = clamp_i16(y, -1000, 1000);
    a->gcs.throttle = clamp_i16(z, 0, 1000);
    a->gcs.yaw      = clamp_i16(r, -1000, 1000);
    a->gcs.buttons  = buttons;
    a->gcs_ms       = now_ms;
    a->gcs_seen     = true;
}

arm_result_t arbiter_request_arm(arbiter_t *a, bool arm, bool confirmed, uint32_t now_ms)
{
    if (!arm) {
        /* Роззброєння — це аварійна зупинка, воно не має жодних умов. */
        a->armed    = false;
        a->failsafe = FS_NONE;
        a->state    = ARB_DISARMED;
        latch_output(a, &(control_axes_t){0});
        return ARM_DISARMED;
    }

    if (a->armed)
        return ARM_ACCEPTED;

    if (a->failsafe != FS_NONE)
        return ARM_DENIED_FAILSAFE;

    /* Свіжий канал керування обов'язковий: армитися «наосліп», коли команда
     * пройшла, а потік осей ні, — прямий шлях до розкрученого мотора. */
    {
        const uint32_t gcs_age = a->gcs_seen ? (now_ms - a->gcs_ms) : 0xFFFFFFFFu;
        const uint32_t rc_age  = a->rc_seen  ? (now_ms - a->rc_ms)  : 0xFFFFFFFFu;
        if (gcs_age > GCS_DEGRADE_MS && rc_age > RC_LINK_TIMEOUT_MS)
            return ARM_DENIED_NO_LINK;
    }

    if ((a->gcs_seen && sticks_deflected(&a->gcs)) ||
        (!a->rc_link_lost && sticks_deflected(&a->rc)))
        return ARM_DENIED_STICKS;

    if (!confirmed)
        return ARM_NEED_CONFIRMATION;

    a->armed = true;
    latch_output(a, &(control_axes_t){0});
    a->state = ARB_GCS_ACTIVE;
    return ARM_ACCEPTED;
}

void arbiter_update(arbiter_t *a, uint32_t now_ms, float dt_sec)
{
    const uint32_t rc_age  = a->rc_seen  ? (now_ms - a->rc_ms)  : 0xFFFFFFFFu;
    const uint32_t gcs_age = a->gcs_seen ? (now_ms - a->gcs_ms) : 0xFFFFFFFFu;

    a->rc_link_lost = (rc_age > RC_LINK_TIMEOUT_MS);

    if (!a->armed) {
        a->state    = ARB_DISARMED;
        a->failsafe = FS_NONE;
        latch_output(a, &(control_axes_t){0});
        return;
    }

    /* Бар'єр 1. Пілот безпеки відхилив стік — станція вимикається тієї ж ітерації.
     * Ніякого лімітера тут немає навмисно: затримка реакції пульта і є те,
     * заради чого пульт узагалі тримають у руках. */
    if (!a->rc_link_lost && sticks_deflected(&a->rc)) {
        if (a->state != ARB_RC_ACTIVE)
            a->preempt_events++;
        a->state    = ARB_RC_ACTIVE;
        a->failsafe = FS_NONE; /* пілот перебрав керування — аварійну процедуру знято */
        latch_output(a, &a->rc);
        return;
    }

    /* Аварійна процедура, раз почавшись, сама не скасовується: її знімає
     * або перехоплення пультом (вище), або дизарм. Свіжі пакети станції
     * мовчки скасувати RTL не можуть. */
    if (a->failsafe != FS_NONE) {
        a->state = ARB_FAILSAFE;
        a->out.roll     = slew(&a->out_f.roll, 0, dt_sec);
        a->out.pitch    = slew(&a->out_f.pitch, 0, dt_sec);
        a->out.yaw      = slew(&a->out_f.yaw, 0, dt_sec);
        a->out.throttle = slew(&a->out_f.throttle, HOVER_THROTTLE, dt_sec);
        a->out.buttons  = 0;
        return;
    }

    if (gcs_age < GCS_DEGRADE_MS) {
        /* Бар'єр 3. Пачка затриманих пакетів приходить одним махом —
         * на осі вона лягає похилою, а не сходинкою. */
        a->state        = ARB_GCS_ACTIVE;
        a->out.roll     = slew(&a->out_f.roll, a->gcs.roll, dt_sec);
        a->out.pitch    = slew(&a->out_f.pitch, a->gcs.pitch, dt_sec);
        a->out.yaw      = slew(&a->out_f.yaw, a->gcs.yaw, dt_sec);
        a->out.throttle = slew(&a->out_f.throttle, a->gcs.throttle, dt_sec);
        a->out.buttons  = a->gcs.buttons;
        return;
    }

    if (gcs_age < GCS_FAILSAFE_MS) {
        /* Бар'єр 2, перший поріг: кути в нуль, тяга на зависання.
         * Апарат зупиняється, але не падає й нікуди не летить. */
        if (a->state != ARB_GCS_DEGRADED)
            a->degrade_events++;
        a->state        = ARB_GCS_DEGRADED;
        a->out.roll     = slew(&a->out_f.roll, 0, dt_sec);
        a->out.pitch    = slew(&a->out_f.pitch, 0, dt_sec);
        a->out.yaw      = slew(&a->out_f.yaw, 0, dt_sec);
        a->out.throttle = slew(&a->out_f.throttle, HOVER_THROTTLE, dt_sec);
        a->out.buttons  = 0;
        return;
    }

    /* Бар'єр 2, другий поріг. Тягу НЕ обнуляємо: керування забирає автономний
     * режим, а нуль на тязі означав би падіння з висоти. */
    a->state    = ARB_FAILSAFE;
    a->failsafe = a->home_valid ? FS_RTL : FS_LAND;
    a->failsafe_events++;
    a->out.roll     = slew(&a->out_f.roll, 0, dt_sec);
    a->out.pitch    = slew(&a->out_f.pitch, 0, dt_sec);
    a->out.yaw      = slew(&a->out_f.yaw, 0, dt_sec);
    a->out.throttle = slew(&a->out_f.throttle, HOVER_THROTTLE, dt_sec);
    a->out.buttons  = 0;
}

const char *arbiter_state_name(arbiter_state_t s)
{
    switch (s) {
    case ARB_DISARMED:     return "DISARMED";
    case ARB_RC_ACTIVE:    return "RC_ACTIVE";
    case ARB_GCS_ACTIVE:   return "GCS_ACTIVE";
    case ARB_GCS_DEGRADED: return "GCS_DEGRADED";
    case ARB_FAILSAFE:     return "FAILSAFE";
    }
    return "?";
}

const char *arbiter_failsafe_name(failsafe_action_t f)
{
    switch (f) {
    case FS_NONE: return "-";
    case FS_RTL:  return "RTL";
    case FS_LAND: return "LAND";
    }
    return "?";
}

const char *arbiter_arm_result_name(arm_result_t r)
{
    switch (r) {
    case ARM_ACCEPTED:          return "ACCEPTED";
    case ARM_NEED_CONFIRMATION: return "NEED_CONFIRMATION";
    case ARM_DENIED_NO_LINK:    return "DENIED_NO_LINK";
    case ARM_DENIED_STICKS:     return "DENIED_STICKS";
    case ARM_DENIED_FAILSAFE:   return "DENIED_FAILSAFE";
    case ARM_DISARMED:          return "DISARMED";
    }
    return "?";
}
