#include "prov_session.h"
#include "prov_platform.h"

#include <string.h>

/* Найдовший осмислений відкритий текст: [len][SSID][len][пароль]. */
#define PROV_PLAINTEXT_MAX (1 + PROV_MAX_SSID_LEN + 1 + PROV_MAX_PASS_LEN)

void prov_session_init(prov_session_t *s, const uint8_t *pop, size_t pop_len)
{
    memset(s, 0, sizeof(*s));
    s->pop = pop;
    s->pop_len = pop_len;
}

void prov_session_reset(prov_session_t *s)
{
    prov_secure_wipe(s->priv_key, sizeof(s->priv_key));
    prov_secure_wipe(s->session_key, sizeof(s->session_key));
    prov_secure_wipe(s->salt, sizeof(s->salt));
    memset(s->device_pub, 0, sizeof(s->device_pub));
    memset(s->nonce_prefix, 0, sizeof(s->nonce_prefix));
    s->last_counter = 0;
    s->have_nonce = false;
    s->established = false;
    /* pop_failures, locked_until_ms і lock_active НЕ чіпаємо. */
}

/* Порівняння через різницю переживає переповнення 32-бітного лічильника мс. */
static bool session_locked(prov_session_t *s)
{
    if (!s->lock_active) {
        return false;
    }
    if ((int32_t)(plat_uptime_ms() - s->locked_until_ms) >= 0) {
        s->lock_active = false;
        s->pop_failures = 0;
        return false;
    }
    return true;
}

static void lock_session(prov_session_t *s)
{
    s->lock_active = true;
    s->locked_until_ms = plat_uptime_ms() + PROV_LOCKOUT_MS;
    prov_session_reset(s);          /* ефемерні ключі — геть */
}

static uint64_t read_be64(const uint8_t *p)
{
    uint64_t v = 0;
    for (size_t i = 0; i < 8; ++i) {
        v = (v << 8) | p[i];
    }
    return v;
}

prov_status_t prov_session_handshake(prov_session_t *s,
                                     const uint8_t *request, size_t request_len,
                                     uint8_t *response_out, size_t *response_len)
{
    *response_len = 0;

    if (session_locked(s)) {
        return PROV_STATUS_LOCKED;
    }
    if (request_len != PROV_SESSION_REQ_SIZE) {
        return PROV_STATUS_INVALID_LEN;
    }

    const uint8_t *client_pub = request;
    const uint8_t *proof = request + PROV_KEY_SIZE;

    if (!prov_pubkey_acceptable(client_pub)) {
        return PROV_STATUS_CRYPTO_FAIL;
    }

    /* Доказ володіння звіряємо ДО того, як витрачати ECDH: інакше кожен
       перехожий змушував би нас рахувати скалярне множення. */
    if (!prov_pop_proof_valid(s->pop, s->pop_len, client_pub, proof)) {
        if (++s->pop_failures >= PROV_POP_MAX_FAILURES) {
            lock_session(s);
            return PROV_STATUS_LOCKED;
        }
        prov_session_reset(s);
        return PROV_STATUS_AUTH_FAIL;
    }

    /* Пара ефемерна: кожне рукостискання починає з нових ключів,
       тож запис старої сесії сніфером не розшифрує наступну. */
    prov_keypair(s->priv_key, s->device_pub);
    plat_random_bytes(s->salt, PROV_SALT_SIZE);

    if (!prov_derive_session_key(s->priv_key, client_pub, s->device_pub,
                                 s->salt, s->pop, s->pop_len, s->session_key)) {
        prov_session_reset(s);
        return PROV_STATUS_CRYPTO_FAIL;
    }

    s->pop_failures = 0;
    s->have_nonce = false;
    s->last_counter = 0;
    s->established = true;

    memcpy(response_out, s->device_pub, PROV_KEY_SIZE);
    memcpy(response_out + PROV_KEY_SIZE, s->salt, PROV_SALT_SIZE);
    *response_len = PROV_SESSION_RESP_SIZE;
    return PROV_STATUS_SUCCESS;
}

/* Розбір [ssid_len][SSID][pass_len][пароль] із перевіркою кожної межі. */
static prov_status_t parse_credentials(const uint8_t *pt, size_t len, prov_credentials_t *out)
{
    if (len < 2) {
        return PROV_STATUS_INVALID_LEN;
    }

    size_t offset = 0;
    uint8_t ssid_len = pt[offset++];
    if (ssid_len == 0 || ssid_len > PROV_MAX_SSID_LEN || offset + ssid_len >= len) {
        return PROV_STATUS_INVALID_LEN;   /* потрібен ще щонайменше байт довжини пароля */
    }
    for (size_t i = 0; i < ssid_len; ++i) {
        if (pt[offset + i] == 0) {
            return PROV_STATUS_INVALID_LEN;  /* нуль усередині обрізав би імʼя мережі */
        }
    }
    memcpy(out->ssid, pt + offset, ssid_len);
    out->ssid[ssid_len] = '\0';
    offset += ssid_len;

    uint8_t pass_len = pt[offset++];
    if (pass_len > PROV_MAX_PASS_LEN || offset + pass_len != len) {
        return PROV_STATUS_INVALID_LEN;   /* хвіст після пароля — привід відмовити */
    }
    /* WPA2: або відкрита мережа, або 8–63 символи парольної фрази, або 64 hex. */
    if (pass_len != 0 && pass_len < 8) {
        return PROV_STATUS_INVALID_LEN;
    }
    for (size_t i = 0; i < pass_len; ++i) {
        if (pt[offset + i] == 0) {
            return PROV_STATUS_INVALID_LEN;
        }
    }
    memcpy(out->password, pt + offset, pass_len);
    out->password[pass_len] = '\0';
    return PROV_STATUS_SUCCESS;
}

prov_status_t prov_session_config(prov_session_t *s,
                                  const uint8_t *payload, size_t payload_len,
                                  prov_credentials_t *out)
{
    memset(out, 0, sizeof(*out));

    if (session_locked(s)) {
        return PROV_STATUS_LOCKED;
    }
    if (!s->established) {
        return PROV_STATUS_AUTH_FAIL;
    }

    /* Кадр: [nonce 12][tag 16][шифротекст]. */
    const size_t header = PROV_NONCE_SIZE + PROV_TAG_SIZE;
    if (payload_len <= header) {
        return PROV_STATUS_INVALID_LEN;
    }

    const uint8_t *nonce = payload;
    const uint8_t *tag = payload + PROV_NONCE_SIZE;
    const uint8_t *ciphertext = payload + header;
    size_t cipher_len = payload_len - header;

    if (cipher_len > PROV_PLAINTEXT_MAX) {
        return PROV_STATUS_INVALID_LEN;
    }

    /* Nonce під одним ключем не повторюється — це вимога GCM, а не побажання.
       Перевіряємо ДО розшифрування, а стан рухаємо тільки після успіху,
       щоб сміттєвим пакетом не можна було зафіксувати чужий префікс. */
    uint64_t counter = read_be64(nonce + 4);
    if (s->have_nonce) {
        if (memcmp(s->nonce_prefix, nonce, sizeof(s->nonce_prefix)) != 0 ||
            counter <= s->last_counter) {
            return PROV_STATUS_REPLAY;
        }
    } else if (counter == 0) {
        return PROV_STATUS_REPLAY;
    }

    uint8_t plaintext[PROV_PLAINTEXT_MAX];
    if (!plat_aes_gcm_decrypt(s->session_key, nonce, tag, ciphertext, cipher_len, plaintext)) {
        prov_secure_wipe(plaintext, sizeof(plaintext));
        return PROV_STATUS_CRYPTO_FAIL;   /* тег GMAC не зійшовся: пакет підроблено або побито */
    }

    prov_status_t st = parse_credentials(plaintext, cipher_len, out);
    prov_secure_wipe(plaintext, sizeof(plaintext));

    if (st != PROV_STATUS_SUCCESS) {
        prov_secure_wipe(out, sizeof(*out));
        return st;
    }

    memcpy(s->nonce_prefix, nonce, sizeof(s->nonce_prefix));
    s->last_counter = counter;
    s->have_nonce = true;
    return PROV_STATUS_SUCCESS;
}
