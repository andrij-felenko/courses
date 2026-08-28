#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <openssl/hmac.h>
#include <openssl/rand.h>

#define NONCE_LEN             16
#define HMAC_LEN              32
#define MAX_CHALLENGE_AGE_SEC 30
#define REPLAY_CACHE_SIZE     256

#pragma pack(push, 1)
typedef struct {
    uint8_t  nonce[NONCE_LEN];
    uint64_t timestamp_sec;
    uint8_t  server_mac[HMAC_LEN];
} challenge_token_t;

typedef struct {
    uint32_t client_id;
    uint8_t  response_mac[HMAC_LEN];
} auth_response_t;
#pragma pack(pop)

/* Циклічний буфер для запам'ятовування використаних nonce */
typedef struct {
    uint8_t nonces[REPLAY_CACHE_SIZE][NONCE_LEN];
    size_t  head;
} replay_cache_t;

/* Порівняння масивів байтів за сталий час (Constant-Time) */
static int constant_time_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *ua = (const uint8_t *)a;
    const uint8_t *ub = (const uint8_t *)b;
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (ua[i] ^ ub[i]);
    }
    return result == 0 ? 0 : -1;
}

/* Генерація безстанового виклику сервером */
int server_create_challenge(const uint8_t *server_key, size_t server_key_len,
                            uint32_t client_id, challenge_token_t *out_token) {
    if (RAND_bytes(out_token->nonce, NONCE_LEN) != 1) {
        return -1;
    }
    out_token->timestamp_sec = (uint64_t)time(NULL);

    /* Обчислення MAC талона: HMAC(K_server, Nonce || Timestamp || ClientID) */
    uint8_t sign_buf[NONCE_LEN + sizeof(uint64_t) + sizeof(uint32_t)];
    memcpy(sign_buf, out_token->nonce, NONCE_LEN);
    memcpy(sign_buf + NONCE_LEN, &out_token->timestamp_sec, sizeof(uint64_t));
    memcpy(sign_buf + NONCE_LEN + sizeof(uint64_t), &client_id, sizeof(uint32_t));

    unsigned int mac_len = 0;
    if (!HMAC(EVP_sha256(), server_key, (int)server_key_len,
              sign_buf, sizeof(sign_buf), out_token->server_mac, &mac_len)) {
        return -1;
    }
    return 0;
}

/* Обчислення відповіді клієнтом: HMAC(K_client, Token || ActionContext) */
int client_compute_response(const uint8_t *client_secret, size_t secret_len,
                            uint32_t client_id,
                            const challenge_token_t *token,
                            const char *action_context,
                            auth_response_t *out_resp) {
    out_resp->client_id = client_id;

    size_t ctx_len = strlen(action_context);
    size_t total_payload = sizeof(challenge_token_t) + ctx_len;
    uint8_t *payload = (uint8_t *)malloc(total_payload);
    if (!payload) return -1;

    memcpy(payload, token, sizeof(challenge_token_t));
    memcpy(payload + sizeof(challenge_token_t), action_context, ctx_len);

    unsigned int mac_len = 0;
    uint8_t *res = HMAC(EVP_sha256(), client_secret, (int)secret_len,
                        payload, total_payload, out_resp->response_mac, &mac_len);
    free(payload);
    return res ? 0 : -1;
}

/* Перевірка відсутності в кеші щойно бачених nonce */
static int check_and_record_nonce(replay_cache_t *cache, const uint8_t *nonce) {
    for (size_t i = 0; i < REPLAY_CACHE_SIZE; ++i) {
        if (constant_time_memcmp(cache->nonces[i], nonce, NONCE_LEN) == 0) {
            return -1; /* Знайдено в кеші: спроба Replay-атаки! */
        }
    }
    memcpy(cache->nonces[cache->head], nonce, NONCE_LEN);
    cache->head = (cache->head + 1) % REPLAY_CACHE_SIZE;
    return 0;
}

/* Верифікація відповіді клієнта сервером */
int server_verify_response(const uint8_t *server_key, size_t server_key_len,
                           const uint8_t *client_secret, size_t client_secret_len,
                           replay_cache_t *cache,
                           const challenge_token_t *token,
                           const auth_response_t *resp,
                           const char *expected_action) {
    /* 1. Перевірка цілісності та автентичності талона сервера */
    uint8_t sign_buf[NONCE_LEN + sizeof(uint64_t) + sizeof(uint32_t)];
    memcpy(sign_buf, token->nonce, NONCE_LEN);
    memcpy(sign_buf + NONCE_LEN, &token->timestamp_sec, sizeof(uint64_t));
    memcpy(sign_buf + NONCE_LEN + sizeof(uint64_t), &resp->client_id, sizeof(uint32_t));

    uint8_t expected_server_mac[HMAC_LEN];
    unsigned int mac_len = 0;
    if (!HMAC(EVP_sha256(), server_key, (int)server_key_len,
              sign_buf, sizeof(sign_buf), expected_server_mac, &mac_len)) {
        return -1;
    }
    if (constant_time_memcmp(token->server_mac, expected_server_mac, HMAC_LEN) != 0) {
        return -2; /* Талон виклику підроблений */
    }

    /* 2. Перевірка свіжості за міткою часу */
    uint64_t now = (uint64_t)time(NULL);
    if (now < token->timestamp_sec || (now - token->timestamp_sec) > MAX_CHALLENGE_AGE_SEC) {
        return -3; /* Термін дії виклику вичерпано або час у майбутньому */
    }

    /* 3. Перевірка кешу повторного використання */
    if (check_and_record_nonce(cache, token->nonce) != 0) {
        return -4; /* Replay Attack: цей nonce уже успішно оброблено */
    }

    /* 4. Перевірка відповіді клієнта на основі його секрету */
    size_t ctx_len = strlen(expected_action);
    size_t total_payload = sizeof(challenge_token_t) + ctx_len;
    uint8_t *payload = (uint8_t *)malloc(total_payload);
    if (!payload) return -1;

    memcpy(payload, token, sizeof(challenge_token_t));
    memcpy(payload + sizeof(challenge_token_t), expected_action, ctx_len);

    uint8_t expected_client_mac[HMAC_LEN];
    HMAC(EVP_sha256(), client_secret, (int)client_secret_len,
         payload, total_payload, expected_client_mac, &mac_len);
    free(payload);

    if (constant_time_memcmp(resp->response_mac, expected_client_mac, HMAC_LEN) != 0) {
        return -5; /* Невірний секрет або контекст операції */
    }

    return 0; /* Успішна автентифікація */
}
