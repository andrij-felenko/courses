#ifndef ESC_ESCALATION_H
#define ESC_ESCALATION_H

#include "protocol.h"
#include "trail.h"

typedef enum {
    FSM_STATE_AUTONOMOUS = 0,
    FSM_STATE_ESCALATION_REQUESTED,       /* пакет треба зібрати й віддати в радіо */
    FSM_STATE_AWAITING_OPERATOR,
    FSM_STATE_APPLYING_OVERRIDE,
    FSM_STATE_FAILSAFE_HOLD,
    FSM_STATE_FAILSAFE_BACKTRACK,
    FSM_STATE_FAILSAFE_SAFE_ABORT,
    FSM_STATE_MANUAL_RC            /* перехоплення апаратним тумблером пульта */
} EscState;

/* Команда, яку автомат віддає нижньому рівню керування цього такту */
typedef enum {
    ESC_CMD_CONTINUE = 0,
    ESC_CMD_HOLD,
    ESC_CMD_FOLLOW_OPTION,
    ESC_CMD_GOTO_POINT,
    ESC_CMD_SAFE_ABORT,
    ESC_CMD_MANUAL
} EscCommand;

typedef struct {
    uint32_t   now_ms;               /* монотонний бортовий час */
    EscTrigger trigger;              /* що каже детектор/планувальник цього такту */
    float      dist_to_obstacle_m;
    float      speed_mps;
    BreadcrumbPoint   pose;                 /* поточна поза з одометрії */
    uint32_t   last_heartbeat_ms;    /* час останнього HEARTBEAT від станції */
    bool       rc_override;          /* апаратний перемикач режимів на пульті */
    bool       maneuver_done;        /* планувальник доробив обрану опцію */
    const EscOption* options;        /* варіанти від планувальника (при тригері) */
    uint8_t    options_count;
    const uint8_t* roi_jpeg;         /* мініатюра спірної ділянки кадру */
    uint16_t   roi_len;
} EscInputs;

typedef struct {
    EscCommand command;
    uint8_t    selected_option_id;   /* для ESC_CMD_FOLLOW_OPTION */
    BreadcrumbPoint   target;               /* для ESC_CMD_GOTO_POINT */
    float      accept_radius_m;
    uint8_t    frame[ESC_MTU_BYTES]; /* кадр у радіо, якщо frame_len > 0 */
    size_t     frame_len;
    bool       persist_incident;     /* один раз: записати інцидент у NVRAM */
} EscOutputs;

typedef struct {
    EscState   state;
    uint32_t   state_entered_ms;
    EscTrigger active_trigger;
    uint16_t   query_id;
    uint32_t   request_started_ms;
    uint32_t   deadline_ms;
    uint8_t    selected_option_id;
    EscOption  options[ESC_MAX_OPTIONS];
    uint8_t    options_count;
    uint8_t    roi[ESC_ROI_MAX];
    uint16_t   roi_len;
    BreadcrumbPoint   pose_at_request;
    float      speed_at_request;
    BreadcrumbTrail   trail;
    BreadcrumbPoint   backtrack_target;
    bool       has_backtrack_target;
    uint32_t   heartbeat_timeout_ms;
    bool       incident_logged;
} EscManager;

typedef enum {
    ESC_REPLY_ACCEPTED = 0,
    ESC_REPLY_BAD_FRAME,
    ESC_REPLY_WRONG_STATE,     /* автомат уже не чекає — запізніла кнопка */
    ESC_REPLY_STALE_ID,        /* відповідь на попередній інцидент */
    ESC_REPLY_TOO_LATE,        /* дедлайн вичерпано */
    ESC_REPLY_UNKNOWN_OPTION
} EscReplyVerdict;

void            esc_init(EscManager* m, uint32_t heartbeat_timeout_ms);
void            esc_tick(EscManager* m, const EscInputs* in, EscOutputs* out);
EscReplyVerdict escalation_manager_handle_response(EscManager* m, const uint8_t* frame, size_t len, uint32_t now_ms);
const char*     esc_state_str(EscState s);
const char*     esc_verdict_str(EscReplyVerdict v);

#endif /* ESC_ESCALATION_H */
