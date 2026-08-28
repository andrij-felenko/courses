#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define HASH_CAPACITY 1024
#define MAX_TAGS_PER_ENTRY 16

typedef enum {
    ENTRY_VALID,
    ENTRY_STALE,
    ENTRY_EVICTED
} EntryState;

typedef struct CacheEntry {
    char url[256];
    char body[1024];
    size_t body_len;
    time_t expires_at;
    EntryState state;
    char tags[MAX_TAGS_PER_ENTRY][64];
    int tag_count;
    struct CacheEntry* next;
} CacheEntry;

typedef struct TagNode {
    char url[256];
    struct TagNode* next;
} TagNode;

typedef struct TagBucket {
    char tag[64];
    TagNode* head;
    struct TagBucket* next;
} TagBucket;

typedef struct FlightGroup {
    char url[256];
    pthread_cond_t cond;
    bool in_progress;
    char response[1024];
    size_t response_len;
    struct FlightGroup* next;
} FlightGroup;

typedef struct {
    CacheEntry* entries[HASH_CAPACITY];
    TagBucket* tag_index[HASH_CAPACITY];
    FlightGroup* flights[HASH_CAPACITY];
    pthread_mutex_t lock;
} EdgeCacheEngine;

static unsigned int hash_str(const char* s) {
    unsigned int h = 5381;
    while (*s) h = ((h << 5) + h) + (unsigned char)(*s++);
    return h % HASH_CAPACITY;
}

void cache_init(EdgeCacheEngine* engine) {
    memset(engine, 0, sizeof(*engine));
    pthread_mutex_init(&engine->lock, NULL);
}

void cache_put(EdgeCacheEngine* engine, const char* url, const char* body, 
               size_t len, int ttl_sec, const char* tags[], int tag_count) {
    pthread_mutex_lock(&engine->lock);
    
    unsigned int idx = hash_str(url);
    CacheEntry* e = engine->entries[idx];
    while (e && strcmp(e->url, url) != 0) e = e->next;
    
    if (!e) {
        e = (CacheEntry*)malloc(sizeof(CacheEntry));
        strncpy(e->url, url, sizeof(e->url) - 1);
        e->next = engine->entries[idx];
        engine->entries[idx] = e;
    }
    
    strncpy(e->body, body, sizeof(e->body) - 1);
    e->body_len = len;
    e->expires_at = time(NULL) + ttl_sec;
    e->state = ENTRY_VALID;
    e->tag_count = (tag_count < MAX_TAGS_PER_ENTRY) ? tag_count : MAX_TAGS_PER_ENTRY;
    
    for (int i = 0; i < e->tag_count; ++i) {
        strncpy(e->tags[i], tags[i], sizeof(e->tags[i]) - 1);
        unsigned int tidx = hash_str(tags[i]);
        TagBucket* tb = engine->tag_index[tidx];
        while (tb && strcmp(tb->tag, tags[i]) != 0) tb = tb->next;
        
        if (!tb) {
            tb = (TagBucket*)malloc(sizeof(TagBucket));
            strncpy(tb->tag, tags[i], sizeof(tb->tag) - 1);
            tb->head = NULL;
            tb->next = engine->tag_index[tidx];
            engine->tag_index[tidx] = tb;
        }
        
        TagNode* tn = tb->head;
        bool exists = false;
        while (tn) {
            if (strcmp(tn->url, url) == 0) { exists = true; break; }
            tn = tn->next;
        }
        if (!exists) {
            TagNode* nn = (TagNode*)malloc(sizeof(TagNode));
            strncpy(nn->url, url, sizeof(nn->url) - 1);
            nn->next = tb->head;
            tb->head = nn;
        }
    }
    
    pthread_mutex_unlock(&engine->lock);
}

int cache_purge_tag(EdgeCacheEngine* engine, const char* tag, bool soft) {
    pthread_mutex_lock(&engine->lock);
    unsigned int tidx = hash_str(tag);
    TagBucket* tb = engine->tag_index[tidx];
    while (tb && strcmp(tb->tag, tag) != 0) tb = tb->next;
    
    if (!tb) {
        pthread_mutex_unlock(&engine->lock);
        return 0;
    }
    
    int purged = 0;
    TagNode* cur = tb->head;
    while (cur) {
        unsigned int uidx = hash_str(cur->url);
        CacheEntry* e = engine->entries[uidx];
        while (e) {
            if (strcmp(e->url, cur->url) == 0) {
                e->state = soft ? ENTRY_STALE : ENTRY_EVICTED;
                purged++;
                break;
            }
            e = e->next;
        }
        cur = cur->next;
    }
    
    pthread_mutex_unlock(&engine->lock);
    return purged;
}

// Диспетчер схлопування (Single-Flight Fetch)
bool cache_get_or_fetch(EdgeCacheEngine* engine, const char* url, char* out_buf, size_t* out_len) {
    pthread_mutex_lock(&engine->lock);
    
    unsigned int uidx = hash_str(url);
    CacheEntry* e = engine->entries[uidx];
    while (e && strcmp(e->url, url) != 0) e = e->next;
    
    // Хіт валідного кешу
    if (e && e->state == ENTRY_VALID && e->expires_at > time(NULL)) {
        strncpy(out_buf, e->body, e->body_len);
        *out_len = e->body_len;
        pthread_mutex_unlock(&engine->lock);
        return true;
    }
    
    // Якщо є stale-копія, повертаємо її клієнту негайно (stale-while-revalidate)
    bool has_stale = (e && (e->state == ENTRY_STALE || e->expires_at <= time(NULL)));
    if (has_stale) {
        strncpy(out_buf, e->body, e->body_len);
        *out_len = e->body_len;
    }
    
    // Перевіряємо, чи вже йде фоновий запит до бекенду
    unsigned int fidx = hash_str(url);
    FlightGroup* fg = engine->flights[fidx];
    while (fg && strcmp(fg->url, url) != 0) fg = fg->next;
    
    if (fg && fg->in_progress) {
        if (has_stale) {
            // Клієнт отримав застарілі дані й не блокується
            pthread_mutex_unlock(&engine->lock);
            return true;
        }
        // Очікуємо завершення єдиного польоту запиту
        while (fg->in_progress) {
            pthread_cond_wait(&fg->cond, &engine->lock);
        }
        strncpy(out_buf, fg->response, fg->response_len);
        *out_len = fg->response_len;
        pthread_mutex_unlock(&engine->lock);
        return true;
    }
    
    // Ми перший потік — реєструємо новий політ
    if (!fg) {
        fg = (FlightGroup*)malloc(sizeof(FlightGroup));
        strncpy(fg->url, url, sizeof(fg->url) - 1);
        pthread_cond_init(&fg->cond, NULL);
        fg->next = engine->flights[fidx];
        engine->flights[fidx] = fg;
    }
    fg->in_progress = true;
    pthread_mutex_unlock(&engine->lock);
    
    // Імітація запиту до Origin (виконується без утримання глобального м'ютекса)
    char origin_data[1024];
    snprintf(origin_data, sizeof(origin_data), "{\"url\":\"%s\",\"price\":199,\"gen_time\":%ld}", url, time(NULL));
    size_t origin_len = strlen(origin_data);
    usleep(50000); // 50 мс затримка мережі
    
    // Оновлюємо кеш та розблоковуємо очікуючі потоки
    const char* default_tags[] = {"products", "catalog"};
    cache_put(engine, url, origin_data, origin_len, 300, default_tags, 2);
    
    pthread_mutex_lock(&engine->lock);
    fg->in_progress = false;
    strncpy(fg->response, origin_data, origin_len);
    fg->response_len = origin_len;
    pthread_cond_broadcast(&fg->cond);
    
    if (!has_stale) {
        strncpy(out_buf, origin_data, origin_len);
        *out_len = origin_len;
    }
    pthread_mutex_unlock(&engine->lock);
    return true;
}
