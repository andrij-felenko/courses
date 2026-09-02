#ifndef AUTH_ARBITER_H
#define AUTH_ARBITER_H

#include <stddef.h>
#include "auth_protocol.h"

/* Скільки станцій арбітр тримає в таблиці лічильників послідовності. */
#define AUTH_MAX_PEERS 8

/* Куди борт віддає власні кадри (радіомодем, UART, сокет). */
typedef void (*auth_emit_fn)(void *ctx, const uint8_t *frame, size_t len);

typedef struct {
    uint8_t  gcs_id;             /* 0 — токен вільний */
    uint32_t nonce;              /* одноразове число цієї оренди */
    uint32_t lease_deadline_ms;  /* час, коли оренда протухає */
} auth_token_t;

typedef struct {
    uint8_t  gcs_id;
    uint16_t last_seq;
    bool     seen;
} auth_peer_t;

typedef struct {
    uint8_t  self_id;         /* System ID борту */
    uint32_t commander_key;   /* попередньо узгоджений ключ командира */
    uint32_t rng;             /* стан генератора nonce */
    uint16_t tx_seq;          /* лічильник власних кадрів */

    auth_token_t pilot;
    auth_token_t payload;
    auth_token_t commander;

    auth_arb_state_t state;
    uint8_t  handover_from;
    uint8_t  handover_to;
    uint32_t handover_deadline_ms;

    int16_t  vehicle_throttle;    /* поточний газ борту, 0..1000 */
    auth_failsafe_t pending_failsafe;

    auth_peer_t peers[AUTH_MAX_PEERS];

    auth_emit_fn emit;
    void        *emit_ctx;
} auth_arbiter_t;

void auth_arbiter_init(auth_arbiter_t *a, uint8_t self_id, uint32_t commander_key,
                       uint32_t seed, auth_emit_fn emit, void *emit_ctx);

/* Поточне положення газу борту — під нього вирівнюється змінний пілот. */
void auth_arbiter_set_throttle(auth_arbiter_t *a, int16_t throttle);

/* Обробка одного вхідного кадру з мережі. */
auth_status_code_t auth_arbiter_handle(auth_arbiter_t *a, uint32_t now_ms,
                                       const uint8_t *frame, size_t len);

/* Періодичний хід годинника: тайм-аути оренди та передачі зміни.
   Повертає дію, якої арбітр вимагає від автопілота (зазвичай NONE). */
auth_failsafe_t auth_arbiter_tick(auth_arbiter_t *a, uint32_t now_ms);

/* Фільтр керівних пакетів на 50 Гц: чи має ця станція право рухати
   саме цією площиною керування саме зараз. */
bool auth_arbiter_accept_control(const auth_arbiter_t *a, uint32_t now_ms,
                                 uint8_t source_id, uint32_t nonce,
                                 auth_role_flags_t plane);

void auth_arbiter_fill_status(const auth_arbiter_t *a, uint32_t now_ms,
                              msg_auth_status_t *out);

#endif /* AUTH_ARBITER_H */
