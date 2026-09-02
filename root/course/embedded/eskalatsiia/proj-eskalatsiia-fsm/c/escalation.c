#include "escalation.h"

#include "deadline.h"

#include <math.h>
#include <string.h>

/* Параметри платформи: логістичний ровер 350 кг */
#define ESC_BRAKING_DECEL_MPS2       2.0f
#define ESC_SAFETY_MARGIN_M          4.0f
#define ESC_SENSOR_LAG_MS            200u
/* Скільки стоїмо на місці, перш ніж почати відкат */
#define ESC_HOLD_BEFORE_BACKTRACK_MS 5000u

static void enter(EscManager* m, EscState s, uint32_t now_ms)
{
    m->state = s;
    m->state_entered_ms = now_ms;
}

void esc_init(EscManager* m, uint32_t heartbeat_timeout_ms)
{
    memset(m, 0, sizeof *m);
    esc_trail_init(&m->trail);
    m->heartbeat_timeout_ms = (heartbeat_timeout_ms > 0u) ? heartbeat_timeout_ms : 1500u;
    m->state = FSM_STATE_AUTONOMOUS;
}

/* Фіксуємо кінематичний стан і варіанти планувальника на момент тригера:
   далі апарат рухається, а оператор бачить саме ту сцену, яку йому надіслали. */
static void latch_trigger(EscManager* m, const EscInputs* in)
{
    m->active_trigger      = in->trigger;
    m->query_id++;                       /* монотонно, без повторів */
    m->request_started_ms  = in->now_ms;
    m->pose_at_request     = in->pose;
    m->speed_at_request    = in->speed_mps;
    m->selected_option_id  = 0u;

    m->options_count = (in->options_count > ESC_MAX_OPTIONS) ? (uint8_t)ESC_MAX_OPTIONS
                                                             : in->options_count;
    for (uint8_t i = 0; i < m->options_count; ++i) {
        m->options[i] = in->options[i];
    }

    m->roi_len = 0u;
    if (in->roi_jpeg != NULL && in->roi_len > 0u && in->roi_len <= ESC_ROI_MAX) {
        memcpy(m->roi, in->roi_jpeg, in->roi_len);
        m->roi_len = in->roi_len;
    }
}

static bool build_frame(EscManager* m, EscOutputs* out)
{
    EscQuery q;
    memset(&q, 0, sizeof q);

    q.query_id     = m->query_id;
    q.timestamp_ms = m->request_started_ms;
    q.deadline_ms  = (uint16_t)((m->deadline_ms > 65535u) ? 65535u : m->deadline_ms);
    q.trigger_code = m->active_trigger;

    q.position_xyz[0] = m->pose_at_request.x;
    q.position_xyz[1] = m->pose_at_request.y;
    q.position_xyz[2] = m->pose_at_request.z;
    q.velocity_xyz[0] = m->speed_at_request * cosf(m->pose_at_request.yaw);
    q.velocity_xyz[1] = m->speed_at_request * sinf(m->pose_at_request.yaw);
    q.velocity_xyz[2] = 0.0f;

    q.options_count = m->options_count;
    for (uint8_t i = 0; i < m->options_count; ++i) {
        q.options[i] = m->options[i];
    }
    q.roi_size_bytes = m->roi_len;
    if (m->roi_len > 0u) {
        memcpy(q.roi_jpeg, m->roi, m->roi_len);
    }

    size_t written = 0u;
    if (esc_pack_query(&q, out->frame, sizeof out->frame, &written) != ESC_WIRE_OK) {
        return false;
    }
    out->frame_len = written;
    return true;
}

void esc_tick(EscManager* m, const EscInputs* in, EscOutputs* out)
{
    memset(out, 0, sizeof *out);
    out->command         = ESC_CMD_CONTINUE;
    out->accept_radius_m = ESC_ACCEPT_RADIUS_M;

    /* Пріоритет нуль: апаратний тумблер пульта б'є все й безумовно скидає автомат */
    if (in->rc_override) {
        if (m->state != FSM_STATE_MANUAL_RC) {
            m->active_trigger       = ESC_TRIGGER_NONE;
            m->selected_option_id   = 0u;
            m->has_backtrack_target = false;
            enter(m, FSM_STATE_MANUAL_RC, in->now_ms);
        }
        out->command = ESC_CMD_MANUAL;
        return;
    }
    if (m->state == FSM_STATE_MANUAL_RC) {
        enter(m, FSM_STATE_AUTONOMOUS, in->now_ms);   /* тумблер відпущено */
    }

    /* Беззнакове віднімання: millis() переповнюється раз на 49.7 днів */
    const bool link_alive =
        ((uint32_t)(in->now_ms - in->last_heartbeat_ms) <= m->heartbeat_timeout_ms);

    /* Слід пишемо лише коли справді їдемо вперед */
    if (m->state == FSM_STATE_AUTONOMOUS || m->state == FSM_STATE_APPLYING_OVERRIDE) {
        esc_trail_push_if_moved(&m->trail, &in->pose);
    }

    switch (m->state) {
        case FSM_STATE_AUTONOMOUS:
            if (in->trigger != ESC_TRIGGER_NONE && in->options_count > 0u) {
                latch_trigger(m, in);
                m->deadline_ms = esc_deadline_ms(in->dist_to_obstacle_m,
                                                 in->speed_mps,
                                                 ESC_BRAKING_DECEL_MPS2,
                                                 ESC_SAFETY_MARGIN_M,
                                                 ESC_SENSOR_LAG_MS);
                if (m->deadline_ms == 0u) {
                    /* Часу на діалог немає — гальмуємо, оператор дізнається постфактум */
                    enter(m, FSM_STATE_FAILSAFE_HOLD, in->now_ms);
                    out->command = ESC_CMD_HOLD;
                } else {
                    enter(m, FSM_STATE_ESCALATION_REQUESTED, in->now_ms);
                }
            }
            break;

        case FSM_STATE_ESCALATION_REQUESTED:
            if (build_frame(m, out)) {
                enter(m, FSM_STATE_AWAITING_OPERATOR, in->now_ms);
            } else {
                /* Спитати нікого не вийшло — далі поводимося як при мовчанні */
                enter(m, FSM_STATE_FAILSAFE_HOLD, in->now_ms);
                out->command = ESC_CMD_HOLD;
            }
            break;

        case FSM_STATE_AWAITING_OPERATOR: {
            const uint32_t elapsed = (uint32_t)(in->now_ms - m->request_started_ms);
            if (!link_alive || elapsed >= m->deadline_ms) {
                enter(m, FSM_STATE_FAILSAFE_HOLD, in->now_ms);
                out->command = ESC_CMD_HOLD;
            }
            /* До дедлайну рух триває: дедлайн і рахували так, щоб гальма ще встигли */
            break;
        }

        case FSM_STATE_APPLYING_OVERRIDE:
            out->command             = ESC_CMD_FOLLOW_OPTION;
            out->selected_option_id  = m->selected_option_id;
            if (in->maneuver_done) {
                m->active_trigger = ESC_TRIGGER_NONE;
                enter(m, FSM_STATE_AUTONOMOUS, in->now_ms);
            }
            break;

        case FSM_STATE_FAILSAFE_HOLD:
            out->command = ESC_CMD_HOLD;
            if ((uint32_t)(in->now_ms - m->state_entered_ms) > ESC_HOLD_BEFORE_BACKTRACK_MS) {
                m->has_backtrack_target = false;
                enter(m, FSM_STATE_FAILSAFE_BACKTRACK, in->now_ms);
            }
            break;

        case FSM_STATE_FAILSAFE_BACKTRACK:
            /* Знімаємо точки, доки не знайдемо ту, до якої ще треба доїхати */
            for (;;) {
                if (m->has_backtrack_target &&
                    esc_dist2d(&in->pose, &m->backtrack_target) > ESC_BACKTRACK_RADIUS_M) {
                    break;
                }
                m->has_backtrack_target = false;
                if (!esc_trail_pop_reverse(&m->trail, &m->backtrack_target)) {
                    break;   /* історія вичерпана */
                }
                m->has_backtrack_target = true;
            }
            if (m->has_backtrack_target) {
                out->command         = ESC_CMD_GOTO_POINT;
                out->target          = m->backtrack_target;
                out->accept_radius_m = ESC_BACKTRACK_RADIUS_M;  /* дрейф одометрії */
            } else {
                enter(m, FSM_STATE_FAILSAFE_SAFE_ABORT, in->now_ms);
                out->command = ESC_CMD_SAFE_ABORT;
                if (!m->incident_logged) {
                    m->incident_logged   = true;
                    out->persist_incident = true;
                }
            }
            break;

        case FSM_STATE_FAILSAFE_SAFE_ABORT:
            out->command = ESC_CMD_SAFE_ABORT;
            if (!m->incident_logged) {
                m->incident_logged    = true;
                out->persist_incident = true;
            }
            break;

        case FSM_STATE_MANUAL_RC:
            out->command = ESC_CMD_MANUAL;
            break;
    }
}

EscReplyVerdict escalation_manager_handle_response(EscManager* m, const uint8_t* frame, size_t len, uint32_t now_ms)
{
    EscReply rep;
    if (esc_unpack_reply(frame, len, &rep) != ESC_WIRE_OK) {
        return ESC_REPLY_BAD_FRAME;
    }
    /* Три бар'єри поспіль; будь-який спрацював — приводів не чіпаємо взагалі */
    if (m->state != FSM_STATE_AWAITING_OPERATOR) {
        return ESC_REPLY_WRONG_STATE;
    }
    if (rep.query_id != m->query_id) {
        return ESC_REPLY_STALE_ID;
    }
    if ((uint32_t)(now_ms - m->request_started_ms) > m->deadline_ms) {
        return ESC_REPLY_TOO_LATE;
    }
    for (uint8_t i = 0; i < m->options_count; ++i) {
        if (m->options[i].option_id == rep.option_id) {
            m->selected_option_id = rep.option_id;
            enter(m, FSM_STATE_APPLYING_OVERRIDE, now_ms);
            return ESC_REPLY_ACCEPTED;
        }
    }
    return ESC_REPLY_UNKNOWN_OPTION;
}

const char* esc_state_str(EscState s)
{
    switch (s) {
        case FSM_STATE_AUTONOMOUS:          return "AUTONOMOUS";
        case FSM_STATE_ESCALATION_REQUESTED:       return "ESCALATION_REQUESTED";
        case FSM_STATE_AWAITING_OPERATOR:   return "AWAITING_OPERATOR";
        case FSM_STATE_APPLYING_OVERRIDE:   return "APPLYING_OVERRIDE";
        case FSM_STATE_FAILSAFE_HOLD:       return "FAILSAFE_HOLD";
        case FSM_STATE_FAILSAFE_BACKTRACK:  return "FAILSAFE_BACKTRACK";
        case FSM_STATE_FAILSAFE_SAFE_ABORT: return "FAILSAFE_SAFE_ABORT";
        case FSM_STATE_MANUAL_RC:           return "MANUAL_RC";
    }
    return "?";
}

const char* esc_verdict_str(EscReplyVerdict v)
{
    switch (v) {
        case ESC_REPLY_ACCEPTED:       return "прийнято";
        case ESC_REPLY_BAD_FRAME:      return "битий кадр";
        case ESC_REPLY_WRONG_STATE:    return "автомат уже не чекає";
        case ESC_REPLY_STALE_ID:       return "чужий query_id";
        case ESC_REPLY_TOO_LATE:       return "після дедлайну";
        case ESC_REPLY_UNKNOWN_OPTION: return "невідома опція";
    }
    return "?";
}
