#ifndef PROV_SESSION_H
#define PROV_SESSION_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "prov_crypto.h"

#define PROV_MAX_SSID_LEN     32
#define PROV_MAX_PASS_LEN     64
#define PROV_POP_MAX_FAILURES 3
#define PROV_LOCKOUT_MS       30000u

/* Запис у prov-session: [client_pub 32][proof 32]. */
#define PROV_SESSION_REQ_SIZE  (PROV_KEY_SIZE + PROV_PROOF_SIZE)
/* Читання з prov-session: [device_pub 32][salt 16]. */
#define PROV_SESSION_RESP_SIZE (PROV_KEY_SIZE + PROV_SALT_SIZE)

typedef enum {
    PROV_STATUS_SUCCESS = 0,
    PROV_STATUS_INVALID_LEN,
    PROV_STATUS_CRYPTO_FAIL,
    PROV_STATUS_AUTH_FAIL,
    PROV_STATUS_STATION_TIMEOUT,
    PROV_STATUS_LOCKED,
    PROV_STATUS_REPLAY,
    PROV_STATUS_STORAGE_FAIL
} prov_status_t;

typedef struct {
    char ssid[PROV_MAX_SSID_LEN + 1];
    char password[PROV_MAX_PASS_LEN + 1];
} prov_credentials_t;

typedef struct {
    uint8_t  priv_key[PROV_KEY_SIZE];
    uint8_t  device_pub[PROV_KEY_SIZE];
    uint8_t  session_key[PROV_KEY_SIZE];
    uint8_t  salt[PROV_SALT_SIZE];
    bool     established;

    /* Захист від повтору: nonce клієнта — [префікс 4][лічильник BE 8]. */
    uint8_t  nonce_prefix[4];
    uint64_t last_counter;
    bool     have_nonce;

    /* Захист від перебору PoP. Переживає розрив зʼєднання — інакше
       брутфорс зводився б до перепідключення після кожної спроби. */
    uint8_t  pop_failures;
    uint32_t locked_until_ms;
    bool     lock_active;

    const uint8_t *pop;
    size_t   pop_len;
} prov_session_t;

void prov_session_init(prov_session_t *s, const uint8_t *pop, size_t pop_len);

/* Розрив зʼєднання чи таймаут нагляду: ефемерні ключі геть, блокування лишається. */
void prov_session_reset(prov_session_t *s);

prov_status_t prov_session_handshake(prov_session_t *s,
                                     const uint8_t *request, size_t request_len,
                                     uint8_t *response_out, size_t *response_len);

prov_status_t prov_session_config(prov_session_t *s,
                                  const uint8_t *payload, size_t payload_len,
                                  prov_credentials_t *out);

#endif /* PROV_SESSION_H */
