#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 16
#define MAX_BUFFER 64
#define MAX_PAYLOAD 128

typedef enum {
    ORDER_EQUAL,
    ORDER_BEFORE,
    ORDER_AFTER,
    ORDER_CONCURRENT
} CausalOrder;

typedef struct {
    uint32_t counters[MAX_NODES];
    size_t size;
} VectorClock;

typedef struct {
    size_t sender_id;
    VectorClock clock;
    char payload[MAX_PAYLOAD];
    bool occupied;
} BufferedMessage;

typedef struct {
    size_t node_id;
    VectorClock clock;
    BufferedMessage buffer[MAX_BUFFER];
} Node;

void vc_init(VectorClock *vc, size_t size) {
    vc->size = size;
    memset(vc->counters, 0, sizeof(uint32_t) * MAX_NODES);
}

void vc_tick(VectorClock *vc, size_t node_id) {
    if (node_id < vc->size) {
        vc->counters[node_id]++;
    }
}

void vc_merge(VectorClock *dest, const VectorClock *src) {
    size_t limit = dest->size < src->size ? dest->size : src->size;
    for (size_t i = 0; i < limit; i++) {
        if (src->counters[i] > dest->counters[i]) {
            dest->counters[i] = src->counters[i];
        }
    }
}

CausalOrder vc_compare(const VectorClock *a, const VectorClock *b) {
    bool has_less = false;
    bool has_greater = false;
    size_t limit = a->size < b->size ? a->size : b->size;

    for (size_t i = 0; i < limit; i++) {
        if (a->counters[i] < b->counters[i]) {
            has_less = true;
        } else if (a->counters[i] > b->counters[i]) {
            has_greater = true;
        }
    }

    if (!has_less && !has_greater) return ORDER_EQUAL;
    if (has_less && !has_greater)  return ORDER_BEFORE;
    if (!has_less && has_greater)  return ORDER_AFTER;
    return ORDER_CONCURRENT;
}

void node_init(Node *node, size_t node_id, size_t cluster_size) {
    node->node_id = node_id;
    vc_init(&node->clock, cluster_size);
    for (size_t i = 0; i < MAX_BUFFER; i++) {
        node->buffer[i].occupied = false;
    }
}

bool can_deliver(const Node *node, size_t sender_id, const VectorClock *msg_clock) {
    if (msg_clock->counters[sender_id] != node->clock.counters[sender_id] + 1) {
        return false;
    }
    for (size_t i = 0; i < node->clock.size; i++) {
        if (i != sender_id && msg_clock->counters[i] > node->clock.counters[i]) {
            return false;
        }
    }
    return true;
}

void node_deliver(Node *node, size_t sender_id, const VectorClock *msg_clock, const char *payload) {
    node->clock.counters[sender_id] = msg_clock->counters[sender_id];
    printf("[Вузол %zu] Доставлено від Вузла %zu: \"%s\" (Вектор: [", node->node_id, sender_id, payload);
    for (size_t i = 0; i < node->clock.size; i++) {
        printf("%u%s", node->clock.counters[i], i + 1 < node->clock.size ? ", " : "");
    }
    printf("])\n");

    bool progress = true;
    while (progress) {
        progress = false;
        for (size_t i = 0; i < MAX_BUFFER; i++) {
            if (node->buffer[i].occupied && can_deliver(node, node->buffer[i].sender_id, &node->buffer[i].clock)) {
                node->buffer[i].occupied = false;
                node->clock.counters[node->buffer[i].sender_id] = node->buffer[i].clock.counters[node->buffer[i].sender_id];
                printf("[Вузол %zu] Розблоковано з буфера від Вузла %zu: \"%s\"\n",
                       node->node_id, node->buffer[i].sender_id, node->buffer[i].payload);
                progress = true;
                break;
            }
        }
    }
}

void node_receive_message(Node *node, size_t sender_id, const VectorClock *msg_clock, const char *payload) {
    if (can_deliver(sender_id, msg_clock)) {
        node_deliver(node, sender_id, msg_clock, payload);
    } else {
        for (size_t i = 0; i < MAX_BUFFER; i++) {
            if (!node->buffer[i].occupied) {
                node->buffer[i].occupied = true;
                node->buffer[i].sender_id = sender_id;
                node->buffer[i].clock = *msg_clock;
                strncpy(node->buffer[i].payload, payload, MAX_PAYLOAD - 1);
                node->buffer[i].payload[MAX_PAYLOAD - 1] = '\0';
                printf("[Вузол %zu] Затримано в буфері від Вузла %zu: \"%s\"\n", node->node_id, sender_id, payload);
                return;
            }
        }
        fprintf(stderr, "[Вузол %zu] Помилка: буфер переповнено!\n", node->node_id);
    }
}
