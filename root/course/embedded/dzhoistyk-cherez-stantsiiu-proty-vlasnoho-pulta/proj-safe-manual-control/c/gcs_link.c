#include "gcs_link.h"

#include <string.h>

static void queue_ack(gcs_link_t *l, uint16_t command, uint8_t result)
{
    mav_command_ack_t ack;
    uint8_t payload[3];
    uint8_t len;

    ack.command = command;
    ack.result  = result;
    len = mav_pack_command_ack(payload, &ack);

    l->ack_len = mav_encode(l->ack, sizeof(l->ack), l->our_sysid, l->our_compid,
                            l->tx_seq++, MAV_MSG_COMMAND_ACK, payload, len);
}

static uint8_t arm_result_to_mav(arm_result_t r)
{
    switch (r) {
    case ARM_ACCEPTED:
    case ARM_DISARMED:          return MAV_RESULT_ACCEPTED;
    case ARM_NEED_CONFIRMATION: return MAV_RESULT_TEMPORARILY_REJECTED;
    case ARM_DENIED_NO_LINK:
    case ARM_DENIED_STICKS:
    case ARM_DENIED_FAILSAFE:   return MAV_RESULT_DENIED;
    }
    return MAV_RESULT_FAILED;
}

void gcs_link_init(gcs_link_t *l, uint8_t sysid, uint8_t compid)
{
    memset(l, 0, sizeof(*l));
    l->our_sysid  = sysid;
    l->our_compid = compid;
    mav_parser_init(&l->parser);
}

static bool from_our_gcs(const gcs_link_t *l, const mav_frame_t *f)
{
    return l->gcs_sysid != 0 && f->sysid == l->gcs_sysid;
}

static void handle_manual_control(gcs_link_t *l, const mav_frame_t *f,
                                  uint32_t now_ms, arbiter_t *arb)
{
    mav_manual_control_t mc;
    mav_unpack_manual_control(f, &mc);

    /* Кадр адресований конкретному апарату. Чужий — не наша справа. */
    if (mc.target != l->our_sysid) {
        l->n_wrong_target++;
        return;
    }

    if (l->gcs_sysid == 0 || (now_ms - l->last_gcs_frame_ms) > GCS_RELATCH_MS) {
        /* Перша авторизована станція фіксується тут; інша зможе перебрати
         * керування лише після повної тиші зафіксованої. */
        l->gcs_sysid  = f->sysid;
        l->gcs_compid = f->compid;
    } else if (f->sysid != l->gcs_sysid) {
        l->n_foreign++; /* друга станція на тому ж модемі — ігноруємо мовчки */
        return;
    }

    l->last_gcs_frame_ms = now_ms;
    l->n_manual++;
    arbiter_feed_manual_control(arb, mc.x, mc.y, mc.z, mc.r, mc.buttons, now_ms);
}

static void handle_command_long(gcs_link_t *l, const mav_frame_t *f,
                                uint32_t now_ms, arbiter_t *arb)
{
    mav_command_long_t cl;
    arm_result_t res;
    bool arm, confirmed;

    mav_unpack_command_long(f, &cl);

    if (cl.target_system != l->our_sysid)
        { l->n_wrong_target++; return; }
    if (cl.target_component != l->our_compid && cl.target_component != MAV_COMP_ID_ALL)
        { l->n_wrong_target++; return; }
    if (!from_our_gcs(l, f))
        { l->n_foreign++; return; }

    if (cl.command != MAV_CMD_COMPONENT_ARM_DISARM) {
        queue_ack(l, cl.command, MAV_RESULT_UNSUPPORTED);
        return;
    }

    l->n_arm_cmd++;
    arm       = (cl.param[0] > 0.5f);
    /* Поле confirmation: 0 — перша спроба, ≥1 — підтвердження від оператора.
     * Арм по одному натисканню кнопки не проходить свідомо. */
    confirmed = (cl.confirmation >= 1u);

    res = arbiter_request_arm(arb, arm, confirmed, now_ms);
    queue_ack(l, cl.command, arm_result_to_mav(res));
}

void gcs_link_feed(gcs_link_t *l, const uint8_t *data, size_t n, uint32_t now_ms, arbiter_t *arb)
{
    mav_frame_t f;
    size_t i;

    for (i = 0; i < n; ++i) {
        if (!mav_parse_byte(&l->parser, data[i], &f))
            continue;

        switch (f.msgid) {
        case MAV_MSG_HEARTBEAT:
            /* Ізоляція: серцебиття доводить, що жива станція, а не джойстик. */
            if (l->gcs_sysid == 0 || from_our_gcs(l, &f)) {
                l->last_heartbeat_ms = now_ms;
                l->n_heartbeat++;
            }
            break;
        case MAV_MSG_MANUAL_CONTROL:
            handle_manual_control(l, &f, now_ms, arb);
            break;
        case MAV_MSG_COMMAND_LONG:
            handle_command_long(l, &f, now_ms, arb);
            break;
        default:
            break;
        }
    }
}

bool gcs_link_take_ack(gcs_link_t *l, const uint8_t **buf, size_t *len)
{
    if (l->ack_len == 0)
        return false;
    *buf = l->ack;
    *len = l->ack_len;
    l->ack_len = 0;
    return true;
}
