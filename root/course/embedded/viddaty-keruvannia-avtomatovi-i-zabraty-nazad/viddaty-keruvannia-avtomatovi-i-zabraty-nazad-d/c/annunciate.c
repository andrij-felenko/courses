#include "annunciate.h"

#include <stdio.h>

#define MAV_MODE_FLAG_CUSTOM_MODE_ENABLED  1u
#define MAV_MODE_FLAG_AUTO_ENABLED         4u
#define MAV_MODE_FLAG_STABILIZE_ENABLED   16u
#define MAV_MODE_FLAG_MANUAL_INPUT_ENABLED 64u
#define MAV_MODE_FLAG_SAFETY_ARMED       128u

#define HEARTBEAT_PERIOD_MS   1000u
#define NAMED_VALUE_PERIOD_MS 100u

void annunciate_init(annunciator_t *an) {
    if (!an) return;
    an->last_heartbeat_ms = 0u;
    an->last_named_ms = 0u;
    an->started = false;
}

static void fill_text(char dst[50], const char *src) {
    unsigned i = 0u;
    for (; i < 50u && src[i] != '\0'; ++i) dst[i] = src[i];
    for (; i < 50u; ++i) dst[i] = '\0';
}

static void fill_name(char dst[10], const char *src) {
    unsigned i = 0u;
    for (; i < 10u && src[i] != '\0'; ++i) dst[i] = src[i];
    for (; i < 10u; ++i) dst[i] = '\0';
}

/* У прошивці ці три функції складають повідомлення пакувальниками MAVLink
   і кладуть їх у чергу телеметрії. Тут — друк, щоб потік було видно. */
static void send_statustext(const mav_statustext_t *m, uint32_t now_ms) {
    const char *sev = (m->severity == MAV_SEVERITY_CRITICAL) ? "CRITICAL"
                    : (m->severity == MAV_SEVERITY_WARNING)  ? "WARNING"
                                                             : "INFO";
    printf("      [%6.2f] STATUSTEXT %-8s %.50s\n", (double)now_ms / 1000.0, sev, m->text);
}

static void send_heartbeat(const mav_heartbeat_t *m, uint32_t now_ms) {
    printf("      [%6.2f] HEARTBEAT  base_mode=0x%02X custom_mode=%u\n",
           (double)now_ms / 1000.0, m->base_mode, m->custom_mode);
}

static void send_named_value(const mav_named_value_float_t *m) {
    printf("      [%6.2f] NAMED_VALUE_FLOAT %.10s = %.2f\n",
           (double)m->time_boot_ms / 1000.0, m->name, (double)m->value);
}

static void event_message(takeover_event_t e, mav_statustext_t *out) {
    switch (e) {
        case TK_EVT_OVERRIDE_BEGIN:
            out->severity = MAV_SEVERITY_WARNING;
            fill_text(out->text, "Pilot takeover: stick deflection > threshold");
            break;
        case TK_EVT_MANUAL_FULL:
            out->severity = MAV_SEVERITY_WARNING;
            fill_text(out->text, "Manual override: full pilot authority");
            break;
        case TK_EVT_HANDBACK_ARMED:
            out->severity = MAV_SEVERITY_INFO;
            fill_text(out->text, "Sticks centered: handback timer running");
            break;
        case TK_EVT_AUTO_RESUMED:
            out->severity = MAV_SEVERITY_INFO;
            fill_text(out->text, "Autopilot resumed from current position");
            break;
        case TK_EVT_THROTTLE_ENGAGED:
            out->severity = MAV_SEVERITY_INFO;
            fill_text(out->text, "Throttle lever moved: speed loop to pilot");
            break;
        case TK_EVT_RC_LOST:
            out->severity = MAV_SEVERITY_CRITICAL;
            fill_text(out->text, "RC lost during override: failsafe RTL");
            break;
        case TK_EVT_FENCE_RECLAIM:
            out->severity = MAV_SEVERITY_CRITICAL;
            fill_text(out->text, "Geofence: autopilot reclaims control");
            break;
        default:
            out->severity = MAV_SEVERITY_INFO;
            fill_text(out->text, "Takeover: unknown event");
            break;
    }
}

/* Стан автомата їде в custom_mode. Нумерація наша: у ArduPlane своя
   (MANUAL=0, FBWA=5, AUTO=10, RTL=11), і плутати їх не можна. */
static uint32_t custom_mode_of(takeover_state_t s) {
    return (uint32_t)s;
}

static uint8_t base_mode_of(takeover_state_t s) {
    uint8_t flags = MAV_MODE_FLAG_SAFETY_ARMED | MAV_MODE_FLAG_CUSTOM_MODE_ENABLED;
    if (s == TAKEOVER_AUTO_NAV) {
        flags |= MAV_MODE_FLAG_AUTO_ENABLED;
    } else {
        flags |= MAV_MODE_FLAG_MANUAL_INPUT_ENABLED | MAV_MODE_FLAG_STABILIZE_ENABLED;
    }
    return flags;
}

void annunciate_events(annunciator_t *an, takeover_t *t, uint32_t now_ms) {
    if (!an || !t) return;
    takeover_event_t e;
    while (takeover_pop_event(t, &e)) {
        mav_statustext_t msg;
        event_message(e, &msg);
        send_statustext(&msg, now_ms);
    }
}

void annunciate_stream(annunciator_t *an, const takeover_status_t *st, uint32_t now_ms) {
    if (!an || !st) return;

    if (!an->started) {
        an->started = true;
        an->last_heartbeat_ms = now_ms;
        an->last_named_ms = now_ms;
    }

    if ((uint32_t)(now_ms - an->last_heartbeat_ms) >= HEARTBEAT_PERIOD_MS) {
        an->last_heartbeat_ms = now_ms;
        mav_heartbeat_t hb;
        hb.base_mode = base_mode_of(st->state);
        hb.custom_mode = custom_mode_of(st->state);
        send_heartbeat(&hb, now_ms);
    }

    /* Коефіцієнт змішування окремого поля в NAV_CONTROLLER_OUTPUT не має,
       тому α йде named-значенням — його наземна станція кладе на графік. */
    if ((uint32_t)(now_ms - an->last_named_ms) >= NAMED_VALUE_PERIOD_MS) {
        an->last_named_ms = now_ms;
        if (st->alpha > 0.0f || st->alpha_throttle > 0.0f) {
            mav_named_value_float_t nv;
            fill_name(nv.name, "BLEND_A");
            nv.value = st->alpha;
            nv.time_boot_ms = now_ms;
            send_named_value(&nv);
        }
    }
}
