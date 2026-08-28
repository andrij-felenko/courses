#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <math.h>
#include <stdio.h>
#include <assert.h>

#define EVENT_QUEUE_CAPACITY     32
#define TARGET_TRACK_TIMEOUT_MS  3000
#define ACQUIRE_TIMEOUT_MS       4000
#define VERIFY_TIMEOUT_MS        2000
#define OBSTACLE_CLEAR_MARGIN_M  15.0f

/* ── 1. Ідентифікатори сигналів та станів ── */
typedef enum {
    SIG_ENTRY = 0,
    SIG_EXIT,
    SIG_INIT,
    SIG_TICK,
    SIG_CMD_START,
    SIG_CANDIDATE_DETECTED,
    SIG_TARGET_LOCKED,
    SIG_TARGET_LOST,
    SIG_WITHIN_ENGAGE_RANGE,
    SIG_PAYLOAD_RELEASED,
    SIG_VERIFY_COMPLETE,
    SIG_OBSTACLE_DETECTED,
    SIG_OBSTACLE_CLEARED,
    SIG_BATTERY_CRITICAL,
    SIG_GEOFENCE_BREACH,
    SIG_CMD_ABORT
} mission_sig_t;

typedef enum {
    RES_HANDLED = 0,
    RES_IGNORED,
    RES_TRANSITION,
    RES_SUPER
} fsm_res_t;

typedef enum {
    STATE_ID_NONE = 0,
    STATE_ID_OPERATIONAL_SUPER,
    STATE_ID_IDLE,
    STATE_ID_SEARCH,
    STATE_ID_ACQUIRE,
    STATE_ID_TRACK,
    STATE_ID_ENGAGE,
    STATE_ID_VERIFY,
    STATE_ID_AVOID,
    STATE_ID_RECOVERY_SUPER,
    STATE_ID_RTB,
    STATE_ID_ABORT
} state_id_t;

/* ── 2. Структури даних телеметрії, цілей та подій ── */
typedef struct {
    uint32_t id;
    float lat;
    float lon;
    float alt;
    float confidence;
    float distance_m;
    float nis;
} target_desc_t;

typedef struct {
    mission_sig_t sig;
    uint32_t timestamp_ms;
    union {
        target_desc_t target;
        float value;
        uint32_t code;
    } param;
} event_t;

typedef struct {
    float battery_voltage;
    float battery_soc;           /* 0.0 .. 1.0 */
    float energy_remaining_wh;
    float dist_to_home_m;
    float wind_speed_ms;
    float wind_heading_rad;
    float uav_heading_rad;
    float cruise_speed_ms;
    float cruise_power_w;
    bool gnss_3d_fix;
    float gnss_hdop;
    float ekf_nis;
    bool geofence_ok;
    bool payload_armed;
    uint8_t payload_remaining;
    float obstacle_distance_m;
} telemetry_t;

/* ── 3. Безблокувальна черга подій SPSC ── */
typedef struct {
    event_t buffer[EVENT_QUEUE_CAPACITY];
    volatile uint32_t head;
    volatile uint32_t tail;
} event_queue_t;

static void queue_init(event_queue_t *q) {
    q->head = 0;
    q->tail = 0;
}

static bool queue_push(event_queue_t *q, const event_t *evt) {
    uint32_t next_head = (q->head + 1) % EVENT_QUEUE_CAPACITY;
    if (next_head == q->tail) {
        return false; /* Буфер переповнено */
    }
    q->buffer[q->head] = *evt;
    q->head = next_head;
    return true;
}

static bool queue_pop(event_queue_t *q, event_t *evt) {
    if (q->tail == q->head) {
        return false; /* Черга порожня */
    }
    *evt = q->buffer[q->tail];
    q->tail = (q->tail + 1) % EVENT_QUEUE_CAPACITY;
    return true;
}

/* ── 4. Контекст місійного автомата ── */
struct mission_fsm_s;
typedef fsm_res_t (*state_handler_t)(struct mission_fsm_s *ctx, const event_t *evt);

typedef struct mission_fsm_s {
    state_handler_t state;
    state_handler_t history_state;
    state_id_t state_id;
    state_id_t history_state_id;

    telemetry_t telem;
    target_desc_t active_target;
    event_queue_t queue;

    uint32_t state_entry_time_ms;
    uint32_t last_target_seen_ms;
    uint32_t current_time_ms;
    uint32_t transition_count;
    bool payload_release_triggered;
    uint32_t search_grid_leg;
} mission_fsm_t;

/* ── 5. Прототипи функцій станів ── */
fsm_res_t state_op_super(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_idle(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_search(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_acquire(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_track(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_engage(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_verify(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_avoid(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_rec_super(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_rtb(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_abort(mission_fsm_t *ctx, const event_t *evt);

/* Допоміжний макрос переходу */
#define TRANSITION_TO(target_fn, target_id_enum) \
    do { \
        if (ctx->state != NULL) { \
            event_t exit_e = { .sig = SIG_EXIT, .timestamp_ms = ctx->current_time_ms }; \
            ctx->state(ctx, &exit_e); \
        } \
        ctx->state = (target_fn); \
        ctx->state_id = (target_id_enum); \
        ctx->state_entry_time_ms = ctx->current_time_ms; \
        ctx->transition_count++; \
        event_t entry_e = { .sig = SIG_ENTRY, .timestamp_ms = ctx->current_time_ms }; \
        ctx->state(ctx, &entry_e); \
        return RES_TRANSITION; \
    } while (0)

/* ── 6. Охоронні умови (Guard Predicates) ── */
static bool guard_energy_sufficient_for_rtb(const telemetry_t *t) {
    if (t->cruise_speed_ms <= 1.0f) return false;
    
    /* Проєкція вітру на курс повернення */
    float headwind = t->wind_speed_ms * cosf(t->wind_heading_rad - t->uav_heading_rad);
    float ground_speed = t->cruise_speed_ms - headwind;
    if (ground_speed < 3.0f) ground_speed = 3.0f;

    float time_rtb_h = (t->dist_to_home_m / ground_speed) / 3600.0f;
    float energy_rtb_wh = t->cruise_power_w * time_rtb_h;
    float energy_reserve_wh = energy_rtb_wh * 0.20f; /* 20% гарантованого резерву */

    return t->energy_remaining_wh > (energy_rtb_wh + energy_reserve_wh);
}

static bool guard_sensors_healthy(const telemetry_t *t) {
    return t->gnss_3d_fix && (t->gnss_hdop <= 1.3f) && (t->ekf_nis <= 1.0f);
}

static bool guard_target_nis_valid(float nis) {
    return nis <= 5.99f; /* 95% поріг розподілу Chi-Square для 2 DOF */
}

/* ── 7. Реалізація функцій станів ── */

/* Суперстан OPERATIONAL */
fsm_res_t state_op_super(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_BATTERY_CRITICAL:
            TRANSITION_TO(state_rtb, STATE_ID_RTB);

        case SIG_GEOFENCE_BREACH:
            TRANSITION_TO(state_abort, STATE_ID_ABORT);

        case SIG_CMD_ABORT:
            TRANSITION_TO(state_rtb, STATE_ID_RTB);

        case SIG_OBSTACLE_DETECTED:
            TRANSITION_TO(state_avoid, STATE_ID_AVOID);

        case SIG_TICK:
            if (!guard_energy_sufficient_for_rtb(&ctx->telem)) {
                TRANSITION_TO(state_rtb, STATE_ID_RTB);
            }
            return RES_HANDLED;

        default:
            return RES_IGNORED;
    }
}

/* Стан IDLE */
fsm_res_t state_idle(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;

        case SIG_CMD_START:
            if (guard_sensors_healthy(&ctx->telem) && ctx->telem.geofence_ok && 
                guard_energy_sufficient_for_rtb(&ctx->telem)) {
                ctx->search_grid_leg = 1;
                TRANSITION_TO(state_search, STATE_ID_SEARCH);
            }
            return RES_HANDLED;

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан SEARCH */
fsm_res_t state_search(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            ctx->history_state = state_search;
            ctx->history_state_id = STATE_ID_SEARCH;
            return RES_HANDLED;

        case SIG_CANDIDATE_DETECTED:
            if (evt->param.target.confidence >= 0.55f && ctx->telem.geofence_ok) {
                ctx->active_target = evt->param.target;
                ctx->last_target_seen_ms = ctx->current_time_ms;
                TRANSITION_TO(state_acquire, STATE_ID_ACQUIRE);
            }
            return RES_HANDLED;

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан ACQUIRE */
fsm_res_t state_acquire(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;

        case SIG_TARGET_LOCKED:
            if (evt->param.target.confidence >= 0.80f && 
                guard_target_nis_valid(evt->param.target.nis) &&
                guard_sensors_healthy(&ctx->telem) &&
                guard_energy_sufficient_for_rtb(&ctx->telem)) {
                ctx->active_target = evt->param.target;
                ctx->last_target_seen_ms = ctx->current_time_ms;
                TRANSITION_TO(state_track, STATE_ID_TRACK);
            }
            return RES_HANDLED;

        case SIG_TICK:
            if (ctx->current_time_ms - ctx->state_entry_time_ms > ACQUIRE_TIMEOUT_MS) {
                TRANSITION_TO(state_search, STATE_ID_SEARCH);
            }
            return state_op_super(ctx, evt);

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан TRACK */
fsm_res_t state_track(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            ctx->history_state = state_track;
            ctx->history_state_id = STATE_ID_TRACK;
            return RES_HANDLED;

        case SIG_WITHIN_ENGAGE_RANGE:
            if (ctx->telem.payload_armed && ctx->telem.payload_remaining > 0 &&
                ctx->telem.geofence_ok && guard_energy_sufficient_for_rtb(&ctx->telem)) {
                TRANSITION_TO(state_engage, STATE_ID_ENGAGE);
            }
            return RES_HANDLED;

        case SIG_TARGET_LOST:
        case SIG_TICK:
            if (ctx->current_time_ms - ctx->last_target_seen_ms > TARGET_TRACK_TIMEOUT_MS) {
                TRANSITION_TO(state_search, STATE_ID_SEARCH);
            }
            return state_op_super(ctx, evt);

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан ENGAGE */
fsm_res_t state_engage(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            ctx->payload_release_triggered = true;
            if (ctx->telem.payload_remaining > 0) {
                ctx->telem.payload_remaining--;
            }
            return RES_HANDLED;

        case SIG_PAYLOAD_RELEASED:
            TRANSITION_TO(state_verify, STATE_ID_VERIFY);

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан VERIFY */
fsm_res_t state_verify(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;

        case SIG_VERIFY_COMPLETE:
        case SIG_TICK:
            if (ctx->current_time_ms - ctx->state_entry_time_ms >= VERIFY_TIMEOUT_MS) {
                if (ctx->telem.payload_remaining > 0 && guard_energy_sufficient_for_rtb(&ctx->telem)) {
                    TRANSITION_TO(state_search, STATE_ID_SEARCH);
                } else {
                    TRANSITION_TO(state_rtb, STATE_ID_RTB);
                }
            }
            return RES_HANDLED;

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан AVOID (Обхід перешкоди) */
fsm_res_t state_avoid(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;

        case SIG_OBSTACLE_CLEARED:
            /* Повернення до збереженого стану через History */
            if (ctx->history_state != NULL) {
                TRANSITION_TO(ctx->history_state, ctx->history_state_id);
            } else {
                TRANSITION_TO(state_search, STATE_ID_SEARCH);
            }

        default:
            return state_op_super(ctx, evt);
    }
}

/* Суперстан RECOVERY */
fsm_res_t state_rec_super(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;
        default:
            return RES_IGNORED;
    }
}

/* Стан RTB */
fsm_res_t state_rtb(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;
        default:
            return state_rec_super(ctx, evt);
    }
}

/* Стан ABORT */
fsm_res_t state_abort(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;
        default:
            return state_rec_super(ctx, evt);
    }
}

/* ── 8. Ініціалізація та виконання циклу RTC ── */
void mission_fsm_init(mission_fsm_t *ctx, const telemetry_t *init_telem) {
    memset(ctx, 0, sizeof(*ctx));
    ctx->telem = *init_telem;
    queue_init(&ctx->queue);
    
    ctx->state = state_idle;
    ctx->state_id = STATE_ID_IDLE;
    ctx->history_state = state_search;
    ctx->history_state_id = STATE_ID_SEARCH;

    event_t init_evt = { .sig = SIG_ENTRY, .timestamp_ms = 0 };
    ctx->state(ctx, &init_evt);
}

void mission_fsm_process_queue(mission_fsm_t *ctx) {
    event_t evt;
    while (queue_pop(&ctx->queue, &evt)) {
        ctx->current_time_ms = evt.timestamp_ms;
        if (ctx->state != NULL) {
            ctx->state(ctx, &evt);
        }
    }
}

bool mission_fsm_post_event(mission_fsm_t *ctx, const event_t *evt) {
    return queue_push(&ctx->queue, evt);
}

/* ── 9. Модуль автоматизованого тестування C ── */
void run_c_fsm_tests(void) {
    telemetry_t telem = {
        .battery_voltage = 24.5f,
        .battery_soc = 0.95f,
        .energy_remaining_wh = 140.0f,
        .dist_to_home_m = 2000.0f,
        .wind_speed_ms = 3.0f,
        .wind_heading_rad = 0.0f,
        .uav_heading_rad = 0.0f,
        .cruise_speed_ms = 20.0f,
        .cruise_power_w = 220.0f,
        .gnss_3d_fix = true,
        .gnss_hdop = 0.8f,
        .ekf_nis = 0.2f,
        .geofence_ok = true,
        .payload_armed = true,
        .payload_remaining = 2,
        .obstacle_distance_m = 50.0f
    };

    mission_fsm_t fsm;
    mission_fsm_init(&fsm, &telem);
    assert(fsm.state_id == STATE_ID_IDLE);

    /* Тест 1: Старт місії -> SEARCH */
    event_t e_start = { .sig = SIG_CMD_START, .timestamp_ms = 100 };
    mission_fsm_post_event(&fsm, &e_start);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_SEARCH);

    /* Тест 2: Виявлення кандидата -> ACQUIRE */
    event_t e_cand = {
        .sig = SIG_CANDIDATE_DETECTED,
        .timestamp_ms = 500,
        .param.target = { .id = 10, .confidence = 0.70f, .nis = 0.5f }
    };
    mission_fsm_post_event(&fsm, &e_cand);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_ACQUIRE);

    /* Тест 3: Підтвердження цілі з валідним NIS -> TRACK */
    event_t e_lock = {
        .sig = SIG_TARGET_LOCKED,
        .timestamp_ms = 900,
        .param.target = { .id = 10, .confidence = 0.89f, .nis = 1.2f }
    };
    mission_fsm_post_event(&fsm, &e_lock);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_TRACK);

    /* Тест 4: Перешкода під час супроводу -> AVOID -> повернення через History в TRACK */
    event_t e_obs = { .sig = SIG_OBSTACLE_DETECTED, .timestamp_ms = 1200 };
    mission_fsm_post_event(&fsm, &e_obs);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_AVOID);

    event_t e_clear = { .sig = SIG_OBSTACLE_CLEARED, .timestamp_ms = 1800 };
    mission_fsm_post_event(&fsm, &e_clear);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_TRACK);

    /* Тест 5: Зближення на дистанцію ураження -> ENGAGE -> VERIFY */
    event_t e_range = { .sig = SIG_WITHIN_ENGAGE_RANGE, .timestamp_ms = 2200 };
    mission_fsm_post_event(&fsm, &e_range);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_ENGAGE);
    assert(fsm.payload_release_triggered == true);

    event_t e_rel = { .sig = SIG_PAYLOAD_RELEASED, .timestamp_ms = 2300 };
    mission_fsm_post_event(&fsm, &e_rel);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_VERIFY);

    /* Тест 6: Завершення верифікації -> SEARCH (залишився 1 снаряд) */
    event_t e_ver = { .sig = SIG_VERIFY_COMPLETE, .timestamp_ms = 4500 };
    mission_fsm_post_event(&fsm, &e_ver);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_SEARCH);

    /* Тест 7: Failsafe за енергетичним дефіцитом -> RTB */
    fsm.telem.energy_remaining_wh = 12.0f;
    event_t e_tick = { .sig = SIG_TICK, .timestamp_ms = 5000 };
    mission_fsm_post_event(&fsm, &e_tick);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_RTB);

    printf("ALL MISSION HSM C UNIT TESTS PASSED SUCCESSFULLY!\n");
}
