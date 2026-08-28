#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <math.h>

/* Сигнали життєвого циклу автомата */
typedef enum {
    SIG_ENTRY = 0,
    SIG_EXIT,
    SIG_INIT,
    SIG_TICK,
    SIG_CMD_START,
    SIG_CANDIDATE_FOUND,
    SIG_TARGET_CONFIRMED,
    SIG_TARGET_LOST,
    SIG_IN_ENGAGE_ZONE,
    SIG_ACTION_COMPLETE,
    SIG_OBSTACLE_DETECTED,
    SIG_OBSTACLE_CLEARED,
    SIG_BATTERY_LOW,
    SIG_GEOFENCE_BREACH
} hsm_sig_t;

typedef enum {
    HSM_HANDLED,
    HSM_IGNORED,
    HSM_TRANSITION,
    HSM_SUPER
} hsm_res_t;

/* Структура вхідної події */
typedef struct {
    hsm_sig_t sig;
    uint32_t timestamp_ms;
    union {
        float confidence;
        float distance_m;
        uint32_t target_id;
    } param;
} hsm_event_t;

/* Зріз телеметрії для Guard-предикатів */
typedef struct {
    float energy_rem_wh;
    float dist_home_m;
    float wind_speed_ms;
    float wind_heading_rad;
    float uav_heading_rad;
    float cruise_speed_ms;
    float cruise_power_w;
    bool gnss_3d_fix;
    float ekf_nis;
    bool geofence_ok;
    bool payload_armed;
    uint8_t payload_count;
} uav_telemetry_t;

struct mission_hsm_s;
typedef hsm_res_t (*state_fn_t)(struct mission_hsm_s *me, const hsm_event_t *e);

/* Контекст ієрархічного автомата */
typedef struct mission_hsm_s {
    state_fn_t state;          /* Поточний активний стан */
    state_fn_t history_state;  /* Збережений стан (Shallow/Deep History) */
    uav_telemetry_t telem;     /* Зріз сенсорної інформації */
    uint32_t active_target_id;
    uint32_t state_entry_ms;
    uint32_t target_lost_ms;
} mission_hsm_t;

/* Прототипи функцій станів */
hsm_res_t state_operational_super(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_idle(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_search(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_acquire(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_track(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_engage(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_verify(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_avoid(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_recovery_super(mission_hsm_t *me, const hsm_event_t *e);
hsm_res_t state_rtb(mission_hsm_t *me, const hsm_event_t *e);

/* Макрос атомарного переходу зі збереженням життєвого циклу */
#define HSM_TRANSITION_TO(target) \
    do { \
        hsm_event_t exit_evt = { .sig = SIG_EXIT, .timestamp_ms = e->timestamp_ms }; \
        me->state(me, &exit_evt); \
        me->state = (state_fn_t)(target); \
        me->state_entry_ms = e->timestamp_ms; \
        hsm_event_t entry_evt = { .sig = SIG_ENTRY, .timestamp_ms = e->timestamp_ms }; \
        me->state(me, &entry_evt); \
        return HSM_TRANSITION; \
    } while (0)

/* Охоронна умова: розрахунок енергетичного бюджету повернення */
static bool guard_energy_ok(const uav_telemetry_t *t) {
    if (t->cruise_speed_ms <= 1.0f) return false;
    float headwind = t->wind_speed_ms * cosf(t->wind_heading_rad - t->uav_heading_rad);
    float ground_speed = t->cruise_speed_ms - headwind;
    if (ground_speed < 3.0f) ground_speed = 3.0f;
    
    float time_rtb_h = (t->dist_home_m / ground_speed) / 3600.0f;
    float energy_rtb_wh = t->cruise_power_w * time_rtb_h;
    float energy_reserve_wh = energy_rtb_wh * 0.20f;
    return t->energy_rem_wh > (energy_rtb_wh + energy_reserve_wh);
}

/* Обробник стану SEARCH */
hsm_res_t state_search(mission_hsm_t *me, const hsm_event_t *e) {
    switch (e->sig) {
        case SIG_ENTRY:
            me->history_state = state_search;
            return HSM_HANDLED;

        case SIG_CANDIDATE_FOUND:
            if (e->param.confidence >= 0.55f && me->telem.geofence_ok) {
                HSM_TRANSITION_TO(state_acquire);
            }
            return HSM_HANDLED;

        default:
            return state_operational_super(me, e);
    }
}

/* Обробник стану ACQUIRE */
hsm_res_t state_acquire(mission_hsm_t *me, const hsm_event_t *e) {
    switch (e->sig) {
        case SIG_ENTRY:
            return HSM_HANDLED;

        case SIG_TARGET_CONFIRMED:
            if (e->param.confidence >= 0.80f && (me->telem.ekf_nis <= 5.99f) && guard_energy_ok(&me->telem)) {
                me->active_target_id = e->param.target_id;
                HSM_TRANSITION_TO(state_track);
            }
            return HSM_HANDLED;

        case SIG_TICK:
            if (e->timestamp_ms - me->state_entry_ms > 4000) {
                HSM_TRANSITION_TO(state_search);
            }
            return state_operational_super(me, e);

        default:
            return state_operational_super(me, e);
    }
}

/* Обробник стану TRACK */
hsm_res_t state_track(mission_hsm_t *me, const hsm_event_t *e) {
    switch (e->sig) {
        case SIG_ENTRY:
            me->history_state = state_track;
            return HSM_HANDLED;

        case SIG_IN_ENGAGE_ZONE:
            if (me->telem.payload_armed && (me->telem.payload_count > 0) && guard_energy_ok(&me->telem)) {
                HSM_TRANSITION_TO(state_engage);
            }
            return HSM_HANDLED;

        case SIG_TARGET_LOST:
            if (e->timestamp_ms - me->target_lost_ms > 3000) {
                HSM_TRANSITION_TO(state_search);
            }
            return HSM_HANDLED;

        default:
            return state_operational_super(me, e);
    }
}

/* Обробник суперстану OPERATIONAL (Failsafe та загальні переривання) */
hsm_res_t state_operational_super(mission_hsm_t *me, const hsm_event_t *e) {
    switch (e->sig) {
        case SIG_OBSTACLE_DETECTED:
            HSM_TRANSITION_TO(state_avoid);

        case SIG_BATTERY_LOW:
            HSM_TRANSITION_TO(state_rtb);

        case SIG_GEOFENCE_BREACH:
            HSM_TRANSITION_TO(state_recovery_super);

        case SIG_TICK:
            if (!guard_energy_ok(&me->telem)) {
                HSM_TRANSITION_TO(state_rtb);
            }
            return HSM_HANDLED;

        default:
            return HSM_IGNORED;
    }
}

/* Обробник стану AVOID (обхід перешкоди з відновленням History) */
hsm_res_t state_avoid(mission_hsm_t *me, const hsm_event_t *e) {
    switch (e->sig) {
        case SIG_ENTRY:
            return HSM_HANDLED;

        case SIG_OBSTACLE_CLEARED:
            /* Повернення до збереженого стану через History */
            if (me->history_state != NULL) {
                HSM_TRANSITION_TO(me->history_state);
            } else {
                HSM_TRANSITION_TO(state_search);
            }

        default:
            return state_operational_super(me, e);
    }
}

/* Обробник стану RTB */
hsm_res_t state_rtb(mission_hsm_t *me, const hsm_event_t *e) {
    switch (e->sig) {
        case SIG_ENTRY:
            /* Надсилання навігаційної команди RTL */
            return HSM_HANDLED;
        default:
            return HSM_IGNORED;
    }
}

/* Ініціалізація та диспетчеризація */
void mission_hsm_init(mission_hsm_t *me, const uav_telemetry_t *t) {
    me->telem = *t;
    me->state = state_search;
    me->history_state = state_search;
    hsm_event_t init_evt = { .sig = SIG_ENTRY, .timestamp_ms = 0 };
    me->state(me, &init_evt);
}

void mission_hsm_dispatch(mission_hsm_t *me, const hsm_event_t *e) {
    if (me != NULL && me->state != NULL && e != NULL) {
        me->state(me, e);
    }
}
