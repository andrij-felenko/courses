#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_KEYS_PER_TAG 64
#define MAX_TAGS_PER_KEY 16
#define HASH_BUCKETS 1024

/* Запис у кеші */
typedef struct CacheEntry {
    char key[128];
    char value[512];
    time_t expires_at;
    uint64_t lease_token;
    char tags[MAX_TAGS_PER_KEY][64];
    int tag_count;
    struct CacheEntry* next;
} CacheEntry;

/* Вузол інвертованого індексу тегів */
typedef struct TagNode {
    char tag[64];
    char keys[MAX_KEYS_PER_TAG][128];
    int key_count;
    struct TagNode* next;
} TagNode;

/* Лічильник покоління простору імен */
typedef struct NamespaceGen {
    char ns[64];
    uint64_t generation;
    struct NamespaceGen* next;
} NamespaceGen;

/* Головний стан двигуна інвалідації */
typedef struct {
    CacheEntry* cache_table[HASH_BUCKETS];
    TagNode* tag_index[HASH_BUCKETS];
    NamespaceGen* ns_table[HASH_BUCKETS];
    uint64_t next_lease_id;
} InvalidationEngine;

static unsigned int hash_str(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_BUCKETS;
}

InvalidationEngine* engine_create(void) {
    InvalidationEngine* eng = (InvalidationEngine*)calloc(1, sizeof(InvalidationEngine));
    eng->next_lease_id = 1000;
    return eng;
}

/* Прив'язка ключа до тегу в інвертованому індексі */
static void add_key_to_tag(InvalidationEngine* eng, const char* tag, const char* key) {
    unsigned int b = hash_str(tag);
    TagNode* cur = eng->tag_index[b];
    while (cur) {
        if (strcmp(cur->tag, tag) == 0) {
            for (int i = 0; i < cur->key_count; ++i) {
                if (strcmp(cur->keys[i], key) == 0) return;
            }
            if (cur->key_count < MAX_KEYS_PER_TAG) {
                strncpy(cur->keys[cur->key_count++], key, 127);
            }
            return;
        }
        cur = cur->next;
    }
    TagNode* node = (TagNode*)malloc(sizeof(TagNode));
    strncpy(node->tag, tag, 63);
    node->tag[63] = '\0';
    strncpy(node->keys[0], key, 127);
    node->keys[0][127] = '\0';
    node->key_count = 1;
    node->next = eng->tag_index[b];
    eng->tag_index[b] = node;
}

/* Запис значення з набором тегів */
void engine_set(InvalidationEngine* eng, const char* key, const char* val,
                int ttl_seconds, const char* tags[], int num_tags) {
    unsigned int b = hash_str(key);
    CacheEntry* cur = eng->cache_table[b];
    while (cur) {
        if (strcmp(cur->key, key) == 0) break;
        cur = cur->next;
    }
    if (!cur) {
        cur = (CacheEntry*)malloc(sizeof(CacheEntry));
        strncpy(cur->key, key, 127);
        cur->key[127] = '\0';
        cur->next = eng->cache_table[b];
        eng->cache_table[b] = cur;
    }
    strncpy(cur->value, val, 511);
    cur->value[511] = '\0';
    cur->expires_at = time(NULL) + ttl_seconds;
    cur->lease_token = ++eng->next_lease_id;
    cur->tag_count = 0;

    for (int i = 0; i < num_tags && i < MAX_TAGS_PER_KEY; ++i) {
        strncpy(cur->tags[cur->tag_count++], tags[i], 63);
        add_key_to_tag(eng, tags[i], key);
    }
}

/* Пряме видалення одного ключа */
bool engine_del(InvalidationEngine* eng, const char* key) {
    unsigned int b = hash_str(key);
    CacheEntry** pp = &eng->cache_table[b];
    while (*pp) {
        if (strcmp((*pp)->key, key) == 0) {
            CacheEntry* victim = *pp;
            *pp = victim->next;
            free(victim);
            return true;
        }
        pp = &(*pp)->next;
    }
    return false;
}

/* Очищення всіх ключів за заданим тегом */
int engine_purge_tag(InvalidationEngine* eng, const char* tag) {
    unsigned int b = hash_str(tag);
    TagNode** pp = &eng->tag_index[b];
    while (*pp) {
        if (strcmp((*pp)->tag, tag) == 0) {
            TagNode* node = *pp;
            int purged = 0;
            for (int i = 0; i < node->key_count; ++i) {
                if (engine_del(eng, node->keys[i])) {
                    purged++;
                }
            }
            *pp = node->next;
            free(node);
            return purged;
        }
        pp = &(*pp)->next;
    }
    return 0;
}

/* Отримання актуальної епохи простору імен */
uint64_t engine_get_generation(InvalidationEngine* eng, const char* ns) {
    unsigned int b = hash_str(ns);
    NamespaceGen* cur = eng->ns_table[b];
    while (cur) {
        if (strcmp(cur->ns, ns) == 0) return cur->generation;
        cur = cur->next;
    }
    NamespaceGen* node = (NamespaceGen*)malloc(sizeof(NamespaceGen));
    strncpy(node->ns, ns, 63);
    node->ns[63] = '\0';
    node->generation = 1;
    node->next = eng->ns_table[b];
    eng->ns_table[b] = node;
    return 1;
}

/* Інкремент епохи (миттєва інвалідація простору імен за O(1)) */
uint64_t engine_bump_generation(InvalidationEngine* eng, const char* ns) {
    unsigned int b = hash_str(ns);
    NamespaceGen* cur = eng->ns_table[b];
    while (cur) {
        if (strcmp(cur->ns, ns) == 0) {
            return ++cur->generation;
        }
        cur = cur->next;
    }
    NamespaceGen* node = (NamespaceGen*)malloc(sizeof(NamespaceGen));
    strncpy(node->ns, ns, 63);
    node->ns[63] = '\0';
    node->generation = 2;
    node->next = eng->ns_table[b];
    eng->ns_table[b] = node;
    return 2;
}

void engine_free(InvalidationEngine* eng) {
    for (int i = 0; i < HASH_BUCKETS; ++i) {
        CacheEntry* ce = eng->cache_table[i];
        while (ce) { CacheEntry* n = ce->next; free(ce); ce = n; }
        TagNode* tn = eng->tag_index[i];
        while (tn) { TagNode* n = tn->next; free(tn); tn = n; }
        NamespaceGen* ng = eng->ns_table[i];
        while (ng) { NamespaceGen* n = ng->next; free(ng); ng = n; }
    }
    free(eng);
}
