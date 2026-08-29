#include "failsafe.h"

#include <math.h>

#include "fm_time.h"
#include "guards.h"
#include "report.h"

bool fm_priority_overrides(fm_priority_t request, fm_priority_t active)
{
    if (active == FM_PRIO_NONE) {
        return true;
    }
    if (request >= FM_PRIO_HARDWARE) {
        return true;   /* апаратну відсічку не перебиває ніщо */
    }
    if (active >= FM_PRIO_CRITICAL) {
        return false;  /* Stage 2 і крах оцінювачів блокують і оператора, і місію */
    }
    if (active == FM_PRIO_NAV_FAILSAFE) {
        /* Рівень 3 пілот має право перехопити: якщо пульт знову в ефірі й
           людина свідомо бере керування, автомат поступається. */
        return request >= FM_PRIO_ROUTINE;
    }
    return request >= active;
}

const char *fm_priority_name(fm_priority_t prio)
{
    switch (prio) {
    case FM_PRIO_NONE:           return "none";
    case FM_PRIO_ROUTINE:        return "routine";
    case FM_PRIO_PILOT_OVERRIDE: return "pilot override";
    case FM_PRIO_NAV_FAILSAFE:   return "nav failsafe";
    case FM_PRIO_CRITICAL:       return "critical failsafe";
    case FM_PRIO_HARDWARE:       return "hardware";
    default:                     return "unknown";
    }
}

bool fm_failsafe_fence_breached(const fm_state_t *s, const fm_params_t *p)
{
    if (!s || !p) {
        return false;
    }
    if (!isnan(s->altitude_rel_m) && s->altitude_rel_m > p->fence_alt_m) {
        return true;
    }
    if (s->home_set && s->ekf_horiz_pos_valid &&
        fm_state_home_distance_m(s) > p->fence_radius_m) {
        return true;
    }
    return false;
}

static fm_preempt_t none_preempt(void)
{
    fm_preempt_t e;

    e.active   = false;
    e.priority = FM_PRIO_NONE;
    e.mode     = FM_MODE_STABILIZE;
    e.severity = MAV_SEVERITY_INFO;
    e.reason   = "";
    return e;
}

static fm_preempt_t make_preempt(fm_priority_t prio, fm_mode_t mode,
                                 uint8_t severity, const char *reason)
{
    fm_preempt_t e;

    e.active   = true;
    e.priority = prio;
    e.mode     = mode;
    e.severity = severity;
    e.reason   = reason;
    return e;
}

/* Куди повертатися, коли повертатися вже нікуди: RTL за наявності точки старту
   й справної горизонтальної оцінки, інакше — негайна посадка на місці, а без
   вертикальної оцінки — аварійний спуск на фіксованій тязі. Це і є каскадна
   деградація, записана в одну функцію. */
static fm_mode_t rescue_mode(const fm_state_t *s, const fm_params_t *p)
{
    if (fm_guard_rtl(s, p) == FM_ALLOW) {
        return FM_MODE_RTL;
    }
    if (fm_guard_altitude(s, p) == FM_ALLOW) {
        return FM_MODE_LAND;
    }
    return FM_MODE_EMERGENCY_LAND;
}

fm_preempt_t fm_failsafe_evaluate(const fm_state_t *s, const fm_params_t *p,
                                  fm_mode_t current, bool in_air)
{
    if (!s || !p) {
        return none_preempt();
    }

    /* Рівень 5: апаратна відсічка. Тумблер уже зняв живлення з регуляторів
       повз автомат — нам лишається привести свій стан у відповідність. */
    if (s->kill_switch) {
        return make_preempt(FM_PRIO_HARDWARE, FM_MODE_TERMINATE,
                            MAV_SEVERITY_EMERGENCY, "Failsafe: hardware kill switch");
    }

    /* Рівень 4: повна втрата кутової оцінки. Стабілізувати нічим, спускатися
       нічим; лишається відсічка (на апаратах із парашутом — його розкриття). */
    if (in_air && fm_guard_attitude(s) != FM_ALLOW) {
        return make_preempt(FM_PRIO_CRITICAL, FM_MODE_TERMINATE,
                            MAV_SEVERITY_EMERGENCY, "Failsafe: IMU lost, terminate");
    }

    /* Рівень 4: критичний розряд. Місія й оператор блокуються повністю. */
    if (s->battery_cell_v < p->batt_crit_cell_v ||
        s->battery_remaining < p->batt_crit_remaining) {
        const fm_mode_t mode = (fm_guard_altitude(s, p) == FM_ALLOW)
                             ? FM_MODE_LAND : FM_MODE_EMERGENCY_LAND;
        return make_preempt(FM_PRIO_CRITICAL, mode,
                            MAV_SEVERITY_CRITICAL, "Failsafe: battery stage 2, landing");
    }

    /* Рівень 4: обидві просторові оцінки розсипалися одночасно. */
    if (in_air && !s->ekf_vert_pos_valid && !s->ekf_horiz_pos_valid) {
        return make_preempt(FM_PRIO_CRITICAL, FM_MODE_EMERGENCY_LAND,
                            MAV_SEVERITY_CRITICAL, "Failsafe: EKF crash, emergency land");
    }

    /* Рівень 3 діє лише в повітрі: на землі втрата пульта — це просто вимкнений
       пульт, і зривати з місця апарат, що стоїть, не можна. */
    if (in_air) {
        if (fm_age_ms(s->now_ms, s->rc_last_frame_ms) > p->rc_loss_ms) {
            return make_preempt(FM_PRIO_NAV_FAILSAFE, rescue_mode(s, p),
                                MAV_SEVERITY_ALERT, "Failsafe: RC link lost");
        }
        if (fm_failsafe_fence_breached(s, p)) {
            return make_preempt(FM_PRIO_NAV_FAILSAFE, rescue_mode(s, p),
                                MAV_SEVERITY_ALERT, "Failsafe: geofence breach");
        }
        if (current == FM_MODE_GUIDED &&
            fm_age_ms(s->now_ms, s->gcs_last_heartbeat_ms) > p->gcs_loss_ms) {
            /* Guided без станції — політ за протермінованою точкою. */
            return make_preempt(FM_PRIO_NAV_FAILSAFE, rescue_mode(s, p),
                                MAV_SEVERITY_ALERT, "Failsafe: GCS link lost");
        }
        if (s->battery_cell_v < p->batt_low_cell_v ||
            s->battery_remaining < p->batt_low_remaining) {
            return make_preempt(FM_PRIO_NAV_FAILSAFE, rescue_mode(s, p),
                                MAV_SEVERITY_WARNING, "Failsafe: battery stage 1, RTL");
        }
    }

    return none_preempt();
}
