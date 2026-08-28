#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAX_KEY_LEN   64
#define MAX_VAL_LEN   256
#define TABLE_SIZE    1024

typedef enum {
    CACHE_HIT,
    CACHE_MISS_LEASE_GRANTED,
    CACHE_MISS_LEASE_BUSY,
    SET_SUCCESS,
    SET_STALE_TOKEN_REJECTED
} cache_status_t;

typedef struct cache_entry {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    bool is_valid;
    uint64_t generation;
    uint64_t active_lease_token;
    time_t lease_expiry;
    struct cache_entry *next;
} cache_entry_t;

typedef struct {
    cache_entry_t *buckets[TABLE_SIZE];
    pthread_mutex_t lock;
    uint64_t global_token_counter;
} lease_cache_t;

static unsigned int hash_key(const char *key) {
    unsigned int hash = 5381;
    while (*key) {
        hash = ((hash << 5) + hash) + (unsigned char)(*key++);
    }
    return hash % TABLE_SIZE;
}

void lease_cache_init(lease_cache_t *cache) {
    memset(cache->buckets, 0, sizeof(cache->buckets));
    pthread_mutex_init(&cache->lock, NULL);
    cache->global_token_counter = 1000;
}

static cache_entry_t* find_or_create_entry(lease_cache_t *cache, const char *key) {
    unsigned int idx = hash_key(key);
    cache_entry_t *entry = cache->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) return entry;
        entry = entry->next;
    }
    entry = (cache_entry_t*)malloc(sizeof(cache_entry_t));
    strncpy(entry->key, key, MAX_KEY_LEN - 1);
    entry->key[MAX_KEY_LEN - 1] = '\0';
    entry->is_valid = false;
    entry->generation = 1;
    entry->active_lease_token = 0;
    entry->lease_expiry = 0;
    entry->next = cache->buckets[idx];
    cache->buckets[idx] = entry;
    return entry;
}

cache_status_t lease_cache_get(lease_cache_t *cache, const char *key, 
                               char *out_val, uint64_t *out_token) {
    pthread_mutex_lock(&cache->lock);
    cache_entry_t *entry = find_or_create_entry(cache, key);
    time_t now = time(NULL);

    if (entry->is_valid) {
        strncpy(out_val, entry->value, MAX_VAL_LEN - 1);
        out_val[MAX_VAL_LEN - 1] = '\0';
        pthread_mutex_unlock(&cache->lock);
        return CACHE_HIT;
    }

    if (entry->active_lease_token != 0 && now < entry->lease_expiry) {
        pthread_mutex_unlock(&cache->lock);
        return CACHE_MISS_LEASE_BUSY;
    }

    entry->active_lease_token = ++cache->global_token_counter;
    entry->lease_expiry = now + 5;
    *out_token = entry->active_lease_token;
    pthread_mutex_unlock(&cache->lock);
    return CACHE_MISS_LEASE_GRANTED;
}

cache_status_t lease_cache_set(lease_cache_t *cache, const char *key, 
                               const char *val, uint64_t token) {
    pthread_mutex_lock(&cache->lock);
    cache_entry_t *entry = find_or_create_entry(cache, key);

    if (entry->active_lease_token != token) {
        pthread_mutex_unlock(&cache->lock);
        return SET_STALE_TOKEN_REJECTED;
    }

    strncpy(entry->value, val, MAX_VAL_LEN - 1);
    entry->value[MAX_VAL_LEN - 1] = '\0';
    entry->is_valid = true;
    entry->active_lease_token = 0;
    entry->generation++;
    pthread_mutex_unlock(&cache->lock);
    return SET_SUCCESS;
}

void lease_cache_invalidate(lease_cache_t *cache, const char *key) {
    pthread_mutex_lock(&cache->lock);
    cache_entry_t *entry = find_or_create_entry(cache, key);
    entry->is_valid = false;
    entry->generation++;
    entry->active_lease_token = 0;
    pthread_mutex_unlock(&cache->lock);
}

void lease_cache_destroy(lease_cache_t *cache) {
    pthread_mutex_lock(&cache->lock);
    for (int i = 0; i < TABLE_SIZE; ++i) {
        cache_entry_t *entry = cache->buckets[i];
        while (entry) {
            cache_entry_t *tmp = entry->next;
            free(entry);
            entry = tmp;
        }
        cache->buckets[i] = NULL;
    }
    pthread_mutex_unlock(&cache->lock);
    pthread_mutex_destroy(&cache->lock);
}
