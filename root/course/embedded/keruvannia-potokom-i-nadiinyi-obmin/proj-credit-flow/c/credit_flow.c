#include "credit_flow.h"

#include <string.h>

/* --- Передавач ----------------------------------------------------------- */

void cf_sender_init(cf_sender_t *s, uint32_t now_ms)
{
    memset(s, 0, sizeof *s);
    s->credits = (int32_t)CF_RX_SLOTS; /* стартове вікно узгоджене при встановленні зв'язку */
    s->state = CF_LINK_READY;
    s->last_event_ms = now_ms;
}

bool cf_sender_can_send(const cf_sender_t *s)
{
    return s->state != CF_LINK_DEAD && s->credits > 0;
}

cf_send_result_t cf_sender_encode(cf_sender_t *s, const uint8_t *data, uint8_t len,
                                  uint32_t now_ms, cf_frame_t *out_frame)
{
    if (s->state == CF_LINK_DEAD) {
        return CF_SEND_LINK_DEAD;
    }
    if (len > CF_MAX_PAYLOAD) {
        return CF_SEND_TOO_LONG;
    }
    if (s->credits <= 0) {
        return CF_SEND_NO_CREDIT;
    }

    memset(out_frame, 0, sizeof *out_frame);
    out_frame->type = (uint8_t)CF_FRAME_DATA;
    out_frame->seq = s->next_seq++;
    out_frame->length = len;
    if (len > 0u) {
        memcpy(out_frame->payload, data, len);
    }

    s->credits--;
    s->frames_sent++;

    if (s->credits == 0) {
        /* Тишу міряємо від миті, коли витратили останній кредит: саме звідси
         * має сенс чекати повернення. */
        s->state = CF_LINK_BLOCKED;
        s->last_event_ms = now_ms;
        s->polls_sent = 0;
    }
    return CF_SEND_OK;
}

void cf_sender_on_frame(cf_sender_t *s, const cf_frame_t *frame, uint32_t now_ms)
{
    uint16_t delta;

    if (s->state == CF_LINK_DEAD) {
        return; /* мертвий лінк піднімає лише повторне встановлення зв'язку */
    }

    /* Різниця беззнакових 16-бітних правильна й після переповнення лічильника. */
    delta = (uint16_t)(frame->cum_release - s->last_cum_release);

    if (delta > (uint16_t)CF_RX_SLOTS) {
        /* Приймач фізично не міг звільнити більше слотів, ніж вікно: кадр побито
         * або він від чужого сеансу. Стан не чіпаємо взагалі. */
        s->suspect_grants++;
        return;
    }

    if (delta == 0u) {
        /* Повторений або переставлений кадр. Кумулятивне число робить його
         * безпечним: нічого не додаємо й нічого не ламаємо. */
        s->stale_grants++;
    } else {
        s->last_cum_release = frame->cum_release;
        s->credits += (int32_t)delta;
        s->credits_granted += delta;
        if (s->credits > (int32_t)CF_RX_SLOTS) {
            s->credits = (int32_t)CF_RX_SLOTS; /* вікно — тверда стеля */
        }
    }

    s->last_event_ms = now_ms;
    if (s->credits > 0) {
        s->state = CF_LINK_READY;
        s->polls_sent = 0;
    }
}

bool cf_sender_tick(cf_sender_t *s, uint32_t now_ms, cf_frame_t *out_poll)
{
    if (s->state != CF_LINK_BLOCKED && s->state != CF_LINK_POLLING) {
        return false;
    }
    if ((uint32_t)(now_ms - s->last_event_ms) < CF_POLL_TIMEOUT_MS) {
        return false;
    }
    if (s->polls_sent >= (uint8_t)CF_MAX_POLLS) {
        s->state = CF_LINK_DEAD;
        return false;
    }

    memset(out_poll, 0, sizeof *out_poll);
    out_poll->type = (uint8_t)CF_FRAME_POLL;
    /* Кажемо, що вже зараховано: приймачу видно, наскільки ми відстали. */
    out_poll->cum_release = s->last_cum_release;

    s->polls_sent++;
    s->last_event_ms = now_ms;
    s->state = CF_LINK_POLLING;
    return true;
}

const char *cf_link_state_name(cf_link_state_t state)
{
    switch (state) {
    case CF_LINK_READY: return "READY";
    case CF_LINK_BLOCKED: return "BLOCKED";
    case CF_LINK_POLLING: return "POLLING";
    case CF_LINK_DEAD: return "DEAD";
    default: return "?";
    }
}

/* --- Приймач ------------------------------------------------------------- */

void cf_receiver_init(cf_receiver_t *r)
{
    memset(r, 0, sizeof *r);
}

cf_rx_result_t cf_receiver_on_frame(cf_receiver_t *r, const cf_frame_t *frame)
{
    switch (frame->type) {
    case CF_FRAME_POLL:
        r->poll_pending = true;
        return CF_RX_POLLED;
    case CF_FRAME_DATA:
        break;
    default:
        r->bad_frames++;
        return CF_RX_BAD_FRAME;
    }

    if (frame->length > CF_MAX_PAYLOAD) {
        r->bad_frames++;
        return CF_RX_BAD_FRAME;
    }
    if (r->occupied >= (uint8_t)CF_RX_SLOTS) {
        /* Класти нікуди: передавач порахував кредити неправильно. Кадр гине,
         * але пам'ять уже прийнятих пакетів лишається цілою. */
        r->over_quota++;
        return CF_RX_OVER_QUOTA;
    }

    if (r->seq_seen && frame->seq != r->expected_seq) {
        r->seq_gaps++; /* кадр даних загубився на шині */
    }
    r->expected_seq = (uint8_t)(frame->seq + 1u);
    r->seq_seen = true;

    r->slots[r->write_idx] = *frame;
    r->write_idx = (uint8_t)((r->write_idx + 1u) % CF_RX_SLOTS);
    r->occupied++;
    return CF_RX_ACCEPTED;
}

bool cf_receiver_take(cf_receiver_t *r, cf_frame_t *out_frame)
{
    if (r->occupied == 0u) {
        return false;
    }

    *out_frame = r->slots[r->read_idx];
    r->read_idx = (uint8_t)((r->read_idx + 1u) % CF_RX_SLOTS);
    r->occupied--;
    r->cum_release++; /* пам'ять звільнено — росте абсолютний лічильник */
    return true;
}

bool cf_receiver_build_grant(cf_receiver_t *r, cf_frame_t *out_frame)
{
    const uint16_t unreported = (uint16_t)(r->cum_release - r->last_reported);

    if (!r->poll_pending && unreported < (uint16_t)CF_GRANT_BATCH) {
        /* Копимо пачку: кожен окремий GRANT коштує стільки ж ефіру, скільки й
         * кадр даних. Але POLL відповідаємо негайно, хай навіть новини нема. */
        return false;
    }

    memset(out_frame, 0, sizeof *out_frame);
    out_frame->type = (uint8_t)CF_FRAME_GRANT;
    /* Абсолютне число, а не приріст: попередній GRANT міг згинути. */
    out_frame->cum_release = r->cum_release;

    r->last_reported = r->cum_release;
    r->poll_pending = false;
    return true;
}
