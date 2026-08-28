#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_PEERS 5
#define MAX_LOG 1024

typedef enum {
    ROLE_FOLLOWER = 0,
    ROLE_CANDIDATE,
    ROLE_LEADER
} raft_role_t;

typedef struct {
    uint64_t term;
    uint64_t index;
    int32_t  data;
} log_entry_t;

typedef struct {
    uint64_t term;
    uint32_t candidate_id;
    uint64_t last_log_index;
    uint64_t last_log_term;
} request_vote_args_t;

typedef struct {
    uint64_t term;
    bool     vote_granted;
} request_vote_reply_t;

typedef struct {
    uint64_t term;
    uint32_t leader_id;
    uint64_t prev_log_index;
    uint64_t prev_log_term;
    uint64_t leader_commit;
    uint32_t entries_count;
    log_entry_t entries[16];
} append_entries_args_t;

typedef struct {
    uint64_t term;
    bool     success;
    uint64_t match_index;
    uint64_t conflict_term;
    uint64_t conflict_first_index;
} append_entries_reply_t;

typedef struct {
    uint32_t id;
    uint32_t cluster_size;
    raft_role_t role;

    /* Персистентний стан */
    uint64_t current_term;
    int32_t  voted_for; /* -1, якщо не голосував у поточному термі */
    log_entry_t log[MAX_LOG];
    uint64_t log_size;

    /* Леткий стан на всіх серверах */
    uint64_t commit_index;
    uint64_t last_applied;

    /* Леткий стан лідера */
    uint64_t next_index[MAX_PEERS];
    uint64_t match_index[MAX_PEERS];

    /* Виборча статистика кандидата */
    uint32_t votes_received;
} raft_node_t;

void raft_node_init(raft_node_t *node, uint32_t id, uint32_t cluster_size) {
    node->id = id;
    node->cluster_size = cluster_size;
    node->role = ROLE_FOLLOWER;
    node->current_term = 0;
    node->voted_for = -1;
    node->log_size = 0;
    node->commit_index = 0;
    node->last_applied = 0;
    node->votes_received = 0;

    for (uint32_t i = 0; i < MAX_PEERS; i++) {
        node->next_index[i] = 1;
        node->match_index[i] = 0;
    }
}

static uint64_t get_last_log_term(const raft_node_t *node) {
    if (node->log_size == 0) return 0;
    return node->log[node->log_size - 1].term;
}

static uint64_t get_last_log_index(const raft_node_t *node) {
    return node->log_size;
}

/* Перехід фоловера у стан кандидата та старт виборів */
void raft_start_election(raft_node_t *node) {
    node->role = ROLE_CANDIDATE;
    node->current_term++;
    node->voted_for = (int32_t)node->id;
    node->votes_received = 1; /* Голосує за самого себе */

    printf("[Вузол %u] Став Кандидатом, новий Терм %llu, розсилка RequestVote\n",
           node->id, (unsigned long long)node->current_term);
}

/* Обробка вхідного запиту RequestVote */
void raft_handle_request_vote(raft_node_t *node,
                              const request_vote_args_t *args,
                              request_vote_reply_t *reply) {
    /* 1. Якщо терм запиту більший за наш — оновлюємося й переходимо у фоловери */
    if (args->term > node->current_term) {
        node->current_term = args->term;
        node->role = ROLE_FOLLOWER;
        node->voted_for = -1;
    }

    reply->term = node->current_term;
    reply->vote_granted = false;

    /* Застарілі вибори відкидаються негайно */
    if (args->term < node->current_term) {
        return;
    }

    /* 2. Перевірка: чи не віддали ми вже голос іншому кандидату в цьому термі */
    bool can_vote = (node->voted_for == -1 || node->voted_for == (int32_t)args->candidate_id);
    if (!can_vote) {
        return;
    }

    /* 3. Перевірка актуальності логу (Election Restriction) */
    uint64_t my_last_term = get_last_log_term(node);
    uint64_t my_last_idx  = get_last_log_index(node);

    bool log_is_up_to_date = (args->last_log_term > my_last_term) ||
                             (args->last_log_term == my_last_term &&
                              args->last_log_index >= my_last_idx);

    if (log_is_up_to_date) {
        node->voted_for = (int32_t)args->candidate_id;
        reply->vote_granted = true;
        printf("[Вузол %u] Віддав голос за кандидата %u у термі %llu\n",
               node->id, args->candidate_id, (unsigned long long)node->current_term);
    }
}

/* Обробка вхідного виклику AppendEntries */
void raft_handle_append_entries(raft_node_t *node,
                                const append_entries_args_t *args,
                                append_entries_reply_t *reply) {
    /* Якщо терм вищий за локальний — підкоряємося новому лідеру */
    if (args->term > node->current_term) {
        node->current_term = args->term;
        node->role = ROLE_FOLLOWER;
        node->voted_for = -1;
    }

    reply->term = node->current_term;
    reply->success = false;
    reply->match_index = node->log_size;
    reply->conflict_term = 0;
    reply->conflict_first_index = 0;

    /* 1. Відхиляємо старі терми */
    if (args->term < node->current_term) {
        return;
    }

    /* Визнаємо легітимного лідера поточного терму */
    if (node->role == ROLE_CANDIDATE) {
        node->role = ROLE_FOLLOWER;
    }

    /* 2. Перевірка інваріанта відповідності (Log Matching) */
    if (args->prev_log_index > 0) {
        if (args->prev_log_index > node->log_size) {
            /* Лог надто короткий: повертаємо довжину для швидкого відкочування */
            reply->conflict_first_index = node->log_size + 1;
            return;
        }
        if (node->log[args->prev_log_index - 1].term != args->prev_log_term) {
            /* Конфлікт терму: знаходимо перший індекс цього конфліктного терму */
            uint64_t c_term = node->log[args->prev_log_index - 1].term;
            reply->conflict_term = c_term;
            uint64_t first_idx = args->prev_log_index;
            while (first_idx > 1 && node->log[first_idx - 2].term == c_term) {
                first_idx--;
            }
            reply->conflict_first_index = first_idx;

            /* Обрізаємо конфліктну гілку */
            node->log_size = args->prev_log_index - 1;
            return;
        }
    }

    /* 3. Дописування нових записів та вирішення колізій */
    for (uint32_t i = 0; i < args->entries_count; i++) {
        uint64_t insert_idx = args->prev_log_index + 1 + i;
        if (insert_idx <= node->log_size) {
            if (node->log[insert_idx - 1].term != args->entries[i].term) {
                node->log_size = insert_idx - 1;
                node->log[node->log_size++] = args->entries[i];
            }
        } else {
            node->log[node->log_size++] = args->entries[i];
        }
    }

    /* 4. Оновлення commitIndex за вказівкою лідера */
    if (args->leader_commit > node->commit_index) {
        node->commit_index = (args->leader_commit < node->log_size) ?
                              args->leader_commit : node->log_size;
    }

    reply->success = true;
    reply->match_index = node->log_size;
}

/* Просування коміт-індексу на лідері за правилом §5.4.2 */
void raft_leader_advance_commit(raft_node_t *node) {
    if (node->role != ROLE_LEADER) return;

    for (uint64_t n = node->log_size; n > node->commit_index; n--) {
        /* Фіксуємо лише записи власного поточного терму! */
        if (node->log[n - 1].term != node->current_term) {
            continue;
        }

        uint32_t match_count = 1; /* Власний лог лідера */
        for (uint32_t peer = 0; peer < node->cluster_size; peer++) {
            if (peer != node->id && node->match_index[peer] >= n) {
                match_count++;
            }
        }

        if (match_count > node->cluster_size / 2) {
            node->commit_index = n;
            printf("[Лідер %u] Просунув commitIndex до %llu у термі %llu\n",
                   node->id, (unsigned long long)node->commit_index,
                   (unsigned long long)node->current_term);
            break;
        }
    }
}
