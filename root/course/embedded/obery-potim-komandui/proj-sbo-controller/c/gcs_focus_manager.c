/* gcs_focus_manager.c — замок цілі на пульті: що обрано, чи підтверджено, чи можна тиснути. */
#include "gcs_focus_manager.h"

#include <string.h>

#define GCS_COLOR_RED   0xD0342Cu
#define GCS_COLOR_GREEN 0x2E9E4Fu
#define GCS_COLOR_AMBER 0xE0A800u
#define GCS_COLOR_GREY  0x6E6E6Eu

static void gcs_build_request(const gcs_focus_t *focus, sbo_packet_t *out, uint8_t msg_type) {
    memset(out, 0, sizeof(*out));
    out->magic       = SBO_MAGIC_BYTE;
    out->msg_type    = msg_type;
    out->seq         = focus->seq;
    out->source_id   = focus->self_id;
    out->target_id   = focus->focused_target_id;
    out->target_comp = focus->focused_comp;
    out->cmd_code    = focus->pending_cmd_code;
}

void gcs_focus_init(gcs_focus_t *focus, uint8_t self_id) {
    if (focus == NULL) {
        return;
    }
    memset(focus, 0, sizeof(*focus));
    focus->self_id = (self_id != 0u) ? self_id : (uint8_t)SBO_GCS_DEFAULT_ID;
    focus->status = GCS_FOCUS_NONE;
}

bool gcs_focus_select(gcs_focus_t *focus, uint8_t target_id, uint8_t component,
                      const char *name, uint16_t cmd_code, uint16_t window_ms,
                      uint32_t now_ms, sbo_packet_t *out_select) {
    if (focus == NULL || out_select == NULL) {
        return false;
    }
    /* Відсікаємо широкомовну селекцію вже на пульті: такий кадр борт усе одно
     * відкине, але оператор не мусить бачити «вибрано всіх». */
    if (target_id == SBO_BROADCAST_ID || target_id == focus->self_id || target_id == 0u) {
        focus->last_error = SBO_ERR_BROADCAST_FORBIDDEN;
        return false;
    }

    uint16_t window = (window_ms > 0u) ? window_ms : (uint16_t)SBO_DEFAULT_TIMEOUT_MS;
    if (window > SBO_MAX_TIMEOUT_MS) {
        window = (uint16_t)SBO_MAX_TIMEOUT_MS;
    }

    focus->focused_target_id = target_id;
    focus->focused_comp = component;
    if (name != NULL) {
        strncpy(focus->target_name, name, GCS_NAME_LEN - 1u);
        focus->target_name[GCS_NAME_LEN - 1u] = '\0';
    } else {
        focus->target_name[0] = '\0';
    }
    focus->pending_cmd_code = cmd_code;
    focus->window_ms = window;
    focus->token = 0u;                       /* старий токен не переживає нової селекції */
    focus->status = GCS_FOCUS_WAIT_ACK;
    focus->last_error = SBO_ERR_NONE;
    focus->sent_ms = now_ms;
    focus->ack_deadline_ms = now_ms + GCS_ACK_TIMEOUT_MS;
    focus->select_deadline_ms = 0u;
    focus->seq++;

    gcs_build_request(focus, out_select, SBO_MSG_SELECT_REQ);
    out_select->timeout_ms = window;
    return true;
}

void gcs_focus_tick(gcs_focus_t *focus, uint32_t now_ms) {
    if (focus == NULL) {
        return;
    }
    switch (focus->status) {
    case GCS_FOCUS_WAIT_ACK:
    case GCS_FOCUS_WAIT_OP:
        if ((int32_t)(now_ms - focus->ack_deadline_ms) >= 0) {
            /* Квитанції немає: картка червоніє, кнопка дії гасне. Оператор не має
             * права вважати апарат готовим, поки канал мовчить. */
            focus->status = GCS_FOCUS_LINK_LOST;
            focus->token = 0u;
            focus->last_error = SBO_ERR_TIMEOUT_EXPIRED;
        }
        break;
    case GCS_FOCUS_ARMED:
        if ((int32_t)(now_ms - focus->select_deadline_ms) >= 0) {
            focus->status = GCS_FOCUS_EXPIRED;
            focus->token = 0u;
        }
        break;
    default:
        break;
    }
}

void gcs_focus_on_response(gcs_focus_t *focus, const sbo_packet_t *rx, uint32_t now_ms) {
    if (focus == NULL || rx == NULL) {
        return;
    }
    /* Чужий контекст: відповідь не від того апарата або не нам. */
    if (rx->source_id != focus->focused_target_id || rx->target_id != focus->self_id) {
        return;
    }

    switch (rx->msg_type) {
    case SBO_MSG_SELECT_ACK:
        if (focus->status != GCS_FOCUS_WAIT_ACK) {
            return;                        /* запізніла квитанція після втрати звʼязку */
        }
        if (rx->cmd_code != focus->pending_cmd_code) {
            focus->status = GCS_FOCUS_REJECTED;
            focus->last_error = SBO_ERR_CMD_MISMATCH;
            return;
        }
        focus->token = rx->sbo_token;
        focus->status = GCS_FOCUS_ARMED;
        {
            /* Вікно рахуємо від МОМЕНТУ ВІДПРАВКИ запиту (борт відлічує своє від
             * прийому) і забираємо запас на політ команди назад. */
            uint16_t window = (rx->timeout_ms > 0u) ? rx->timeout_ms : focus->window_ms;
            uint32_t usable = (window > GCS_GUARD_MS) ? (uint32_t)(window - GCS_GUARD_MS)
                                                      : (uint32_t)(window / 2u);
            focus->select_deadline_ms = focus->sent_ms + usable;
        }
        break;

    case SBO_MSG_SELECT_NACK:
    case SBO_MSG_OPERATE_NACK:
    case SBO_MSG_CANCEL_NACK:
        focus->status = GCS_FOCUS_REJECTED;
        focus->last_error = (rx->payload_len > 0u) ? (sbo_error_t)rx->payload[0]
                                                   : SBO_ERR_INTERNAL_FAULT;
        focus->token = 0u;
        break;

    case SBO_MSG_OPERATE_ACK:
        focus->status = GCS_FOCUS_DONE;
        focus->token = 0u;
        focus->last_error = SBO_ERR_NONE;
        break;

    case SBO_MSG_CANCEL_ACK:
        focus->status = GCS_FOCUS_NONE;
        focus->token = 0u;
        focus->last_error = SBO_ERR_NONE;
        break;

    default:
        break;
    }
    (void)now_ms;
}

bool gcs_focus_build_operate(gcs_focus_t *focus, const uint8_t *payload, uint8_t payload_len,
                             uint32_t now_ms, sbo_packet_t *out_operate) {
    if (focus == NULL || out_operate == NULL || payload_len > SBO_MAX_PAYLOAD_LEN) {
        return false;
    }
    gcs_focus_tick(focus, now_ms);        /* стан міг протухнути між перемальовуваннями */
    if (focus->status != GCS_FOCUS_ARMED || focus->token == 0u) {
        return false;
    }

    focus->seq++;
    gcs_build_request(focus, out_operate, SBO_MSG_OPERATE_REQ);
    out_operate->sbo_token = focus->token;
    if (payload != NULL && payload_len > 0u) {
        memcpy(out_operate->payload, payload, payload_len);
        out_operate->payload_len = payload_len;
    }

    /* Локальний замок теж одноразовий: другий клік вимагатиме нової селекції. */
    focus->token = 0u;
    focus->status = GCS_FOCUS_WAIT_OP;
    focus->sent_ms = now_ms;
    focus->ack_deadline_ms = now_ms + GCS_ACK_TIMEOUT_MS;
    return true;
}

bool gcs_focus_build_cancel(gcs_focus_t *focus, uint32_t now_ms, sbo_packet_t *out_cancel) {
    if (focus == NULL || out_cancel == NULL) {
        return false;
    }
    if (focus->status == GCS_FOCUS_NONE || focus->focused_target_id == 0u) {
        return false;
    }
    focus->seq++;
    gcs_build_request(focus, out_cancel, SBO_MSG_CANCEL_REQ);
    focus->token = 0u;
    focus->status = GCS_FOCUS_WAIT_OP;
    focus->sent_ms = now_ms;
    focus->ack_deadline_ms = now_ms + GCS_ACK_TIMEOUT_MS;
    return true;
}

bool gcs_focus_button_enabled(const gcs_focus_t *focus, uint32_t now_ms) {
    if (focus == NULL || focus->status != GCS_FOCUS_ARMED || focus->token == 0u) {
        return false;
    }
    return (int32_t)(now_ms - focus->select_deadline_ms) < 0;
}

const char *gcs_focus_badge(const gcs_focus_t *focus) {
    switch (focus->status) {
    case GCS_FOCUS_NONE:      return "Апарат не обрано";
    case GCS_FOCUS_WAIT_ACK:  return "Очікування квитанції…";
    case GCS_FOCUS_ARMED:     return "Замок зведено";
    case GCS_FOCUS_WAIT_OP:   return "Команду надіслано…";
    case GCS_FOCUS_DONE:      return "Виконано";
    case GCS_FOCUS_LINK_LOST: return "Втрата зв'язку";
    case GCS_FOCUS_REJECTED:  return sbo_error_text(focus->last_error);
    case GCS_FOCUS_EXPIRED:   return "Вікно вибору спливло";
    default:                  return "";
    }
}

uint32_t gcs_focus_frame_color(const gcs_focus_t *focus) {
    switch (focus->status) {
    case GCS_FOCUS_ARMED:
    case GCS_FOCUS_DONE:      return GCS_COLOR_GREEN;
    case GCS_FOCUS_WAIT_ACK:
    case GCS_FOCUS_WAIT_OP:   return GCS_COLOR_AMBER;
    case GCS_FOCUS_LINK_LOST:
    case GCS_FOCUS_REJECTED:  return GCS_COLOR_RED;
    default:                  return GCS_COLOR_GREY;
    }
}
