/* C Implementation: High-Performance C11 Revocation Engine */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <stdatomic.h>

#define MAX_KIDS 8
#define JTI_LEN 36
#define HASH_BUCKETS 1024

typedef enum {
    REVOKE_OK = 0,
    REVOKE_ERR_EXPIRED = 1,
    REVOKE_ERR_ISSUED_BEFORE_LEAK = 2,
    REVOKE_ERR_JTI_BLACKLISTED = 3,
    REVOKE_ERR_UNKNOWN_KID = 4,
    REVOKE_ERR_INVALID_SIG = 5
} revoke_status_t;

typedef struct jti_node {
    char jti[JTI_LEN + 1];
    struct jti_node *next;
} jti_node_t;

typedef struct {
    char kid[16];
    char public_key_pem[256];
    bool is_active_for_signing;
    uint64_t created_at;
} key_entry_t;

typedef struct {
    _Atomic uint64_t leak_timestamp;
    jti_node_t *buckets[HASH_BUCKETS];
    key_entry_t key_ring[MAX_KIDS];
    size_t key_count;
} revocation_engine_t;

static uint32_t hash_jti(const char *jti) {
    uint32_t hash = 5381;
    int c;
    while ((c = *jti++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_BUCKETS;
}

revocation_engine_t* revocation_engine_create(void) {
    revocation_engine_t *eng = (revocation_engine_t*)calloc(1, sizeof(revocation_engine_t));
    if (!eng) return NULL;
    atomic_init(&eng->leak_timestamp, 0);
    return eng;
}

void revocation_engine_destroy(revocation_engine_t *eng) {
    if (!eng) return;
    for (int i = 0; i < HASH_BUCKETS; i++) {
        jti_node_t *curr = eng->buckets[i];
        while (curr) {
            jti_node_t *tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(eng);
}

void revocation_engine_trigger_leak_emergency(revocation_engine_t *eng, uint64_t leak_time) {
    atomic_store(&eng->leak_timestamp, leak_time);
}

bool revocation_engine_blacklist_jti(revocation_engine_t *eng, const char *jti) {
    uint32_t idx = hash_jti(jti);
    jti_node_t *curr = eng->buckets[idx];
    while (curr) {
        if (strncmp(curr->jti, jti, JTI_LEN) == 0) {
            return true; /* Already blacklisted */
        }
        curr = curr->next;
    }
    jti_node_t *new_node = (jti_node_t*)malloc(sizeof(jti_node_t));
    if (!new_node) return false;
    strncpy(new_node->jti, jti, JTI_LEN);
    new_node->jti[JTI_LEN] = '\0';
    new_node->next = eng->buckets[idx];
    eng->buckets[idx] = new_node;
    return true;
}

revoke_status_t revocation_engine_validate_jwt(
    const revocation_engine_t *eng,
    const char *kid,
    const char *jti,
    uint64_t issued_at,
    uint64_t expires_at,
    uint64_t current_time
) {
    if (current_time >= expires_at) {
        return REVOKE_ERR_EXPIRED;
    }

    uint64_t global_leak = atomic_load(&eng->leak_timestamp);
    if (global_leak > 0 && issued_at <= global_leak) {
        return REVOKE_ERR_ISSUED_BEFORE_LEAK;
    }

    /* Check kid validity in JWKS Key Ring */
    bool kid_found = false;
    for (size_t i = 0; i < eng->key_count; i++) {
        if (strcmp(eng->key_ring[i].kid, kid) == 0) {
            kid_found = true;
            break;
        }
    }
    if (!kid_found) {
        return REVOKE_ERR_UNKNOWN_KID;
    }

    /* Check JTI Blacklist */
    uint32_t idx = hash_jti(jti);
    jti_node_t *curr = eng->buckets[idx];
    while (curr) {
        if (strcmp(curr->jti, jti) == 0) {
            return REVOKE_ERR_JTI_BLACKLISTED;
        }
        curr = curr->next;
    }

    return REVOKE_OK;
}
