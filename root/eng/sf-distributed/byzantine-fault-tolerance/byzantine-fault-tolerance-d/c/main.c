#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_REPLICAS 4
#define SHA256_LEN 32

typedef struct {
    uint8_t hash[SHA256_LEN];
} digest_256_t;

typedef enum {
    PBFT_PRE_PREPARE = 1,
    PBFT_PREPARE     = 2,
    PBFT_COMMIT      = 3
} pbft_phase_t;

typedef struct {
    pbft_phase_t phase;
    uint32_t view;
    uint32_t seq_num;
    digest_256_t digest;
    uint32_t sender_id;
} pbft_packet_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    digest_256_t digest;
    bool has_pre_prepare;
    bool prepared;
    bool committed;
    uint32_t prepare_votes;
    uint32_t commit_votes;
    bool prepares_mask[MAX_REPLICAS];
    bool commits_mask[MAX_REPLICAS];
} slot_state_t;

typedef struct {
    uint32_t id;
    uint32_t total_nodes;
    uint32_t f_faults;
    uint32_t current_view;
    slot_state_t slots[128];
} bft_replica_state_t;

static bool digests_match(const digest_256_t* a, const digest_256_t* b) {
    return memcmp(a->hash, b->hash, SHA256_LEN) == 0;
}

void bft_node_init(bft_replica_state_t* node, uint32_t id, uint32_t total_nodes) {
    node->id = id;
    node->total_nodes = total_nodes;
    node->f_faults = (total_nodes - 1) / 3;
    node->current_view = 0;
    memset(node->slots, 0, sizeof(node->slots));
}

bool bft_process_pre_prepare(bft_replica_state_t* node, const pbft_packet_t* pkt, pbft_packet_t* out_prepare) {
    uint32_t expected_primary = node->current_view % node->total_nodes;
    if (pkt->sender_id != expected_primary || pkt->view != node->current_view) {
        return false;
    }

    slot_state_t* slot = &node->slots[pkt->seq_num];
    if (slot->has_pre_prepare) {
        if (!digests_match(&slot->digest, &pkt->digest)) {
            printf("[Вузол %u] УВАГА: Виявлено дворушництво лідера на слоті %u! Ініціація View Change.\n",
                   node->id, pkt->seq_num);
        }
        return false;
    }

    slot->view = pkt->view;
    slot->seq_num = pkt->seq_num;
    slot->digest = pkt->digest;
    slot->has_pre_prepare = true;
    slot->prepare_votes = 1;
    slot->prepares_mask[node->id] = true;

    out_prepare->phase = PBFT_PREPARE;
    out_prepare->view = node->current_view;
    out_prepare->seq_num = pkt->seq_num;
    out_prepare->digest = pkt->digest;
    out_prepare->sender_id = node->id;
    return true;
}

bool bft_process_prepare(bft_replica_state_t* node, const pbft_packet_t* pkt, pbft_packet_t* out_commit) {
    if (pkt->view != node->current_view || pkt->sender_id >= node->total_nodes) {
        return false;
    }

    slot_state_t* slot = &node->slots[pkt->seq_num];
    if (!slot->has_pre_prepare || !digests_match(&slot->digest, &pkt->digest)) {
        return false;
    }

    if (!slot->prepares_mask[pkt->sender_id]) {
        slot->prepares_mask[pkt->sender_id] = true;
        slot->prepare_votes++;
    }

    uint32_t required_prepares = 2 * node->f_faults;
    if (slot->prepare_votes >= required_prepares && !slot->prepared) {
        slot->prepared = true;
        slot->commit_votes = 1;
        slot->commits_mask[node->id] = true;

        out_commit->phase = PBFT_COMMIT;
        out_commit->view = node->current_view;
        out_commit->seq_num = pkt->seq_num;
        out_commit->digest = pkt->digest;
        out_commit->sender_id = node->id;
        return true;
    }
    return false;
}

bool bft_process_commit(bft_replica_state_t* node, const pbft_packet_t* pkt) {
    if (pkt->view != node->current_view || pkt->sender_id >= node->total_nodes) {
        return false;
    }

    slot_state_t* slot = &node->slots[pkt->seq_num];
    if (!slot->prepared || !digests_match(&slot->digest, &pkt->digest)) {
        return false;
    }

    if (!slot->commits_mask[pkt->sender_id]) {
        slot->commits_mask[pkt->sender_id] = true;
        slot->commit_votes++;
    }

    uint32_t commit_quorum = 2 * node->f_faults + 1;
    if (slot->commit_votes >= commit_quorum && !slot->committed) {
        slot->committed = true;
        printf("[Вузол %u] Слот %u: Успішно зафіксовано (Committed-Local). Виконання транзакції!\n",
               node->id, pkt->seq_num);
        return true;
    }
    return false;
}
