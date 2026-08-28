#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

#define MAX_ID_LEN 64
#define MAX_STATUS_LEN 32
#define HASH_TABLE_SIZE 1024

typedef uint64_t version_t;

typedef struct {
    char order_id[MAX_ID_LEN];
    char customer_id[MAX_ID_LEN];
    char status[MAX_STATUS_LEN];
    int64_t total_cents;
    version_t version;
} order_view_t;

typedef struct watermark_node {
    char entity_id[MAX_ID_LEN];
    version_t version;
    struct watermark_node* next;
} watermark_node_t;

typedef struct {
    watermark_node_t* buckets[HASH_TABLE_SIZE];
    pthread_mutex_t lock;
    pthread_cond_t cv;
} watermark_registry_t;

static unsigned int hash_str(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_TABLE_SIZE;
}

void watermark_registry_init(watermark_registry_t* reg) {
    memset(reg->buckets, 0, sizeof(reg->buckets));
    pthread_mutex_init(&reg->lock, NULL);
    pthread_cond_init(&reg->cv, NULL);
}

void watermark_registry_update(watermark_registry_t* reg, const char* id, version_t v) {
    unsigned int idx = hash_str(id);
    pthread_mutex_lock(&reg->lock);
    
    watermark_node_t* cur = reg->buckets[idx];
    while (cur) {
        if (strcmp(cur->entity_id, id) == 0) {
            if (v > cur->version) {
                cur->version = v;
                pthread_cond_broadcast(&reg->cv);
            }
            pthread_mutex_unlock(&reg->lock);
            return;
        }
        cur = cur->next;
    }
    
    watermark_node_t* node = (watermark_node_t*)malloc(sizeof(watermark_node_t));
    strncpy(node->entity_id, id, MAX_ID_LEN - 1);
    node->entity_id[MAX_ID_LEN - 1] = '\0';
    node->version = v;
    node->next = reg->buckets[idx];
    reg->buckets[idx] = node;
    
    pthread_cond_broadcast(&reg->cv);
    pthread_mutex_unlock(&reg->lock);
}

version_t watermark_registry_get(watermark_registry_t* reg, const char* id) {
    unsigned int idx = hash_str(id);
    pthread_mutex_lock(&reg->lock);
    watermark_node_t* cur = reg->buckets[idx];
    while (cur) {
        if (strcmp(cur->entity_id, id) == 0) {
            version_t v = cur->version;
            pthread_mutex_unlock(&reg->lock);
            return v;
        }
        cur = cur->next;
    }
    pthread_mutex_unlock(&reg->lock);
    return 0;
}

bool watermark_registry_wait(watermark_registry_t* reg, const char* id, version_t req_v, int timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    unsigned int idx = hash_str(id);
    pthread_mutex_lock(&reg->lock);
    while (true) {
        watermark_node_t* cur = reg->buckets[idx];
        version_t cur_v = 0;
        while (cur) {
            if (strcmp(cur->entity_id, id) == 0) {
                cur_v = cur->version;
                break;
            }
            cur = cur->next;
        }
        if (cur_v >= req_v) {
            pthread_mutex_unlock(&reg->lock);
            return true;
        }
        int rc = pthread_cond_timedwait(&reg->cv, &reg->lock, &ts);
        if (rc == ETIMEDOUT) {
            pthread_mutex_unlock(&reg->lock);
            return false;
        }
    }
}
