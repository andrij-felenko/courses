#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <stdbool.h>

#define HASH_CAPACITY 1024

typedef struct CacheNode {
    char key[64];
    char value[128];
    time_t expiry;
    struct CacheNode* next;
} CacheNode;

typedef struct {
    CacheNode* buckets[HASH_CAPACITY];
    pthread_rwlock_t rwlock;
    int ttl_seconds;
} PosixCache;

static unsigned int hash_key(const char* key) {
    unsigned int hash = 5381;
    int c;
    while ((c = *key++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_CAPACITY;
}

PosixCache* cache_create(int default_ttl_seconds) {
    PosixCache* cache = (PosixCache*)malloc(sizeof(PosixCache));
    if (!cache) return NULL;

    memset(cache->buckets, 0, sizeof(cache->buckets));
    cache->ttl_seconds = default_ttl_seconds;

    if (pthread_rwlock_init(&cache->rwlock, NULL) != 0) {
        free(cache);
        return NULL;
    }
    return cache;
}

void cache_destroy(PosixCache* cache) {
    if (!cache) return;

    pthread_rwlock_wrlock(&cache->rwlock);
    for (int i = 0; i < HASH_CAPACITY; ++i) {
        CacheNode* curr = cache->buckets[i];
        while (curr) {
            CacheNode* temp = curr;
            curr = curr->next;
            free(temp);
        }
    }
    pthread_rwlock_unlock(&cache->rwlock);
    pthread_rwlock_destroy(&cache->rwlock);
    free(cache);
}

bool cache_get(PosixCache* cache, const char* key, char* out_val, size_t out_size) {
    unsigned int idx = hash_key(key);
    time_t now = time(NULL);
    bool found = false;

    pthread_rwlock_rdlock(&cache->rwlock);
    CacheNode* curr = cache->buckets[idx];
    while (curr) {
        if (strcmp(curr->key, key) == 0) {
            if (now <= curr->expiry) {
                strncpy(out_val, curr->value, out_size - 1);
                out_val[out_size - 1] = '\0';
                found = true;
            }
            break;
        }
        curr = curr->next;
    }
    pthread_rwlock_unlock(&cache->rwlock);
    return found;
}

void cache_put(PosixCache* cache, const char* key, const char* value) {
    unsigned int idx = hash_key(key);
    time_t expiry = time(NULL) + cache->ttl_seconds;

    pthread_rwlock_wrlock(&cache->rwlock);
    CacheNode* curr = cache->buckets[idx];
    while (curr) {
        if (strcmp(curr->key, key) == 0) {
            strncpy(curr->value, value, sizeof(curr->value) - 1);
            curr->expiry = expiry;
            pthread_rwlock_unlock(&cache->rwlock);
            return;
        }
        curr = curr->next;
    }

    CacheNode* new_node = (CacheNode*)malloc(sizeof(CacheNode));
    strncpy(new_node->key, key, sizeof(new_node->key) - 1);
    strncpy(new_node->value, value, sizeof(new_node->value) - 1);
    new_node->expiry = expiry;
    new_node->next = cache->buckets[idx];
    cache->buckets[idx] = new_node;

    pthread_rwlock_unlock(&cache->rwlock);
}
:::
