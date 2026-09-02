/* Наскрізний прогін протоколу арбітражу на модельному годиннику:
   борт із арбітром і чотири станції в спільній радіомережі. */

#include <stdio.h>
#include <string.h>

#include "auth_arbiter.h"
#include "auth_frame.h"

#define GCS_PILOT     11u
#define GCS_PAYLOAD   12u
#define GCS_RELIEF    13u
#define GCS_COMMANDER 14u

#define FCU_ID        1u
#define COMMANDER_KEY 0xC0FFEE01u

typedef struct {
    uint8_t  id;
    uint16_t seq;
    uint32_t nonce;   /* видане бортом одноразове число, 0 — токена немає */
    uint8_t  role;
} station_t;

static station_t g_stations[] = {
    { GCS_PILOT,     0u, 0u, AUTH_ROLE_NONE },
    { GCS_PAYLOAD,   0u, 0u, AUTH_ROLE_NONE },
    { GCS_RELIEF,    0u, 0u, AUTH_ROLE_NONE },
    { GCS_COMMANDER, 0u, 0u, AUTH_ROLE_NONE },
};

static auth_arbiter_t g_fcu;
static uint32_t g_now;          /* модельний час, мс */
static int16_t  g_offer_throttle;  /* газ борту з отриманої оферти */

static station_t *station(uint8_t id)
{
    for (size_t i = 0; i < sizeof g_stations / sizeof g_stations[0]; ++i) {
        if (g_stations[i].id == id) {
            return &g_stations[i];
        }
    }
    return NULL;
}

static const char *status_name(auth_status_code_t st)
{
    switch (st) {
    case AUTH_STATUS_OK:               return "OK";
    case AUTH_ERR_UNAUTHORIZED:        return "UNAUTHORIZED";
    case AUTH_ERR_TOKEN_ALREADY_TAKEN: return "TOKEN_ALREADY_TAKEN";
    case AUTH_ERR_STICK_NOT_NEUTRAL:   return "STICK_NOT_NEUTRAL";
    case AUTH_ERR_LEASE_EXPIRED:       return "LEASE_EXPIRED";
    case AUTH_ERR_PRIORITY_TOO_LOW:    return "PRIORITY_TOO_LOW";
    case AUTH_ERR_CRC_MISMATCH:        return "CRC_MISMATCH";
    case AUTH_ERR_BAD_MAGIC:           return "BAD_MAGIC";
    case AUTH_ERR_BAD_VERSION:         return "BAD_VERSION";
    case AUTH_ERR_BAD_LENGTH:          return "BAD_LENGTH";
    case AUTH_ERR_REPLAY:              return "REPLAY";
    default:                           return "?";
    }
}

static const char *state_name(uint8_t s)
{
    switch (s) {
    case AUTH_STATE_IDLE:                return "IDLE";
    case AUTH_STATE_PILOT_ACTIVE:        return "PILOT_ACTIVE";
    case AUTH_STATE_HANDOVER_WAIT_STICK: return "HANDOVER_WAIT_STICK";
    case AUTH_STATE_LINK_LOST:           return "LINK_LOST";
    case AUTH_STATE_COMMANDER_LOCKED:    return "COMMANDER_LOCKED";
    default:                             return "?";
    }
}

/* Усе, що борт випромінює, чують усі станції — це спільна радіомережа. */
static void on_board_emit(void *ctx, const uint8_t *frame, size_t len)
{
    (void)ctx;

    auth_header_t h;
    const uint8_t *pl = NULL;
    if (auth_frame_decode(frame, len, &h, &pl) != AUTH_STATUS_OK) {
        printf("      [ефір] пошкоджений кадр борту\n");
        return;
    }

    switch (h.msg_id) {
    case MSG_AUTH_TOKEN_GRANT: {
        msg_auth_token_grant_t g;
        memcpy(&g, pl, sizeof g);
        station_t *s = station(h.target_id);
        if (g.status == (uint8_t)AUTH_STATUS_OK) {
            if (s != NULL) {
                s->nonce = g.token_nonce;
                s->role = g.granted_role;
            }
            printf("      GRANT  → GCS#%u  роль=0x%02X  оренда=%u мс  nonce=0x%08X\n",
                   h.target_id, g.granted_role, g.lease_ms, g.token_nonce);
        } else {
            printf("      ВІДМОВА → GCS#%u  причина=%s\n",
                   h.target_id, status_name((auth_status_code_t)g.status));
        }
        break;
    }
    case MSG_AUTH_TOKEN_REVOKE: {
        msg_auth_token_revoke_t r;
        memcpy(&r, pl, sizeof r);
        station_t *s = station(h.target_id);
        if (s != NULL) {
            s->nonce = 0u;
            s->role = AUTH_ROLE_NONE;
        }
        printf("      REVOKE → GCS#%u  роль=0x%02X  причина=%u\n",
               h.target_id, r.revoked_role, r.reason);
        break;
    }
    case MSG_HANDOVER_OFFER: {
        msg_handover_offer_t o;
        memcpy(&o, pl, sizeof o);
        g_offer_throttle = o.throttle_target;
        printf("      OFFER  → GCS#%u  від GCS#%u  вікно=%u мс  газ=%d\n",
               o.to_gcs_id, o.from_gcs_id, o.timeout_ms, o.throttle_target);
        break;
    }
    case MSG_AUTH_STATUS: {
        msg_auth_status_t s;
        memcpy(&s, pl, sizeof s);
        printf("      STATUS: пілот=%u навантаження=%u командир=%u "
               "оренда=%u мс стан=%s\n",
               s.pilot_gcs_id, s.payload_gcs_id, s.commander_gcs_id,
               s.pilot_lease_remaining_ms, state_name(s.arbitration_state));
        break;
    }
    default:
        break;
    }
}

/* Станція складає кадр і кладе його в ефір; борт відповідає негайно. */
static auth_status_code_t send_from(station_t *s, uint16_t msg_id,
                                    const void *payload, size_t len)
{
    uint8_t buf[AUTH_MAX_FRAME];
    auth_header_t h;

    memset(&h, 0, sizeof h);
    h.msg_id       = msg_id;
    h.source_id    = s->id;
    h.target_id    = FCU_ID;
    h.seq_num      = ++s->seq;
    h.timestamp_ms = g_now;
    h.token_nonce  = s->nonce;

    const int n = auth_frame_encode(buf, sizeof buf, &h, payload, len);
    if (n < 0) {
        printf("      GCS#%u: кадр не склався\n", s->id);
        return AUTH_ERR_BAD_LENGTH;
    }
    return auth_arbiter_handle(&g_fcu, g_now, buf, (size_t)n);
}

static auth_status_code_t request_role(station_t *s, auth_role_flags_t role,
                                       uint8_t target, uint32_t key)
{
    msg_auth_token_req_t req;
    req.requested_role = (uint8_t)role;
    req.target_gcs_id  = target;
    req.auth_token     = key;
    return send_from(s, MSG_AUTH_TOKEN_REQ, &req, sizeof req);
}

static void heartbeat(station_t *s)
{
    msg_auth_heartbeat_t hb;
    hb.active_roles = s->role;
    hb.lease_requested_ms = (uint16_t)AUTH_LEASE_TIMEOUT_MS;
    (void)send_from(s, MSG_AUTH_HEARTBEAT, &hb, sizeof hb);
}

static void advance(uint32_t dt_ms)
{
    g_now += dt_ms;
    const auth_failsafe_t fs = auth_arbiter_tick(&g_fcu, g_now);
    if (fs != AUTH_FAILSAFE_NONE) {
        printf("      >>> автопілоту: %s\n",
               fs == AUTH_FAILSAFE_LOITER ? "LOITER" :
               fs == AUTH_FAILSAFE_RTL ? "RTL" : "BRAKE");
    }
}

/* Кадр стіків на 50 Гц: проходить лише крізь фільтр повноважень. */
static void push_control(station_t *s, auth_role_flags_t plane, const char *what)
{
    const bool ok = auth_arbiter_accept_control(&g_fcu, g_now, s->id, s->nonce, plane);
    printf("      GCS#%u %s → %s\n", s->id, what, ok ? "ВИКОНАНО" : "ВІДКИНУТО");
}

int main(void)
{
    auth_arbiter_init(&g_fcu, FCU_ID, COMMANDER_KEY, 0xA5A50F0Fu, on_board_emit, NULL);
    auth_arbiter_set_throttle(&g_fcu, 620);

    printf("=== 1. Розбір ролей ===\n");
    printf("  GCS#%u просить пілотування: %s\n", GCS_PILOT,
           status_name(request_role(station(GCS_PILOT), AUTH_ROLE_PILOT, 0u, 0u)));
    printf("  GCS#%u просить навантаження: %s\n", GCS_PAYLOAD,
           status_name(request_role(station(GCS_PAYLOAD), AUTH_ROLE_PAYLOAD, 0u, 0u)));

    printf("\n=== 2. Оператор навантаження хоче доворот носа на ціль ===\n");
    printf("  запит токена пілота: %s\n",
           status_name(request_role(station(GCS_PAYLOAD), AUTH_ROLE_PILOT, 0u, 0u)));
    push_control(station(GCS_PILOT), AUTH_ROLE_PILOT, "крен -20 град");
    push_control(station(GCS_PAYLOAD), AUTH_ROLE_PILOT, "крен +15 град (авто-ціль)");
    push_control(station(GCS_PAYLOAD), AUTH_ROLE_PAYLOAD, "поворот підвісу");

    printf("\n=== 3. Оренда живе на серцебитті ===\n");
    for (int i = 0; i < 4; ++i) {
        advance(250u);
        heartbeat(station(GCS_PILOT));
        heartbeat(station(GCS_PAYLOAD));
    }
    push_control(station(GCS_PILOT), AUTH_ROLE_PILOT, "крен -20 град");

    printf("\n=== 4. Пульт пілота замовк на 1200 мс ===\n");
    advance(1200u);
    push_control(station(GCS_PILOT), AUTH_ROLE_PILOT, "крен -20 град");
    printf("  вільний токен бере той самий пульт: %s\n",
           status_name(request_role(station(GCS_PILOT), AUTH_ROLE_PILOT, 0u, 0u)));

    printf("\n=== 5. Передача зміни на GCS#%u ===\n", GCS_RELIEF);
    printf("  ініціація: %s\n",
           status_name(request_role(station(GCS_PILOT), AUTH_ROLE_PILOT, GCS_RELIEF, 0u)));

    msg_stick_check_t sticks;
    memset(&sticks, 0, sizeof sticks);
    sticks.roll_axis = 120;                 /* стік відхилено */
    sticks.throttle_axis = g_offer_throttle;
    sticks.is_neutral = 1u;                 /* станція бреше, борт перевіряє */
    printf("  звірка з відхиленим стіком: %s\n",
           status_name(send_from(station(GCS_RELIEF), MSG_HANDOVER_STICK_CHECK,
                                 &sticks, sizeof sticks)));

    sticks.roll_axis = 8;                   /* у межах ±3% */
    printf("  звірка з нейтраллю: %s\n",
           status_name(send_from(station(GCS_RELIEF), MSG_HANDOVER_STICK_CHECK,
                                 &sticks, sizeof sticks)));
    push_control(station(GCS_PILOT), AUTH_ROLE_PILOT, "крен -20 град (старий nonce)");
    push_control(station(GCS_RELIEF), AUTH_ROLE_PILOT, "крен -20 град");

    printf("\n=== 6. Змінний пілот не відповів ===\n");
    printf("  ініціація на GCS#%u: %s\n", GCS_PAYLOAD,
           status_name(request_role(station(GCS_RELIEF), AUTH_ROLE_PILOT, GCS_PAYLOAD, 0u)));
    advance(5100u);
    printf("  токен лишився в GCS#%u\n", GCS_RELIEF);

    printf("\n=== 7. Перехоплення командиром ===\n");
    station_t *cmd = station(GCS_COMMANDER);
    printf("  токен командира: %s\n",
           status_name(request_role(cmd, AUTH_ROLE_COMMANDER, 0u, COMMANDER_KEY)));

    msg_commander_override_t bad = { 0u, (uint8_t)AUTH_OVERRIDE_HOLD, 0xDEADBEEFu };
    printf("  перехоплення з чужим підписом: %s\n",
           status_name(send_from(cmd, MSG_COMMANDER_OVERRIDE, &bad, sizeof bad)));

    msg_commander_override_t ovr;
    ovr.override_reason = 0u;
    ovr.action_command  = (uint8_t)AUTH_OVERRIDE_HOLD;
    /* Підпис накриває наступний seq і поточний час — повторити кадр не вийде. */
    ovr.signature_hash  = auth_sign_override(COMMANDER_KEY, cmd->id,
                                             (uint16_t)(cmd->seq + 1u), g_now);
    printf("  перехоплення з валідним підписом: %s\n",
           status_name(send_from(cmd, MSG_COMMANDER_OVERRIDE, &ovr, sizeof ovr)));
    advance(0u);
    push_control(station(GCS_RELIEF), AUTH_ROLE_PILOT, "крен -20 град");
    printf("  спроба взяти токен під блокуванням: %s\n",
           status_name(request_role(station(GCS_RELIEF), AUTH_ROLE_PILOT, 0u, 0u)));

    return 0;
}
