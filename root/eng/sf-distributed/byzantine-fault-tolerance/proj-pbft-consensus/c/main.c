#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 4
#define MAX_LOG_ENTRIES 64
#define DIGEST_LEN 32

typedef struct {
    uint8_t bytes[DIGEST_LEN];
} digest_t;

typedef enum {
    MSG_PRE_PREPARE = 1,
    MSG_PREPARE     = 2,
    MSG_COMMIT      = 3
} msg_type_t;

typedef struct {
    msg_type_t type;
    uint32_t view;
    uint32_t seq_num;
    digest_t digest;
    uint32_t sender_id;
} pbft_msg_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    digest_t digest;
    bool has_pre_prepare;
    uint32_t prepare_count;
    uint32_t commit_count;
    bool prepares_from[MAX_NODES];
    bool commits_from[MAX_NODES];
    bool is_prepared;
    bool is_committed;
} log_entry_t;

typedef struct {
    uint32_t node_id;
    uint32_t total_nodes;
    uint32_t max_faults;
    uint32_t current_view;
    log_entry_t log[MAX_LOG_ENTRIES];
} pbft_replica_t;

static bool digests_equal(const digest_t* a, const digest_t* b) {
    return memcmp(a->bytes, b->bytes, DIGEST_LEN) == 0;
}

void pbft_init(pbft_replica_t* rep, uint32_t id, uint32_t total_nodes) {
    rep->node_id = id;
    rep->total_nodes = total_nodes;
    rep->max_faults = (total_nodes - 1) / 3;
    rep->current_view = 0;
    memset(rep->log, 0, sizeof(rep->log));
}

bool pbft_handle_pre_prepare(pbft_replica_t* rep, const pbft_msg_t* msg, pbft_msg_t* out_prepare) {
    uint32_t primary_id = rep->current_view % rep->total_nodes;
    if (msg->sender_id != primary_id) {
        printf("[Вузол %u] Відхилено Pre-Prepare: відправник %u не є лідером виду %u\n",
               rep->node_id, msg->sender_id, rep->current_view);
        return false;
    }
    if (msg->view != rep->current_view || msg->seq_num >= MAX_LOG_ENTRIES) {
        return false;
    }

    log_entry_t* entry = &rep->log[msg->seq_num];
    if (entry->has_pre_prepare) {
        if (!digests_equal(&entry->digest, &msg->digest)) {
            printf("[Вузол %u] Детектовано еквівокацію лідера на слоті %u! Запуск View Change.\n",
               rep->node_id, msg->seq_num);
        }
        return false;
    }

    entry->view = msg->view;
    entry->seq_num = msg->seq_num;
    entry->digest = msg->digest;
    entry->has_pre_prepare = true;
    entry->prepare_count = 1;
    entry->prepares_from[rep->node_id] = true;

    out_prepare->type = MSG_PREPARE;
    out_prepare->view = rep->current_view;
    out_prepare->seq_num = msg->seq_num;
    out_prepare->digest = msg->digest;
    out_prepare->sender_id = rep->node_id;
    return true;
}

bool pbft_handle_prepare(pbft_replica_t* rep, const pbft_msg_t* msg, pbft_msg_t* out_commit) {
    if (msg->view != rep->current_view || msg->seq_num >= MAX_LOG_ENTRIES || msg->sender_id >= rep->total_nodes) {
        return false;
    }

    log_entry_t* entry = &rep->log[msg->seq_num];
    if (!entry->has_pre_prepare || !digests_equal(&entry->digest, &msg->digest)) {
        return false;
    }

    if (!entry->prepares_from[msg->sender_id]) {
        entry->prepares_from[msg->sender_id] = true;
        entry->prepare_count++;
    }

    uint32_t quorum_needed = 2 * rep->max_faults;
    if (entry->prepare_count >= quorum_needed && !entry->is_prepared) {
        entry->is_prepared = true;
        entry->commit_count = 1;
        entry->commits_from[rep->node_id] = true;

        out_commit->type = MSG_COMMIT;
        out_commit->view = rep->current_view;
        out_commit->seq_num = msg->seq_num;
        out_commit->digest = msg->digest;
        out_commit->sender_id = rep->node_id;
        return true;
    }
    return false;
}

bool pbft_handle_commit(pbft_replica_t* rep, const pbft_msg_t* msg) {
    if (msg->view != rep->current_view || msg->seq_num >= MAX_LOG_ENTRIES || msg->sender_id >= rep->total_nodes) {
        return false;
    }

    log_entry_t* entry = &rep->log[msg->seq_num];
    if (!entry->is_prepared || !digests_equal(&entry->digest, &msg->digest)) {
        return false;
    }

    if (!entry->commits_from[msg->sender_id]) {
        entry->commits_from[msg->sender_id] = true;
        entry->commit_count++;
    }

    uint32_t commit_quorum = 2 * rep->max_faults + 1;
    if (entry->commit_count >= commit_quorum && !entry->is_committed) {
        entry->is_committed = true;
        printf("[Вузол %u] Слот %u успішно зафіксовано (Committed-Local)! Виконання транзакції.\n",
               rep->node_id, msg->seq_num);
        return true;
    }
    return false;
}
