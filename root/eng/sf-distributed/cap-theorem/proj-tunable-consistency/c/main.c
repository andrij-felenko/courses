#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_KEY 32
#define MAX_VAL 64
#define MAX_ITEMS 128
#define MAX_NODES 5

typedef enum {
    CL_ONE = 1,
    CL_QUORUM = 2,
    CL_ALL = 3
} ConsistencyLevel;

typedef struct {
    char key[MAX_KEY];
    char value[MAX_VAL];
    uint64_t version;
    bool active;
} Record;

typedef struct {
    int id;
    Record store[MAX_ITEMS];
    int count;
} ClusterNode;

typedef struct {
    int node_count;
    int rtt_ms;
    bool partition_active;
    uint64_t global_version;
    ClusterNode nodes[MAX_NODES];
} DistributedCluster;

void node_init(ClusterNode* node, int id) {
    node->id = id;
    node->count = 0;
    memset(node->store, 0, sizeof(node->store));
}

void node_write(ClusterNode* node, const char* key, const char* val, uint64_t ver) {
    for (int i = 0; i < node->count; ++i) {
        if (strcmp(node->store[i].key, key) == 0) {
            strncpy(node->store[i].value, val, MAX_VAL - 1);
            node->store[i].version = ver;
            return;
        }
    }
    if (node->count < MAX_ITEMS) {
        strncpy(node->store[node->count].key, key, MAX_KEY - 1);
        strncpy(node->store[node->count].value, val, MAX_VAL - 1);
        node->store[node->count].version = ver;
        node->store[node->count].active = true;
        node->count++;
    }
}

bool node_read(const ClusterNode* node, const char* key, Record* out) {
    for (int i = 0; i < node->count; ++i) {
        if (node->store[i].active && strcmp(node->store[i].key, key) == 0) {
            *out = node->store[i];
            return true;
        }
    }
    return false;
}

void cluster_init(DistributedCluster* c, int node_count, int rtt_ms) {
    c->node_count = node_count;
    c->rtt_ms = rtt_ms;
    c->partition_active = false;
    c->global_version = 0;
    for (int i = 0; i < node_count; ++i) {
        node_init(&c->nodes[i], i);
    }
}

bool is_partitioned(int from, int to) {
    // Вузол 2 ізольований від 0 та 1
    if ((from == 2 && to != 2) || (from != 2 && to == 2)) return true;
    return false;
}

bool cluster_write(DistributedCluster* c, int coord, const char* key,
                   const char* val, ConsistencyLevel cl, int* out_lat_ms) {
    uint64_t ver = ++c->global_version;
    int required = (int)cl;
    int acks = 0;

    node_write(&c->nodes[coord], key, val, ver);
    acks++;

    for (int i = 0; i < c->node_count; ++i) {
        if (i == coord) continue;
        if (c->partition_active && is_partitioned(coord, i)) continue;
        node_write(&c->nodes[i], key, val, ver);
        acks++;
    }

    *out_lat_ms = (required == 1) ? 0 : c->rtt_ms;
    return acks >= required;
}

bool cluster_read(DistributedCluster* c, int coord, const char* key,
                  ConsistencyLevel cl, char* out_val, int* out_lat_ms) {
    int required = (int)cl;
    Record responses[MAX_NODES];
    int resp_count = 0;

    Record r;
    if (node_read(&c->nodes[coord], key, &r)) {
        responses[resp_count++] = r;
    }

    for (int i = 0; i < c->node_count; ++i) {
        if (i == coord) continue;
        if (c->partition_active && is_partitioned(coord, i)) continue;
        if (node_read(&c->nodes[i], key, &r)) {
            responses[resp_count++] = r;
        }
    }

    *out_lat_ms = (required == 1) ? 0 : c->rtt_ms;

    if (resp_count < required) return false;

    Record newest = responses[0];
    for (int i = 1; i < resp_count; ++i) {
        if (responses[i].version > newest.version) {
            newest = responses[i];
        }
    }
    strncpy(out_val, newest.value, MAX_VAL - 1);
    return true;
}
