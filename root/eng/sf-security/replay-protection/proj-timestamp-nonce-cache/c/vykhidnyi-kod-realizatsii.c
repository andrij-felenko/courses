#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <stdio.h>
#include <assert.h>

#define NONCE_LEN 16
#define DIGEST_LEN 32
#define NONCE_CACHE_CAPACITY 1024
#define DEFAULT_SKEW_TOLERANCE_SEC 300

typedef enum {
    AUTH_OK = 0,
    AUTH_TIMESTAMP_SKEW = 1,
    AUTH_REPLAY_DETECTED = 2,
    AUTH_INVALID_SIGNATURE = 3
} auth_result_t;

typedef struct {
    uint8_t nonce[NONCE_LEN];
    time_t expires_at;
    bool occupied;
} nonce_entry_t;

typedef struct {
    nonce_entry_t entries[NONCE_CACHE_CAPACITY];
    size_t next_idx;
    uint32_t tolerance_sec;
} replay_guard_t;

// Порівняння байтових масивів у константному часі (захист від Timing Attacks)
static bool crypto_verify_equal(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

// Ініціалізація захисного фільтра
void replay_guard_init(replay_guard_t *g, uint32_t tolerance_sec) {
    memset(g->entries, 0, sizeof(g->entries));
    g->next_idx = 0;
    g->tolerance_sec = (tolerance_sec > 0) ? tolerance_sec : DEFAULT_SKEW_TOLERANCE_SEC;
}

// Повна перевірка запиту та фіксація Nonce у разі успіху
auth_result_t replay_guard_verify(
    replay_guard_t *g,
    const uint8_t nonce[NONCE_LEN],
    time_t req_timestamp,
    time_t now,
    const uint8_t expected_sig[DIGEST_LEN],
    const uint8_t provided_sig[DIGEST_LEN]
) {
    // 1. Перевірка допустимого відхилення часової мітки
    int64_t diff = (int64_t)now - (int64_t)req_timestamp;
    if (diff < -(int64_t)g->tolerance_sec || diff > (int64_t)g->tolerance_sec) {
        return AUTH_TIMESTAMP_SKEW;
    }

    // 2. Перевірка наявності Nonce в кеші
    for (size_t i = 0; i < NONCE_CACHE_CAPACITY; ++i) {
        if (g->entries[i].occupied && g->entries[i].expires_at >= now) {
            if (memcmp(g->entries[i].nonce, nonce, NONCE_LEN) == 0) {
                return AUTH_REPLAY_DETECTED;
            }
        }
    }

    // 3. Константно-часова перевірка цифрового підпису / HMAC
    if (!crypto_verify_equal(expected_sig, provided_sig, DIGEST_LEN)) {
        return AUTH_INVALID_SIGNATURE;
    }

    // 4. Успіх: фіксуємо Nonce у кільцевому буфері кешу
    nonce_entry_t *entry = &g->entries[g->next_idx];
    memcpy(entry->nonce, nonce, NONCE_LEN);
    entry->expires_at = now + (time_t)(2 * g->tolerance_sec);
    entry->occupied = true;

    g->next_idx = (g->next_idx + 1) % NONCE_CACHE_CAPACITY;
    return AUTH_OK;
}
