#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>

#define HASH_BUCKETS 1024
#define DEFAULT_LEASE_SEC 30
#define DEFAULT_RETENTION_SEC 86400

typedef enum {
    IDEM_IN_PROGRESS = 0,
    IDEM_COMMITTED   = 1,
    IDEM_FAILED      = 2
} IdemState;

typedef enum {
    IDEM_ACTION_EXECUTE,
    IDEM_ACTION_RETURN_CACHED,
    IDEM_ACTION_IN_FLIGHT_CONFLICT,
    IDEM_ACTION_PAYLOAD_MISMATCH,
    IDEM_ACTION_ERROR
} IdemAction;

typedef struct IdemRecord {
    char *key;
    uint64_t payload_hash;
    IdemState state;
    int response_code;
    char *response_body;
    time_t expires_at;
    struct IdemRecord *next;
} IdemRecord;

typedef struct {
    IdemRecord *buckets[HASH_BUCKETS];
    pthread_mutex_t mutex;
} IdemEngine;

/* 64-бітний хеш FNV-1a для ключів і тіла запитів */
static uint64_t hash_bytes(const void *data, size_t len) {
    const uint8_t *ptr = (const uint8_t *)data;
    uint64_t h = 0xcbf29ce484222325ULL;
    for (size_t i = 0; i < len; ++i) {
        h ^= (uint64_t)ptr[i];
        h *= 0x100000001b3ULL;
    }
    return h;
}

static uint64_t hash_string(const char *s) {
    return hash_bytes(s, strlen(s));
}

IdemEngine *idem_create(void) {
    IdemEngine *engine = (IdemEngine *)calloc(1, sizeof(IdemEngine));
    if (!engine) return NULL;
    if (pthread_mutex_init(&engine->mutex, NULL) != 0) {
        free(engine);
        return NULL;
    }
    return engine;
}

void idem_destroy(IdemEngine *engine) {
    if (!engine) return;
    pthread_mutex_lock(&engine->mutex);
    for (int i = 0; i < HASH_BUCKETS; ++i) {
        IdemRecord *cur = engine->buckets[i];
        while (cur) {
            IdemRecord *next = cur->next;
            free(cur->key);
            free(cur->response_body);
            free(cur);
            cur = next;
        }
    }
    pthread_mutex_unlock(&engine->mutex);
    pthread_mutex_destroy(&engine->mutex);
    free(engine);
}

IdemAction idem_acquire(IdemEngine *engine, const char *key, const void *payload,
                        size_t payload_len, int *out_code, char *out_body, size_t body_buf_sz) {
    if (!engine || !key) return IDEM_ACTION_ERROR;

    time_t now = time(NULL);
    uint64_t p_hash = hash_bytes(payload, payload_len);
    uint64_t k_hash = hash_string(key);
    size_t idx = k_hash % HASH_BUCKETS;

    pthread_mutex_lock(&engine->mutex);

    IdemRecord *rec = engine->buckets[idx];
    while (rec) {
        if (strcmp(rec->key, key) == 0) {
            break;
        }
        rec = rec->next;
    }

    if (rec) {
        if (rec->state == IDEM_COMMITTED) {
            if (rec->payload_hash != p_hash) {
                pthread_mutex_unlock(&engine->mutex);
                return IDEM_ACTION_PAYLOAD_MISMATCH;
            }
            if (out_code) *out_code = rec->response_code;
            if (out_body && rec->response_body) {
                strncpy(out_body, rec->response_body, body_buf_sz - 1);
                out_body[body_buf_sz - 1] = '\0';
            }
            pthread_mutex_unlock(&engine->mutex);
            return IDEM_ACTION_RETURN_CACHED;
        }

        if (rec->state == IDEM_IN_PROGRESS) {
            if (now < rec->expires_at) {
                /* Оренда діє — паралельний дублікат */
                pthread_mutex_unlock(&engine->mutex);
                return IDEM_ACTION_IN_FLIGHT_CONFLICT;
            }
            /* Оренда застаріла — перехоплюємо виконання */
            rec->payload_hash = p_hash;
            rec->expires_at = now + DEFAULT_LEASE_SEC;
            pthread_mutex_unlock(&engine->mutex);
            return IDEM_ACTION_EXECUTE;
        }

        if (rec->state == IDEM_FAILED) {
            /* Дозволений повтор після помилки */
            rec->state = IDEM_IN_PROGRESS;
            rec->payload_hash = p_hash;
            rec->expires_at = now + DEFAULT_LEASE_SEC;
            pthread_mutex_unlock(&engine->mutex);
            return IDEM_ACTION_EXECUTE;
        }
    }

    /* Новий запис */
    IdemRecord *new_rec = (IdemRecord *)calloc(1, sizeof(IdemRecord));
    if (!new_rec) {
        pthread_mutex_unlock(&engine->mutex);
        return IDEM_ACTION_ERROR;
    }
    new_rec->key = strdup(key);
    new_rec->payload_hash = p_hash;
    new_rec->state = IDEM_IN_PROGRESS;
    new_rec->expires_at = now + DEFAULT_LEASE_SEC;
    new_rec->next = engine->buckets[idx];
    engine->buckets[idx] = new_rec;

    pthread_mutex_unlock(&engine->mutex);
    return IDEM_ACTION_EXECUTE;
}

bool idem_commit(IdemEngine *engine, const char *key, int code, const char *body) {
    if (!engine || !key) return false;

    time_t now = time(NULL);
    uint64_t k_hash = hash_string(key);
    size_t idx = k_hash % HASH_BUCKETS;

    pthread_mutex_lock(&engine->mutex);
    IdemRecord *rec = engine->buckets[idx];
    while (rec) {
        if (strcmp(rec->key, key) == 0) {
            if (rec->state == IDEM_IN_PROGRESS) {
                rec->state = IDEM_COMMITTED;
                rec->response_code = code;
                free(rec->response_body);
                rec->response_body = body ? strdup(body) : NULL;
                rec->expires_at = now + DEFAULT_RETENTION_SEC;
                pthread_mutex_unlock(&engine->mutex);
                return true;
            }
            break;
        }
        rec = rec->next;
    }
    pthread_mutex_unlock(&engine->mutex);
    return false;
}

bool idem_fail(IdemEngine *engine, const char *key) {
    if (!engine || !key) return false;

    uint64_t k_hash = hash_string(key);
    size_t idx = k_hash % HASH_BUCKETS;

    pthread_mutex_lock(&engine->mutex);
    IdemRecord *rec = engine->buckets[idx];
    while (rec) {
        if (strcmp(rec->key, key) == 0) {
            if (rec->state == IDEM_IN_PROGRESS) {
                rec->state = IDEM_FAILED;
                pthread_mutex_unlock(&engine->mutex);
                return true;
            }
            break;
        }
        rec = rec->next;
    }
    pthread_mutex_unlock(&engine->mutex);
    return false;
}

size_t idem_evict_expired(IdemEngine *engine) {
    if (!engine) return 0;
    time_t now = time(NULL);
    size_t count = 0;

    pthread_mutex_lock(&engine->mutex);
    for (int i = 0; i < HASH_BUCKETS; ++i) {
        IdemRecord **curr_ptr = &engine->buckets[i];
        while (*curr_ptr) {
            IdemRecord *entry = *curr_ptr;
            if (now >= entry->expires_at) {
                *curr_ptr = entry->next;
                free(entry->key);
                free(entry->response_body);
                free(entry);
                count++;
            } else {
                curr_ptr = &entry->next;
            }
        }
    }
    pthread_mutex_unlock(&engine->mutex);
    return count;
}
