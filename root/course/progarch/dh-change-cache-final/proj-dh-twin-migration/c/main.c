/* C11: Low-Level Singleflight & Cache Invalidator Interface */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct {
    char home_id[64];
    char device_id[64];
    uint64_t version;
    uint64_t updated_at_ms;
} dh_twin_state_t;

typedef struct dh_cache_entry {
    dh_twin_state_t state;
    uint64_t expires_at_ms;
    struct dh_cache_entry* next;
} dh_cache_entry_t;

typedef struct {
    dh_cache_entry_t* head;
    pthread_mutex_t lock;
} dh_cache_t;

dh_cache_t* dh_cache_create(void) {
    dh_cache_t* c = (dh_cache_t*)malloc(sizeof(dh_cache_t));
    if (!c) return NULL;
    c->head = NULL;
    pthread_mutex_init(&c->lock, NULL);
    return c;
}

void dh_cache_invalidate_if_newer(dh_cache_t* c, const char* home_id, uint64_t version) {
    if (!c || !home_id) return;
    pthread_mutex_lock(&c->lock);
    dh_cache_entry_t** curr = &c->head;
    while (*curr) {
        if (strcmp((*curr)->state.home_id, home_id) == 0) {
            if (version >= (*curr)->state.version) {
                dh_cache_entry_t* temp = *curr;
                *curr = (*curr)->next;
                free(temp);
                pthread_mutex_unlock(&c->lock);
                return;
            }
        }
        curr = &(*curr)->next;
    }
    pthread_mutex_unlock(&c->lock);
}

void dh_cache_destroy(dh_cache_t* c) {
    if (!c) return;
    pthread_mutex_lock(&c->lock);
    dh_cache_entry_t* curr = c->head;
    while (curr) {
        dh_cache_entry_t* next = curr->next;
        free(curr);
        curr = next;
    }
    pthread_mutex_unlock(&c->lock);
    pthread_mutex_destroy(&c->lock);
    free(c);
}
