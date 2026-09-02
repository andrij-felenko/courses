#include "fs_status.h"

#include <stdio.h>
#include <string.h>

uint8_t fs_action_for(uint32_t fault_bit, uint32_t faults,
                      const fs_param_block_t *p, uint8_t *arbiter_out)
{
    uint8_t arb = FS_ARB_NONE;
    uint8_t act = FS_ACTION_NONE;

    switch (fault_bit) {
    case FS_FAULT_RC_LOST:
        arb = FS_ARB_RC_LINK;
        switch ((int)fs_params_get(p, FS_P_THR_ENABLE)) {
        case 0: act = FS_ACTION_NONE; break;
        case 1: act = FS_ACTION_RTL;  break;
        case 2: act = FS_ACTION_WARN; break;  /* продовжити місію */
        /* 3 — вимкнено, поки живий канал телеметрії; зник і він — повертаємось */
        default: act = (faults & FS_FAULT_GCS_LOST) ? FS_ACTION_RTL : FS_ACTION_WARN; break;
        }
        break;

    case FS_FAULT_GCS_LOST:
        arb = FS_ARB_GCS;
        switch ((int)fs_params_get(p, FS_P_GCS_ENABLE)) {
        case 0: act = FS_ACTION_NONE; break;
        case 1: act = FS_ACTION_RTL;  break;
        default: act = FS_ACTION_LAND; break;
        }
        break;

    case FS_FAULT_GNSS_HDOP:
        arb = FS_ARB_NAV;
        act = FS_ACTION_WARN;  /* якість погіршилась, фіксацію ще не втрачено */
        break;

    case FS_FAULT_GNSS_LOST:
    case FS_FAULT_EKF_DIVERGED:
        arb = FS_ARB_NAV;
        act = FS_ACTION_ALTHOLD;  /* безсупутниковий режим утримання висоти */
        break;

    case FS_FAULT_BATT_LOW:
        arb = FS_ARB_BATT;
        switch ((int)fs_params_get(p, FS_P_BATT_ACT)) {
        case 1: act = FS_ACTION_WARN; break;
        case 3: act = FS_ACTION_LAND; break;
        default: act = FS_ACTION_RTL; break;  /* 2 — RTL, 4 — SmartRTL тим самим кодом */
        }
        break;

    case FS_FAULT_BATT_CRIT:
        arb = FS_ARB_BATT;
        act = FS_ACTION_LAND;  /* безумовно, конфігурацією не скасовується */
        break;

    case FS_FAULT_FENCE_RADIUS:
    case FS_FAULT_FENCE_ALT:
        arb = FS_ARB_FENCE;
        if (fs_params_get(p, FS_P_FENCE_ENABLE) == 0.0f) {
            act = FS_ACTION_NONE;
        } else {
            switch ((int)fs_params_get(p, FS_P_FENCE_ACT)) {
            case 2: act = FS_ACTION_LAND; break;
            /* 3 — зависання (Loiter/Brake): утримання позиції й висоти */
            case 3: act = FS_ACTION_ALTHOLD; break;
            default: act = FS_ACTION_RTL; break;
            }
        }
        break;

    case FS_FAULT_ESC_FAIL:
        arb = FS_ARB_PROPULSION;
        act = FS_ACTION_LAND;  /* із втратою променя тримаємось лише до землі */
        break;

    case FS_FAULT_ATTITUDE_LOST:
        arb = FS_ARB_NAV;
        act = FS_ACTION_TERMINATE;  /* без горизонту керований політ неможливий */
        break;

    default:
        break;
    }

    if (arbiter_out != NULL)
        *arbiter_out = arb;
    return act;
}

fs_decision_t fs_decide(uint32_t faults, const fs_param_block_t *p)
{
    fs_decision_t d = { FS_ACTION_NONE, FS_ARB_NONE };

    for (int i = 0; i < 32; ++i) {
        uint32_t bit = 1u << i;
        uint8_t arb, act;

        if ((faults & bit) == 0u || (bit & FS_FAULT_ALL) == 0u)
            continue;
        act = fs_action_for(bit, faults, p, &arb);
        if (act > d.action) {   /* суворіша дія перекриває, за рівних виграє перша */
            d.action = act;
            d.arbiter = arb;
        }
    }

    d.action = fs_degrade(d.action, faults);
    return d;
}

uint8_t fs_degrade(uint8_t action, uint32_t faults)
{
    /* Повернення додому потребує позиції: без GNSS і зі зруйнованим фільтром
     * замість RTL сідаємо на місці. */
    if (action == FS_ACTION_RTL &&
        (faults & (FS_FAULT_GNSS_LOST | FS_FAULT_EKF_DIVERGED)) != 0u)
        action = FS_ACTION_LAND;

    /* Без оцінки орієнтації не виконується навіть посадка. */
    if ((faults & FS_FAULT_ATTITUDE_LOST) != 0u && action >= FS_ACTION_ALTHOLD)
        action = FS_ACTION_TERMINATE;

    return action;
}

uint8_t fs_severity_of(uint32_t fault_bit)
{
    switch (fault_bit) {
    case FS_FAULT_ATTITUDE_LOST: return FS_SEV_EMERGENCY;
    case FS_FAULT_BATT_CRIT:
    case FS_FAULT_FENCE_RADIUS:
    case FS_FAULT_FENCE_ALT:     return FS_SEV_ALERT;
    case FS_FAULT_RC_LOST:
    case FS_FAULT_GCS_LOST:
    case FS_FAULT_GNSS_LOST:
    case FS_FAULT_EKF_DIVERGED:
    case FS_FAULT_ESC_FAIL:      return FS_SEV_CRITICAL;
    case FS_FAULT_BATT_LOW:
    case FS_FAULT_GNSS_HDOP:     return FS_SEV_WARNING;
    default:                     return FS_SEV_INFO;
    }
}

static void put_u16(uint8_t *p, uint16_t v) { p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); }
static void put_u32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)v;         p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16); p[3] = (uint8_t)(v >> 24);
}
static void put_u64(uint8_t *p, uint64_t v) { put_u32(p, (uint32_t)v); put_u32(p + 4, (uint32_t)(v >> 32)); }
static void put_f32(uint8_t *p, float f) { uint32_t b; memcpy(&b, &f, 4); put_u32(p, b); }
static uint16_t get_u16(const uint8_t *p) { return (uint16_t)(p[0] | (p[1] << 8)); }
static uint32_t get_u32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static uint64_t get_u64(const uint8_t *p) { return (uint64_t)get_u32(p) | ((uint64_t)get_u32(p + 4) << 32); }
static float get_f32(const uint8_t *p) { uint32_t b = get_u32(p); float f; memcpy(&f, &b, 4); return f; }

uint32_t fs_frame_pack(const failsafe_telemetry_t *t, uint8_t *buf, uint32_t buf_sz)
{
    if (buf_sz < FS_FRAME_LEN)
        return 0;
    put_u64(buf + 0, t->timestamp_us);
    put_u32(buf + 8, t->active_faults_mask);
    buf[12] = t->active_action;
    buf[13] = t->executing_arbiter;
    put_u16(buf + 14, t->rc_valid_frames_sec);
    put_f32(buf + 16, t->gnss_hdop);
    put_f32(buf + 20, t->batt_cell_min_v);
    put_f32(buf + 24, t->distance_to_fence_m);
    return FS_FRAME_LEN;
}

bool fs_frame_unpack(const uint8_t *buf, uint32_t len, failsafe_telemetry_t *out)
{
    if (len < FS_FRAME_LEN)
        return false;
    out->timestamp_us        = get_u64(buf + 0);
    out->active_faults_mask  = get_u32(buf + 8);
    out->active_action       = buf[12];
    out->executing_arbiter   = buf[13];
    out->rc_valid_frames_sec = get_u16(buf + 14);
    out->gnss_hdop           = get_f32(buf + 16);
    out->batt_cell_min_v     = get_f32(buf + 20);
    out->distance_to_fence_m = get_f32(buf + 24);
    /* Чужий кадр міг прийти з новішої прошивки з невідомими нам бітами. */
    return (out->active_faults_mask & ~FS_FAULT_ALL) == 0u &&
           out->active_action <= FS_ACTION_TERMINATE;
}

uint8_t fs_statustext(uint32_t fault_bit, const uint32_t faults, const fs_param_block_t *p,
                      const failsafe_telemetry_t *t, char *out, uint32_t sz)
{
    const char *act = fs_action_name(fs_degrade(fs_action_for(fault_bit, faults, p, NULL), faults));

    switch (fault_bit) {
    case FS_FAULT_RC_LOST:
        snprintf(out, sz, "RC link lost > %.1fs -> %s",
                 (double)fs_params_get(p, FS_P_RC_TIMEOUT), act);
        break;
    case FS_FAULT_GCS_LOST:
        snprintf(out, sz, "GCS heartbeat timeout %.1fs -> %s",
                 (double)fs_params_get(p, FS_P_GCS_TIMEOUT), act);
        break;
    case FS_FAULT_GNSS_HDOP:
        snprintf(out, sz, "GNSS HDOP %.2f > %.2f, position degraded",
                 (double)t->gnss_hdop, (double)fs_params_get(p, FS_P_GNSS_HDOP_MAX));
        break;
    case FS_FAULT_GNSS_LOST:
        snprintf(out, sz, "GNSS fix lost for %.1fs (HDOP %.2f) -> %s",
                 (double)fs_params_get(p, FS_P_GNSS_TIMEOUT), (double)t->gnss_hdop, act);
        break;
    case FS_FAULT_EKF_DIVERGED:
        snprintf(out, sz, "EKF innovation ratio above %.2f -> %s",
                 (double)fs_params_get(p, FS_P_EKF_THRESH), act);
        break;
    case FS_FAULT_BATT_LOW:
        snprintf(out, sz, "Battery low %.2fV/cell < %.2fV -> %s",
                 (double)t->batt_cell_min_v, (double)fs_params_get(p, FS_P_BATT_LOW_V), act);
        break;
    case FS_FAULT_BATT_CRIT:
        snprintf(out, sz, "Battery critical %.2fV/cell < %.2fV -> %s",
                 (double)t->batt_cell_min_v, (double)fs_params_get(p, FS_P_BATT_CRIT_V), act);
        break;
    case FS_FAULT_FENCE_RADIUS:
        snprintf(out, sz, "Fence radius %.0fm breached (%.1fm to boundary) -> %s",
                 (double)fs_params_get(p, FS_P_FENCE_RADIUS),
                 (double)t->distance_to_fence_m, act);
        break;
    case FS_FAULT_FENCE_ALT:
        snprintf(out, sz, "Fence ceiling %.0fm breached -> %s",
                 (double)fs_params_get(p, FS_P_FENCE_ALT_MAX), act);
        break;
    case FS_FAULT_ESC_FAIL:
        snprintf(out, sz, "ESC/motor failure -> %s", act);
        break;
    case FS_FAULT_ATTITUDE_LOST:
        snprintf(out, sz, "Attitude estimate lost -> %s", act);
        break;
    default:
        snprintf(out, sz, "Unknown fault 0x%08lX", (unsigned long)fault_bit);
        break;
    }
    return fs_severity_of(fault_bit);
}

uint8_t fs_statustext_recovered(const fs_param_block_t *p, char *out, uint32_t sz)
{
    snprintf(out, sz, "RC link recovered, manual control restored after %.1fs",
             (double)fs_params_get(p, FS_P_RC_RECOVER));
    return FS_SEV_INFO;
}

const char *fs_action_name(uint8_t action)
{
    switch (action) {
    case FS_ACTION_NONE:      return "FS_ACTION_NONE";
    case FS_ACTION_WARN:      return "FS_ACTION_WARN";
    case FS_ACTION_ALTHOLD:   return "FS_ACTION_ALTHOLD";
    case FS_ACTION_RTL:       return "FS_ACTION_RTL";
    case FS_ACTION_LAND:      return "FS_ACTION_LAND";
    case FS_ACTION_TERMINATE: return "FS_ACTION_TERMINATE";
    default:                  return "FS_ACTION_?";
    }
}

const char *fs_arbiter_name(uint8_t arbiter)
{
    switch (arbiter) {
    case FS_ARB_NONE:       return "none";
    case FS_ARB_RC_LINK:    return "rc_link";
    case FS_ARB_GCS:        return "gcs_link";
    case FS_ARB_NAV:        return "navigation";
    case FS_ARB_BATT:       return "battery";
    case FS_ARB_FENCE:      return "geofence";
    case FS_ARB_PROPULSION: return "propulsion";
    default:                return "?";
    }
}

const char *fs_fault_name(uint32_t fault_bit)
{
    switch (fault_bit) {
    case FS_FAULT_RC_LOST:       return "RC_LOST";
    case FS_FAULT_GCS_LOST:      return "GCS_LOST";
    case FS_FAULT_GNSS_HDOP:     return "GNSS_HDOP";
    case FS_FAULT_GNSS_LOST:     return "GNSS_LOST";
    case FS_FAULT_EKF_DIVERGED:  return "EKF_DIVERGED";
    case FS_FAULT_BATT_LOW:      return "BATT_LOW";
    case FS_FAULT_BATT_CRIT:     return "BATT_CRIT";
    case FS_FAULT_FENCE_RADIUS:  return "FENCE_RADIUS";
    case FS_FAULT_FENCE_ALT:     return "FENCE_ALT";
    case FS_FAULT_ESC_FAIL:      return "ESC_FAIL";
    case FS_FAULT_ATTITUDE_LOST: return "ATTITUDE_LOST";
    default:                     return "?";
    }
}

const char *fs_severity_name(uint8_t sev)
{
    switch (sev) {
    case FS_SEV_EMERGENCY: return "EMERGENCY";
    case FS_SEV_ALERT:     return "ALERT";
    case FS_SEV_CRITICAL:  return "CRITICAL";
    case FS_SEV_ERROR:     return "ERROR";
    case FS_SEV_WARNING:   return "WARNING";
    case FS_SEV_NOTICE:    return "NOTICE";
    default:               return "INFO";
    }
}
