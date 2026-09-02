#include <string.h>

#include "auth_arbiter.h"
#include "auth_frame.h"

/* Порівняння часу з урахуванням переповнення 32-бітного лічильника мс. */
static bool time_before(uint32_t a, uint32_t b)
{
    return (int32_t)(a - b) < 0;
}

static bool token_active(const auth_token_t *t, uint32_t now)
{
    return t->gcs_id != 0u && t->nonce != 0u && time_before(now, t->lease_deadline_ms);
}

static void token_clear(auth_token_t *t)
{
    t->gcs_id = 0u;
    t->nonce = 0u;
    t->lease_deadline_ms = 0u;
}

/* xorshift32; nonce нуль не видаємо — нуль означає «токена немає». */
static uint32_t next_nonce(auth_arbiter_t *a)
{
    uint32_t x = a->rng;
    do {
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
    } while (x == 0u);
    a->rng = x;
    return x;
}

static void emit_msg(auth_arbiter_t *a, uint16_t msg_id, uint8_t target,
                     uint32_t nonce, uint32_t now, const void *payload, size_t len)
{
    uint8_t buf[AUTH_MAX_FRAME];
    auth_header_t h;

    memset(&h, 0, sizeof h);
    h.msg_id       = msg_id;
    h.source_id    = a->self_id;
    h.target_id    = target;
    h.seq_num      = ++a->tx_seq;
    h.timestamp_ms = now;
    h.token_nonce  = nonce;

    const int n = auth_frame_encode(buf, sizeof buf, &h, payload, len);
    if (n > 0 && a->emit != NULL) {
        a->emit(a->emit_ctx, buf, (size_t)n);
    }
}

static void reply_grant(auth_arbiter_t *a, uint8_t target, uint32_t now,
                        auth_role_flags_t role, auth_status_code_t st,
                        uint16_t lease_ms, uint32_t nonce)
{
    msg_auth_token_grant_t g;
    g.granted_role = (uint8_t)role;
    g.status       = (uint8_t)st;
    g.lease_ms     = lease_ms;
    g.token_nonce  = nonce;
    emit_msg(a, MSG_AUTH_TOKEN_GRANT, target, nonce, now, &g, sizeof g);
}

static void emit_revoke(auth_arbiter_t *a, uint8_t target, uint32_t now,
                        auth_role_flags_t role, auth_revoke_reason_t reason)
{
    msg_auth_token_revoke_t r;
    r.revoked_role = (uint8_t)role;
    r.reason       = (uint8_t)reason;
    r.gcs_id       = target;
    emit_msg(a, MSG_AUTH_TOKEN_REVOKE, target, 0u, now, &r, sizeof r);
}

static void broadcast_status(auth_arbiter_t *a, uint32_t now)
{
    msg_auth_status_t s;
    auth_arbiter_fill_status(a, now, &s);
    emit_msg(a, MSG_AUTH_STATUS, AUTH_BROADCAST_ID, 0u, now, &s, sizeof s);
}

/* Оренду просить станція, але стелю ставить борт: понад 1000 мс не даємо. */
static uint16_t clamp_lease(uint16_t requested)
{
    if (requested == 0u || requested > AUTH_LEASE_TIMEOUT_MS) {
        return (uint16_t)AUTH_LEASE_TIMEOUT_MS;
    }
    if (requested < AUTH_HEARTBEAT_PERIOD_MS) {
        return (uint16_t)AUTH_HEARTBEAT_PERIOD_MS;
    }
    return requested;
}

/* Захист від повтору: номер послідовності мусить зростати. Порівняння
   різниці зі знаком витримує переповнення 16-бітного лічильника. */
static bool peer_seq_ok(auth_arbiter_t *a, uint8_t id, uint16_t seq)
{
    auth_peer_t *slot = NULL;

    for (size_t i = 0; i < AUTH_MAX_PEERS; ++i) {
        if (a->peers[i].seen && a->peers[i].gcs_id == id) {
            if ((int16_t)(seq - a->peers[i].last_seq) <= 0) {
                return false;
            }
            a->peers[i].last_seq = seq;
            return true;
        }
        if (!a->peers[i].seen && slot == NULL) {
            slot = &a->peers[i];
        }
    }

    if (slot == NULL) {
        return false;  /* таблиця сусідів заповнена — нового не пускаємо */
    }
    slot->seen = true;
    slot->gcs_id = id;
    slot->last_seq = seq;
    return true;
}

static size_t expected_payload_size(uint16_t msg_id)
{
    switch (msg_id) {
    case MSG_AUTH_HEARTBEAT:       return sizeof(msg_auth_heartbeat_t);
    case MSG_AUTH_TOKEN_REQ:       return sizeof(msg_auth_token_req_t);
    case MSG_HANDOVER_STICK_CHECK: return sizeof(msg_stick_check_t);
    case MSG_COMMANDER_OVERRIDE:   return sizeof(msg_commander_override_t);
    default:                       return (size_t)-1;  /* кадри напрямку FCU→GCS */
    }
}

void auth_arbiter_init(auth_arbiter_t *a, uint8_t self_id, uint32_t commander_key,
                       uint32_t seed, auth_emit_fn emit, void *emit_ctx)
{
    memset(a, 0, sizeof *a);
    a->self_id = self_id;
    a->commander_key = commander_key;
    a->rng = (seed != 0u) ? seed : 0x1BADC0DEu;
    a->state = AUTH_STATE_IDLE;
    a->emit = emit;
    a->emit_ctx = emit_ctx;
}

void auth_arbiter_set_throttle(auth_arbiter_t *a, int16_t throttle)
{
    a->vehicle_throttle = throttle;
}

void auth_arbiter_fill_status(const auth_arbiter_t *a, uint32_t now,
                              msg_auth_status_t *out)
{
    const bool pilot_ok = token_active(&a->pilot, now);

    out->pilot_gcs_id     = pilot_ok ? a->pilot.gcs_id : 0u;
    out->payload_gcs_id   = token_active(&a->payload, now) ? a->payload.gcs_id : 0u;
    out->commander_gcs_id = a->commander.gcs_id;
    out->pilot_lease_remaining_ms = pilot_ok ? (a->pilot.lease_deadline_ms - now) : 0u;
    out->arbitration_state = (uint8_t)a->state;
}

/* ---- обробники окремих повідомлень ---------------------------------- */

static auth_status_code_t on_heartbeat(auth_arbiter_t *a, const auth_header_t *h,
                                       const uint8_t *pl, uint32_t now)
{
    msg_auth_heartbeat_t hb;
    memcpy(&hb, pl, sizeof hb);

    const uint16_t lease = clamp_lease(hb.lease_requested_ms);

    if (h->source_id == a->pilot.gcs_id && h->token_nonce == a->pilot.nonce &&
        token_active(&a->pilot, now)) {
        a->pilot.lease_deadline_ms = now + lease;
        return AUTH_STATUS_OK;
    }
    if (h->source_id == a->payload.gcs_id && h->token_nonce == a->payload.nonce &&
        token_active(&a->payload, now)) {
        a->payload.lease_deadline_ms = now + lease;
        return AUTH_STATUS_OK;
    }
    if (h->source_id == a->commander.gcs_id && h->token_nonce == a->commander.nonce) {
        a->commander.lease_deadline_ms = now + lease;
        return AUTH_STATUS_OK;
    }

    /* Серцебиття з мертвим nonce: станція вважає себе володарем, борт — ні.
       Кажемо їй правду, щоб вона перезапросила токен, а не гадала. */
    if ((hb.active_roles & (uint8_t)(AUTH_ROLE_PILOT | AUTH_ROLE_PAYLOAD)) != 0u) {
        emit_revoke(a, h->source_id, now, AUTH_ROLE_NONE, AUTH_REVOKE_LEASE_EXPIRED);
        return AUTH_ERR_LEASE_EXPIRED;
    }
    return AUTH_STATUS_OK;  /* спостерігач просто підтверджує канал */
}

static auth_status_code_t grant_exclusive(auth_arbiter_t *a, auth_token_t *tok,
                                          auth_role_flags_t role,
                                          const auth_header_t *h, uint32_t now)
{
    if (token_active(tok, now) && tok->gcs_id != h->source_id) {
        reply_grant(a, h->source_id, now, AUTH_ROLE_NONE,
                    AUTH_ERR_TOKEN_ALREADY_TAKEN, 0u, 0u);
        return AUTH_ERR_TOKEN_ALREADY_TAKEN;
    }

    tok->gcs_id = h->source_id;
    tok->nonce = next_nonce(a);
    tok->lease_deadline_ms = now + AUTH_LEASE_TIMEOUT_MS;

    if (role == AUTH_ROLE_PILOT) {
        a->state = AUTH_STATE_PILOT_ACTIVE;
    }

    reply_grant(a, h->source_id, now, role, AUTH_STATUS_OK,
                (uint16_t)AUTH_LEASE_TIMEOUT_MS, tok->nonce);
    broadcast_status(a, now);
    return AUTH_STATUS_OK;
}

static auth_status_code_t start_handover(auth_arbiter_t *a, const auth_header_t *h,
                                         uint8_t target, uint32_t now)
{
    if (a->state == AUTH_STATE_HANDOVER_WAIT_STICK) {
        reply_grant(a, h->source_id, now, AUTH_ROLE_NONE,
                    AUTH_ERR_TOKEN_ALREADY_TAKEN, 0u, 0u);
        return AUTH_ERR_TOKEN_ALREADY_TAKEN;
    }
    if (target == a->pilot.gcs_id || target == 0u || target == AUTH_BROADCAST_ID) {
        reply_grant(a, h->source_id, now, AUTH_ROLE_NONE, AUTH_ERR_UNAUTHORIZED, 0u, 0u);
        return AUTH_ERR_UNAUTHORIZED;
    }

    a->state = AUTH_STATE_HANDOVER_WAIT_STICK;
    a->handover_from = a->pilot.gcs_id;
    a->handover_to = target;
    a->handover_deadline_ms = now + AUTH_HANDOVER_TIMEOUT_MS;

    msg_handover_offer_t offer;
    offer.from_gcs_id     = a->handover_from;
    offer.to_gcs_id       = target;
    offer.timeout_ms      = (uint16_t)AUTH_HANDOVER_TIMEOUT_MS;
    offer.throttle_target = a->vehicle_throttle;
    emit_msg(a, MSG_HANDOVER_OFFER, target, 0u, now, &offer, sizeof offer);

    broadcast_status(a, now);
    return AUTH_STATUS_OK;
}

static auth_status_code_t on_token_req(auth_arbiter_t *a, const auth_header_t *h,
                                       const uint8_t *pl, uint32_t now)
{
    msg_auth_token_req_t req;
    memcpy(&req, pl, sizeof req);

    /* Командирський токен видається лише під спільний ключ. */
    if (req.requested_role == (uint8_t)AUTH_ROLE_COMMANDER) {
        if (req.auth_token != a->commander_key) {
            reply_grant(a, h->source_id, now, AUTH_ROLE_NONE,
                        AUTH_ERR_UNAUTHORIZED, 0u, 0u);
            return AUTH_ERR_UNAUTHORIZED;
        }
        a->commander.gcs_id = h->source_id;
        a->commander.nonce = next_nonce(a);
        a->commander.lease_deadline_ms = now + AUTH_LEASE_TIMEOUT_MS;
        reply_grant(a, h->source_id, now, AUTH_ROLE_COMMANDER, AUTH_STATUS_OK,
                    (uint16_t)AUTH_LEASE_TIMEOUT_MS, a->commander.nonce);
        broadcast_status(a, now);
        return AUTH_STATUS_OK;
    }

    /* Поки борт замкнено командиром, чужі запити не проходять. */
    if (a->state == AUTH_STATE_COMMANDER_LOCKED && h->source_id != a->commander.gcs_id) {
        reply_grant(a, h->source_id, now, AUTH_ROLE_NONE,
                    AUTH_ERR_PRIORITY_TOO_LOW, 0u, 0u);
        return AUTH_ERR_PRIORITY_TOO_LOW;
    }

    switch (req.requested_role) {
    case (uint8_t)AUTH_ROLE_MONITOR:
        /* Спостерігач не ексклюзивний: токен видається кожному охочому. */
        reply_grant(a, h->source_id, now, AUTH_ROLE_MONITOR, AUTH_STATUS_OK,
                    (uint16_t)AUTH_LEASE_TIMEOUT_MS, next_nonce(a));
        return AUTH_STATUS_OK;

    case (uint8_t)AUTH_ROLE_PILOT:
        if (req.target_gcs_id != 0u && h->source_id == a->pilot.gcs_id &&
            token_active(&a->pilot, now)) {
            if (h->token_nonce != a->pilot.nonce) {
                reply_grant(a, h->source_id, now, AUTH_ROLE_NONE,
                            AUTH_ERR_UNAUTHORIZED, 0u, 0u);
                return AUTH_ERR_UNAUTHORIZED;
            }
            return start_handover(a, h, req.target_gcs_id, now);
        }
        if (a->state == AUTH_STATE_HANDOVER_WAIT_STICK) {
            reply_grant(a, h->source_id, now, AUTH_ROLE_NONE,
                        AUTH_ERR_TOKEN_ALREADY_TAKEN, 0u, 0u);
            return AUTH_ERR_TOKEN_ALREADY_TAKEN;
        }
        return grant_exclusive(a, &a->pilot, AUTH_ROLE_PILOT, h, now);

    case (uint8_t)AUTH_ROLE_PAYLOAD:
        return grant_exclusive(a, &a->payload, AUTH_ROLE_PAYLOAD, h, now);

    default:
        reply_grant(a, h->source_id, now, AUTH_ROLE_NONE, AUTH_ERR_UNAUTHORIZED, 0u, 0u);
        return AUTH_ERR_UNAUTHORIZED;
    }
}

static bool sticks_in_deadband(const msg_stick_check_t *s, int16_t vehicle_throttle)
{
    const int16_t d = AUTH_DEADBAND_UNITS;
    const bool centered = (s->roll_axis >= -d && s->roll_axis <= d) &&
                          (s->pitch_axis >= -d && s->pitch_axis <= d) &&
                          (s->yaw_axis >= -d && s->yaw_axis <= d);
    int32_t diff = (int32_t)s->throttle_axis - (int32_t)vehicle_throttle;
    if (diff < 0) {
        diff = -diff;
    }
    return centered && diff <= d;
}

static auth_status_code_t on_stick_check(auth_arbiter_t *a, const auth_header_t *h,
                                         const uint8_t *pl, uint32_t now)
{
    if (a->state != AUTH_STATE_HANDOVER_WAIT_STICK || h->source_id != a->handover_to) {
        reply_grant(a, h->source_id, now, AUTH_ROLE_NONE, AUTH_ERR_UNAUTHORIZED, 0u, 0u);
        return AUTH_ERR_UNAUTHORIZED;
    }

    msg_stick_check_t sticks;
    memcpy(&sticks, pl, sizeof sticks);

    /* Прапорець is_neutral — думка станції; борт рахує сам. Довіритися
       чужому «в мене все по нулях» означає віддати кермо відхиленим стікам. */
    if (!sticks_in_deadband(&sticks, a->vehicle_throttle)) {
        reply_grant(a, h->source_id, now, AUTH_ROLE_NONE,
                    AUTH_ERR_STICK_NOT_NEUTRAL, 0u, 0u);
        return AUTH_ERR_STICK_NOT_NEUTRAL;
    }

    /* Атомарний світч: старий nonce вмирає тим самим присвоєнням, яким
       народжується новий, — проміжного стану «керма ні в кого» немає. */
    const uint8_t old_pilot = a->pilot.gcs_id;
    a->pilot.gcs_id = a->handover_to;
    a->pilot.nonce = next_nonce(a);
    a->pilot.lease_deadline_ms = now + AUTH_LEASE_TIMEOUT_MS;
    a->state = AUTH_STATE_PILOT_ACTIVE;
    a->handover_from = 0u;
    a->handover_to = 0u;

    reply_grant(a, a->pilot.gcs_id, now, AUTH_ROLE_PILOT, AUTH_STATUS_OK,
                (uint16_t)AUTH_LEASE_TIMEOUT_MS, a->pilot.nonce);
    if (old_pilot != 0u) {
        emit_revoke(a, old_pilot, now, AUTH_ROLE_PILOT, AUTH_REVOKE_HANDOVER);
    }
    broadcast_status(a, now);
    return AUTH_STATUS_OK;
}

static auth_status_code_t on_override(auth_arbiter_t *a, const auth_header_t *h,
                                      const uint8_t *pl, uint32_t now)
{
    msg_commander_override_t ovr;
    memcpy(&ovr, pl, sizeof ovr);

    const uint32_t expect = auth_sign_override(a->commander_key, h->source_id,
                                               h->seq_num, h->timestamp_ms);
    if (ovr.signature_hash != expect) {
        reply_grant(a, h->source_id, now, AUTH_ROLE_NONE, AUTH_ERR_UNAUTHORIZED, 0u, 0u);
        return AUTH_ERR_UNAUTHORIZED;
    }

    a->commander.gcs_id = h->source_id;
    a->commander.nonce = next_nonce(a);
    a->commander.lease_deadline_ms = now + AUTH_LEASE_TIMEOUT_MS;

    if (ovr.action_command == (uint8_t)AUTH_OVERRIDE_RELEASE) {
        /* Командир сам знімає блокування: токени лишаються вільними. */
        a->state = AUTH_STATE_IDLE;
        a->pending_failsafe = AUTH_FAILSAFE_NONE;
        reply_grant(a, h->source_id, now, AUTH_ROLE_COMMANDER, AUTH_STATUS_OK,
                    (uint16_t)AUTH_LEASE_TIMEOUT_MS, a->commander.nonce);
        broadcast_status(a, now);
        return AUTH_STATUS_OK;
    }

    /* Перехоплення рве і незавершену передачу зміни. */
    if (a->pilot.gcs_id != 0u) {
        emit_revoke(a, a->pilot.gcs_id, now, AUTH_ROLE_PILOT, AUTH_REVOKE_COMMANDER);
    }
    if (a->payload.gcs_id != 0u) {
        emit_revoke(a, a->payload.gcs_id, now, AUTH_ROLE_PAYLOAD, AUTH_REVOKE_COMMANDER);
    }
    token_clear(&a->pilot);
    token_clear(&a->payload);
    a->handover_from = 0u;
    a->handover_to = 0u;
    a->state = AUTH_STATE_COMMANDER_LOCKED;
    a->pending_failsafe = (ovr.action_command == (uint8_t)AUTH_OVERRIDE_RTL)
                              ? AUTH_FAILSAFE_RTL
                              : AUTH_FAILSAFE_BRAKE;

    reply_grant(a, h->source_id, now, AUTH_ROLE_COMMANDER, AUTH_STATUS_OK,
                (uint16_t)AUTH_LEASE_TIMEOUT_MS, a->commander.nonce);
    broadcast_status(a, now);
    return AUTH_STATUS_OK;
}

/* ---- вхідна точка обробки кадру ------------------------------------- */

auth_status_code_t auth_arbiter_handle(auth_arbiter_t *a, uint32_t now,
                                       const uint8_t *frame, size_t len)
{
    auth_header_t h;
    const uint8_t *pl = NULL;

    const auth_status_code_t st = auth_frame_decode(frame, len, &h, &pl);
    if (st != AUTH_STATUS_OK) {
        /* Початок заголовка стабільний між версіями, тож відправника
           видно навіть у несумісному кадрі — і йому можна відповісти. */
        if (st == AUTH_ERR_BAD_VERSION && len >= 5u) {
            reply_grant(a, frame[4], now, AUTH_ROLE_NONE, AUTH_ERR_BAD_VERSION, 0u, 0u);
        }
        return st;
    }

    if (h.target_id != a->self_id && h.target_id != AUTH_BROADCAST_ID) {
        return AUTH_STATUS_OK;  /* кадр не нам: у спільній мережі це норма */
    }

    const size_t need = expected_payload_size(h.msg_id);
    if (need == (size_t)-1) {
        return AUTH_ERR_UNAUTHORIZED;  /* напрямок FCU→GCS, від станції не буває */
    }
    if (h.payload_len != need) {
        return AUTH_ERR_BAD_LENGTH;
    }
    if (!peer_seq_ok(a, h.source_id, h.seq_num)) {
        return AUTH_ERR_REPLAY;
    }

    switch (h.msg_id) {
    case MSG_AUTH_HEARTBEAT:       return on_heartbeat(a, &h, pl, now);
    case MSG_AUTH_TOKEN_REQ:       return on_token_req(a, &h, pl, now);
    case MSG_HANDOVER_STICK_CHECK: return on_stick_check(a, &h, pl, now);
    case MSG_COMMANDER_OVERRIDE:   return on_override(a, &h, pl, now);
    default:                       return AUTH_ERR_UNAUTHORIZED;
    }
}

auth_failsafe_t auth_arbiter_tick(auth_arbiter_t *a, uint32_t now)
{
    /* Прострочена оренда пілота: стіки глухнуть, автопілот іде в LOITER,
       а токен лишається вільним — резервний пульт бере його негайно. */
    if (a->pilot.gcs_id != 0u && !token_active(&a->pilot, now)) {
        emit_revoke(a, a->pilot.gcs_id, now, AUTH_ROLE_PILOT, AUTH_REVOKE_LEASE_EXPIRED);
        token_clear(&a->pilot);
        if (a->state != AUTH_STATE_COMMANDER_LOCKED) {
            a->state = AUTH_STATE_LINK_LOST;
            a->pending_failsafe = AUTH_FAILSAFE_LOITER;
        }
        a->handover_from = 0u;
        a->handover_to = 0u;
        broadcast_status(a, now);
    }

    if (a->payload.gcs_id != 0u && !token_active(&a->payload, now)) {
        emit_revoke(a, a->payload.gcs_id, now, AUTH_ROLE_PAYLOAD, AUTH_REVOKE_LEASE_EXPIRED);
        token_clear(&a->payload);
        broadcast_status(a, now);
    }

    /* Змінний пілот не відповів за п'ять секунд — токен лишається старому. */
    if (a->state == AUTH_STATE_HANDOVER_WAIT_STICK &&
        !time_before(now, a->handover_deadline_ms)) {
        const uint8_t declined = a->handover_to;
        a->handover_from = 0u;
        a->handover_to = 0u;
        a->state = AUTH_STATE_PILOT_ACTIVE;
        emit_revoke(a, declined, now, AUTH_ROLE_NONE, AUTH_REVOKE_HANDOVER);
        broadcast_status(a, now);
    }

    const auth_failsafe_t action = a->pending_failsafe;
    a->pending_failsafe = AUTH_FAILSAFE_NONE;
    return action;
}

bool auth_arbiter_accept_control(const auth_arbiter_t *a, uint32_t now,
                                 uint8_t source_id, uint32_t nonce,
                                 auth_role_flags_t plane)
{
    if (nonce == 0u) {
        return false;
    }

    if (plane == AUTH_ROLE_PILOT) {
        if (a->state == AUTH_STATE_COMMANDER_LOCKED) {
            return false;
        }
        return token_active(&a->pilot, now) &&
               a->pilot.gcs_id == source_id && a->pilot.nonce == nonce;
    }

    if (plane == AUTH_ROLE_PAYLOAD) {
        return token_active(&a->payload, now) &&
               a->payload.gcs_id == source_id && a->payload.nonce == nonce;
    }

    /* Монітор керувати не може за означенням: deny-by-default. */
    return false;
}
