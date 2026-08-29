#include "sbo_client.h"

#include <string.h>

void sbo_client_init(struct sbo_client *c, uint8_t source_id)
{
    memset(c, 0, sizeof(*c));
    c->source_id = source_id;
}

static size_t build(struct sbo_client *c, uint8_t type, uint8_t target_id,
                    uint8_t comp, uint16_t cmd_code, uint16_t window_ms,
                    uint32_t token, const uint8_t *params, uint8_t params_len,
                    uint8_t *out, size_t cap)
{
    struct sbo_frame f;
    memset(&f, 0, sizeof(f));
    f.seq = c->seq++;
    f.msg_type = type;
    f.source_id = c->source_id;
    f.target_id = target_id;
    f.target_comp = comp;
    f.sbo_state = c->armed ? SBO_STATE_ARMED : SBO_STATE_IDLE;
    f.sbo_token = token;
    f.cmd_code = cmd_code;
    f.timeout_ms = window_ms;
    if (params_len > SBO_MAX_PAYLOAD) {
        return 0;
    }
    if (params_len) {
        memcpy(f.payload, params, params_len);
        f.payload_len = params_len;
    }
    return sbo_encode(&f, out, cap);
}

size_t sbo_client_select(struct sbo_client *c, uint8_t target_id, uint8_t comp,
                         uint16_t cmd_code, uint16_t window_ms,
                         uint8_t *out, size_t cap)
{
    /* Пульт запам'ятовує намір ще до квитанції: повтори за N_retry мусять
       нести той самий вибір, інакше борт побачить два різні запити. */
    c->target_id = target_id;
    c->target_comp = comp;
    c->cmd_code = cmd_code;
    c->window_ms = window_ms;
    c->token = 0;
    c->armed = false;
    return build(c, SBO_MSG_SELECT_REQ, target_id, comp, cmd_code, window_ms,
                 0, NULL, 0, out, cap);
}

size_t sbo_client_operate(struct sbo_client *c, const uint8_t *params,
                          uint8_t params_len, uint8_t *out, size_t cap)
{
    return build(c, SBO_MSG_OPERATE_REQ, c->target_id, c->target_comp,
                 c->cmd_code, 0, c->token, params, params_len, out, cap);
}

size_t sbo_client_cancel(struct sbo_client *c, uint8_t *out, size_t cap)
{
    return build(c, SBO_MSG_CANCEL_REQ, c->target_id, c->target_comp,
                 c->cmd_code, 0, c->token, NULL, 0, out, cap);
}

size_t sbo_client_ping(struct sbo_client *c, uint8_t target_id,
                       uint8_t *out, size_t cap)
{
    return build(c, SBO_MSG_STATUS_PING, target_id, c->target_comp,
                 0, 0, 0, NULL, 0, out, cap);
}

void sbo_client_on_reply(struct sbo_client *c, const struct sbo_frame *r)
{
    const uint8_t err = (r->payload_len >= 1) ? r->payload[0] : 0;

    switch (r->msg_type) {
    case SBO_MSG_SELECT_ACK:
        c->token = r->sbo_token;
        c->window_ms = r->timeout_ms;   /* борт міг підрізати вікно під межі */
        c->armed = true;
        c->last_error = 0;
        break;
    case SBO_MSG_SELECT_NACK:
    case SBO_MSG_OPERATE_NACK:
        c->armed = false;
        c->token = 0;
        c->last_error = err;
        break;
    case SBO_MSG_OPERATE_ACK:
    case SBO_MSG_CANCEL_ACK:
        c->armed = false;
        c->token = 0;
        c->last_error = err;
        break;
    case SBO_MSG_STATUS_PONG:
        /* Розділ 8: борт звітує ARMED, а пульт вважає замок вільним —
           уявлення розійшлися, треба примусовий CANCEL_REQ. */
        if ((err & SBO_FLAG_ARMED) && !c->armed) {
            c->last_error = ERR_SBO_BUSY;
        }
        break;
    default:
        break;
    }
}
