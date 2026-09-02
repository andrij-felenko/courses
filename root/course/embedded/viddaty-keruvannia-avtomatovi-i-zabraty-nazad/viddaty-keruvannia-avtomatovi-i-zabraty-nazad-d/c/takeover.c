#include "takeover.h"

#include <math.h>

#define TK_DT_MIN 0.0002f
#define TK_DT_MAX 0.1f

static void push_event(takeover_t *t, takeover_event_t e) {
    if (t->evt_count >= TK_EVENT_QUEUE) {
        /* Черга переповнена — губимо найстарішу подію: свіжа важливіша. */
        t->evt_head = (uint8_t)((t->evt_head + 1u) % TK_EVENT_QUEUE);
        t->evt_count--;
    }
    const uint8_t slot = (uint8_t)((t->evt_head + t->evt_count) % TK_EVENT_QUEUE);
    t->events[slot] = e;
    t->evt_count++;
}

bool takeover_pop_event(takeover_t *t, takeover_event_t *out) {
    if (!t || !out || t->evt_count == 0u) return false;
    *out = t->events[t->evt_head];
    t->evt_head = (uint8_t)((t->evt_head + 1u) % TK_EVENT_QUEUE);
    t->evt_count--;
    return true;
}

void takeover_init(takeover_t *t) {
    if (!t) return;
    t->state = TAKEOVER_AUTO_NAV;
    t->alpha = 0.0f;
    t->alpha_thr = 0.0f;
    t->hold_timer = 0.0f;
    t->thr_prev = 0.0f;
    t->thr_rate_lp = 0.0f;
    t->thr_engaged = false;
    t->prev_switch_manual = false;
    t->fence_latched = false;
    t->rc_lost = false;
    t->primed = false;
    t->evt_head = 0u;
    t->evt_count = 0u;
}

const char *takeover_state_name(takeover_state_t s) {
    switch (s) {
        case TAKEOVER_AUTO_NAV:      return "AUTO_NAV";
        case TAKEOVER_OVERRIDE_IN:   return "OVERRIDE_IN";
        case TAKEOVER_MANUAL_HOLD:   return "MANUAL_HOLD";
        case TAKEOVER_HANDBACK_WAIT: return "HANDBACK_WAIT";
        case TAKEOVER_BLENDING_OUT:  return "BLENDING_OUT";
        default:                     return "?";
    }
}

/* Осі орієнтації пружинять у нейтраль — їх судимо за абсолютним відхиленням. */
static bool attitude_deflected(const rc_command_t *rc) {
    return fabsf(rc->roll)  > TK_DEADBAND ||
           fabsf(rc->pitch) > TK_DEADBAND ||
           fabsf(rc->yaw)   > TK_DEADBAND;
}

static takeover_status_t make_status(const takeover_t *t, bool request_rtl) {
    takeover_status_t st;
    st.state = t->state;
    st.alpha = t->alpha;
    st.alpha_throttle = t->alpha_thr;
    st.freeze_nav = (t->alpha > TK_ACTIVE_EPS) || (t->alpha_thr > TK_ACTIVE_EPS);
    st.request_rtl = request_rtl;
    return st;
}

takeover_status_t takeover_update(takeover_t *t,
                                  const rc_command_t *rc,
                                  bool fence_breach,
                                  float dt_sec) {
    if (!t || !rc) {
        takeover_status_t dead = { TAKEOVER_AUTO_NAV, 0.0f, 0.0f, false, true };
        return dead;
    }

    /* Пропущений такт планувальника не має права перестрибнути всю рампу. */
    const float dt = clampf(dt_sec, TK_DT_MIN, TK_DT_MAX);

    if (!rc->link_ok) {
        /* Пастка перша: втрата зв'язку посеред ручного маневру. Тримати
           останні стіки не можна — вони вже нічого не означають. */
        if (!t->rc_lost) push_event(t, TK_EVT_RC_LOST);
        t->state = TAKEOVER_AUTO_NAV;
        t->alpha = 0.0f;
        t->alpha_thr = 0.0f;
        t->hold_timer = 0.0f;
        t->thr_engaged = false;
        t->prev_switch_manual = false;
        t->rc_lost = true;
        return make_status(t, true);
    }

    if (t->rc_lost || !t->primed) {
        /* Перший дійсний кадр (чи повернення зв'язку): похідну газу треба
           завести з поточного положення важеля, інакше стрибок з нуля
           виглядатиме як рвучкий рух пілота. */
        t->rc_lost = false;
        t->primed = true;
        t->thr_prev = rc->throttle;
        t->thr_rate_lp = 0.0f;
    }

    /* Рух важеля газу вимірюємо ШВИДКІСТЮ, а не відхиленням від центру:
       у літака газ не пружинить у нейтраль, і поріг |thr − 0.5| > db дав би
       вічне перехоплення на пульті, що просто лежить у нулі. */
    const float thr_rate = (rc->throttle - t->thr_prev) / dt;
    t->thr_prev = rc->throttle;
    t->thr_rate_lp += (thr_rate - t->thr_rate_lp) * (dt / (TK_THR_RATE_TAU + dt));
    const bool thr_moving = fabsf(t->thr_rate_lp) > TK_THR_MOVE_RATE;

    const bool switch_manual = (rc->mode == RC_MODE_MANUAL);
    const bool released_switch = t->prev_switch_manual && !switch_manual;
    t->prev_switch_manual = switch_manual;

    bool demand = attitude_deflected(rc) || thr_moving || switch_manual;

    /* Пастка третя: геозона. Її авторитет вищий за авторитет пілота, тому
       вимога перехоплення просто перестає існувати, доки триває порушення. */
    if (fence_breach) {
        if (!t->fence_latched) {
            t->fence_latched = true;
            push_event(t, TK_EVT_FENCE_RECLAIM);
        }
        demand = false;
        if (t->state == TAKEOVER_OVERRIDE_IN ||
            t->state == TAKEOVER_MANUAL_HOLD ||
            t->state == TAKEOVER_HANDBACK_WAIT) {
            /* Примусово, без таймера утримання — але через ту саму рампу. */
            t->state = TAKEOVER_BLENDING_OUT;
            t->hold_timer = 0.0f;
        }
    } else {
        t->fence_latched = false;
    }

    switch (t->state) {
        case TAKEOVER_AUTO_NAV:
            t->alpha = 0.0f;
            if (demand) {
                t->state = TAKEOVER_OVERRIDE_IN;
                push_event(t, TK_EVT_OVERRIDE_BEGIN);
            }
            break;

        case TAKEOVER_OVERRIDE_IN:
            t->alpha += dt / TK_BLEND_IN_SEC;
            if (t->alpha >= 1.0f) {
                t->alpha = 1.0f;
                t->state = TAKEOVER_MANUAL_HOLD;
                push_event(t, TK_EVT_MANUAL_FULL);
            }
            break;

        case TAKEOVER_MANUAL_HOLD:
            t->alpha = 1.0f;
            if (!demand) {
                t->hold_timer = 0.0f;
                if (released_switch) {
                    /* Тумблер — свідома дія, чекати нема на що. */
                    t->state = TAKEOVER_BLENDING_OUT;
                } else {
                    t->state = TAKEOVER_HANDBACK_WAIT;
                    push_event(t, TK_EVT_HANDBACK_ARMED);
                }
            }
            break;

        case TAKEOVER_HANDBACK_WAIT:
            t->alpha = 1.0f;
            if (demand) {
                /* Прохід стіка через нуль по дорозі в інший бік — не віддача. */
                t->state = TAKEOVER_MANUAL_HOLD;
                t->hold_timer = 0.0f;
            } else {
                t->hold_timer += dt;
                if (released_switch || t->hold_timer >= TK_HANDBACK_HOLD) {
                    t->state = TAKEOVER_BLENDING_OUT;
                }
            }
            break;

        case TAKEOVER_BLENDING_OUT:
            if (demand) {
                t->state = TAKEOVER_OVERRIDE_IN;
                push_event(t, TK_EVT_OVERRIDE_BEGIN);
            } else {
                t->alpha -= dt / TK_BLEND_OUT_SEC;
                if (t->alpha <= 0.0f) {
                    t->alpha = 0.0f;
                    t->state = TAKEOVER_AUTO_NAV;
                    t->thr_engaged = false;
                    push_event(t, TK_EVT_AUTO_RESUMED);
                }
            }
            break;

        default:
            t->state = TAKEOVER_AUTO_NAV;
            t->alpha = 0.0f;
            break;
    }

    /* Пастка друга: неузгодженість газу. Осі крену й тангажу віддаємо стікам
       одразу, а контур швидкості лишається за автопілотом, доки важіль газу
       фізично не зрушить з місця. */
    if (t->state != TAKEOVER_AUTO_NAV && thr_moving && !t->thr_engaged) {
        t->thr_engaged = true;
        push_event(t, TK_EVT_THROTTLE_ENGAGED);
    }

    const float thr_target = t->thr_engaged ? t->alpha : 0.0f;
    if (t->alpha_thr < thr_target) {
        t->alpha_thr = fminf(thr_target, t->alpha_thr + dt / TK_BLEND_IN_SEC);
    } else {
        t->alpha_thr = fmaxf(thr_target, t->alpha_thr - dt / TK_BLEND_OUT_SEC);
    }

    return make_status(t, false);
}

control_command_t takeover_blend(const takeover_status_t *st,
                                 const control_command_t *cmd_auto,
                                 const control_command_t *cmd_pilot) {
    control_command_t out = { 0.0f, 0.0f, 0.0f, 0.0f };
    if (!st || !cmd_auto || !cmd_pilot) return out;

    /* u = (1 − α)·u_auto + α·u_pilot, окремо для орієнтації й окремо для газу. */
    const float ap = clampf(st->alpha, 0.0f, 1.0f);
    const float at = clampf(st->alpha_throttle, 0.0f, 1.0f);

    out.roll     = (1.0f - ap) * cmd_auto->roll     + ap * cmd_pilot->roll;
    out.pitch    = (1.0f - ap) * cmd_auto->pitch    + ap * cmd_pilot->pitch;
    out.yaw      = (1.0f - ap) * cmd_auto->yaw      + ap * cmd_pilot->yaw;
    out.throttle = (1.0f - at) * cmd_auto->throttle + at * cmd_pilot->throttle;
    return out;
}
