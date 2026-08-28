#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define NODE_ID_LEN 32
#define SIGNATURE_LEN 64
#define MAX_PAYLOAD_LEN 1024
#define PEER_TABLE_SIZE 256
#define MAX_CLOCK_DRIFT_SEC 5
#define SCORE_INVALID_SIG -100.0f
#define SCORE_EQUIVOCATION -500.0f
#define SCORE_VALID_DELIVERY 1.0f
#define SCORE_GREYLIST_THRESHOLD -50.0f

typedef struct {
    uint8_t origin_id[NODE_ID_LEN];
    uint64_t seq_num;
    uint64_t timestamp_sec;
    uint32_t payload_len;
    uint8_t payload[MAX_PAYLOAD_LEN];
    uint8_t signature[SIGNATURE_LEN];
} GossipEnvelope;

typedef struct {
    uint8_t node_id[NODE_ID_LEN];
    uint64_t last_seq;
    uint8_t last_payload_hash[32];
    float score;
    bool is_banned;
} PeerRecord;

typedef struct {
    PeerRecord peers[PEER_TABLE_SIZE];
    size_t peer_count;
    uint8_t local_id[NODE_ID_LEN];
} SecureGossipEngine;

// Проста імітація криптографічного хешу для ілюстрації логіки валідації
static void compute_payload_hash(const uint8_t *payload, size_t len, uint8_t *out_hash) {
    memset(out_hash, 0, 32);
    for (size_t i = 0; i < len; ++i) {
        out_hash[i % 32] ^= payload[i];
    }
}

// Заглушка перевірки Ed25519 підпису (у продакшені: crypto_sign_verify_detached)
static bool verify_ed25519_signature(const uint8_t *origin_id, const GossipEnvelope *env) {
    if (env->signature[0] == 0xFF && env->signature[1] == 0xFF) {
        return false; // Симуляція підробленого підпису
    }
    return (origin_id != NULL && env != NULL);
}

void engine_init(SecureGossipEngine *engine, const uint8_t *local_id) {
    memset(engine, 0, sizeof(SecureGossipEngine));
    memcpy(engine->local_id, local_id, NODE_ID_LEN);
}

PeerRecord *get_or_create_peer(SecureGossipEngine *engine, const uint8_t *node_id) {
    for (size_t i = 0; i < engine->peer_count; ++i) {
        if (memcmp(engine->peers[i].node_id, node_id, NODE_ID_LEN) == 0) {
            return &engine->peers[i];
        }
    }
    if (engine->peer_count < PEER_TABLE_SIZE) {
        PeerRecord *p = &engine->peers[engine->peer_count++];
        memcpy(p->node_id, node_id, NODE_ID_LEN);
        p->last_seq = 0;
        p->score = 0.0f;
        p->is_banned = false;
        memset(p->last_payload_hash, 0, 32);
        return p;
    }
    return NULL;
}

typedef enum {
    PROCESS_OK = 0,
    ERR_PEER_BANNED,
    ERR_INVALID_LENGTH,
    ERR_CLOCK_DRIFT,
    ERR_BAD_SIGNATURE,
    ERR_REPLAY_STALE,
    ERR_EQUIVOCATION_DETECTED
} ValidationResult;

ValidationResult process_incoming_gossip(SecureGossipEngine *engine,
                                         const uint8_t *relay_peer_id,
                                         const GossipEnvelope *env,
                                         uint64_t current_time_sec) {
    PeerRecord *relay = get_or_create_peer(engine, relay_peer_id);
    if (relay && relay->is_banned) {
        return ERR_PEER_BANNED;
    }

    if (env->payload_len > MAX_PAYLOAD_LEN) {
        if (relay) relay->score += SCORE_INVALID_SIG;
        return ERR_INVALID_LENGTH;
    }

    // 1. Перевірка часового зсуву (Clock Drift)
    int64_t drift = (int64_t)env->timestamp_sec - (int64_t)current_time_sec;
    if (drift > MAX_CLOCK_DRIFT_SEC || drift < -MAX_CLOCK_DRIFT_SEC) {
        return ERR_CLOCK_DRIFT;
    }

    // 2. Криптографічна перевірка підпису джерела
    if (!verify_ed25519_signature(env->origin_id, env)) {
        if (relay) {
            relay->score += SCORE_INVALID_SIG;
            if (relay->score < SCORE_GREYLIST_THRESHOLD) {
                relay->is_banned = true;
            }
        }
        return ERR_BAD_SIGNATURE;
    }

    PeerRecord *origin = get_or_create_peer(engine, env->origin_id);
    if (!origin) {
        return ERR_PEER_BANNED;
    }

    uint8_t current_hash[32];
    compute_payload_hash(env->payload, env->payload_len, current_hash);

    // 3. Перевірка еквівокації (той самий seq, але інший хеш)
    if (env->seq_num == origin->last_seq && origin->last_seq > 0) {
        if (memcmp(origin->last_payload_hash, current_hash, 32) != 0) {
            origin->score += SCORE_EQUIVOCATION;
            origin->is_banned = true;
            if (relay) relay->score += SCORE_INVALID_SIG;
            return ERR_EQUIVOCATION_DETECTED;
        }
        return ERR_REPLAY_STALE;
    }

    // 4. Перевірка на застарілий номер послідовності (Replay)
    if (env->seq_num < origin->last_seq) {
        return ERR_REPLAY_STALE;
    }

    // 5. Оновлення стану та підвищення рейтингу
    origin->last_seq = env->seq_num;
    memcpy(origin->last_payload_hash, current_hash, 32);
    if (relay) {
        relay->score += SCORE_VALID_DELIVERY;
    }

    return PROCESS_OK;
}

int main(void) {
    SecureGossipEngine engine;
    uint8_t my_id[NODE_ID_LEN] = {1};
    uint8_t peer_a[NODE_ID_LEN] = {2};
    uint8_t rogue[NODE_ID_LEN] = {9};

    engine_init(&engine, my_id);

    GossipEnvelope msg1;
    memcpy(msg1.origin_id, peer_a, NODE_ID_LEN);
    msg1.seq_num = 1;
    msg1.timestamp_sec = 1000;
    msg1.payload_len = 12;
    memcpy(msg1.payload, "Status=Alive", 12);
    msg1.signature[0] = 0xAA; // Валідний підпис

    ValidationResult r1 = process_incoming_gossip(&engine, peer_a, &msg1, 1000);
    printf("Message 1 result: %d (Expected 0 - OK)\n", r1);

    // Спроба повтору старого повідомлення (Replay)
    ValidationResult r2 = process_incoming_gossip(&engine, peer_a, &msg1, 1001);
    printf("Replay result: %d (Expected 5 - Stale)\n", r2);

    // Спроба еквівокації від rogue: той самий seq=1, але інший payload
    GossipEnvelope msg_rogue1;
    memcpy(msg_rogue1.origin_id, rogue, NODE_ID_LEN);
    msg_rogue1.seq_num = 10;
    msg_rogue1.timestamp_sec = 1002;
    msg_rogue1.payload_len = 8;
    memcpy(msg_rogue1.payload, "State=V1", 8);
    msg_rogue1.signature[0] = 0xAA;
    process_incoming_gossip(&engine, rogue, &msg_rogue1, 1002);

    GossipEnvelope msg_rogue2;
    memcpy(msg_rogue2.origin_id, rogue, NODE_ID_LEN);
    msg_rogue2.seq_num = 10; // Той самий seq!
    msg_rogue2.timestamp_sec = 1002;
    msg_rogue2.payload_len = 8;
    memcpy(msg_rogue2.payload, "State=V2", 8); // Інший вміст!
    msg_rogue2.signature[0] = 0xAA;

    ValidationResult r3 = process_incoming_gossip(&engine, rogue, &msg_rogue2, 1002);
    printf("Equivocation result: %d (Expected 6 - Equivocation Detected)\n", r3);

    PeerRecord *rogue_rec = get_or_create_peer(&engine, rogue);
    if (rogue_rec) {
        printf("Rogue peer banned status: %s, Score: %.1f\n",
               rogue_rec->is_banned ? "TRUE" : "FALSE", rogue_rec->score);
    }

    return 0;
}
