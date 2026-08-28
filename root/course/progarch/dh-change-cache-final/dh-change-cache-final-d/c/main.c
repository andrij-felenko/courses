/* C11: Singleflight Mutex Map for Embedded Gateway */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct {
    char home_id[64];
    uint64_t version_seq;
    uint64_t expires_at_ms;
} dh_c_cache_item_t;

typedef struct {
    dh_c_cache_item_t items[1024];
    size_t count;
    pthread_mutex_t lock;
} dh_c_cache_t;

void dh_c_cache_init(dh_c_cache_t* cache) {
    cache->count = 0;
    pthread_mutex_init(&cache->lock, NULL);
}

void dh_c_cache_invalidate(dh_c_cache_t* cache, const char* home_id, uint64_t version) {
    pthread_mutex_lock(&cache->lock);
    for (size_t i = 0; i < cache->count; ++i) {
        if (strcmp(cache->items[i].home_id, home_id) == 0) {
            if (version >= cache->items[i].version_seq) {
                cache->items[i] = cache->items[cache->count - 1];
                cache->count--;
            }
            break;
        }
    }
    pthread_mutex_unlock(&cache->lock);
}
