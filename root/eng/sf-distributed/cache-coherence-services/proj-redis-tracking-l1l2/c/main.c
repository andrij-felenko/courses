#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>

#define L1_CAPACITY 1024
#define KEY_MAX_LEN 64
#define VAL_MAX_LEN 256

/* Елемент локального L1 кешу в оперативній пам'яті */
typedef struct {
    char key[KEY_MAX_LEN];
    char value[VAL_MAX_LEN];
    uint64_t version;
    uint64_t lease_token;
    time_t expires_at;
    bool is_valid;
} L1Entry;

/* Дворівневий кеш-менеджер */
typedef struct {
    L1Entry table[L1_CAPACITY];
    pthread_rwlock_t lock;
    uint64_t global_lease_counter;
} TwoTierCache;

static unsigned int hash_key(const char *key) {
    unsigned int h = 5381;
    while (*key) {
        h = ((h << 5) + h) + (unsigned char)(*key++);
    }
    return h % L1_CAPACITY;
}

void cache_init(TwoTierCache *c) {
    memset(c->table, 0, sizeof(c->table));
    pthread_rwlock_init(&c->lock, NULL);
    c->global_lease_counter = 1;
}

void cache_destroy(TwoTierCache *c) {
    pthread_rwlock_destroy(&c->lock);
}

/* 1. Швидке читання з L1 кешу */
bool cache_get_l1(TwoTierCache *c, const char *key, char *out_val, size_t out_size, uint64_t *out_ver) {
    unsigned int idx = hash_key(key);
    bool found = false;
    time_t now = time(NULL);

    pthread_rwlock_rdlock(&c->lock);
    if (c->table[idx].is_valid && strcmp(c->table[idx].key, key) == 0) {
        if (c->table[idx].expires_at > now) {
            snprintf(out_val, out_size, "%s", c->table[idx].value);
            if (out_ver) *out_ver = c->table[idx].version;
            found = true;
        }
    }
    pthread_rwlock_unlock(&c->lock);
    return found;
}

/* 2. Обробник асинхронного push-повідомлення інвалідації від Redis/брокера */
void cache_on_invalidation_push(TwoTierCache *c, const char *key, uint64_t min_valid_ver) {
    unsigned int idx = hash_key(key);

    pthread_rwlock_wrlock(&c->lock);
    if (c->table[idx].is_valid && strcmp(c->table[idx].key, key) == 0) {
        if (c->table[idx].version <= min_valid_ver) {
            c->table[idx].is_valid = false;
            c->table[idx].lease_token = 0; /* Анулювання оренди */
        }
    }
    pthread_rwlock_unlock(&c->lock);
}

/* 3. Отримання токена оренди при кеш-промаху */
uint64_t cache_acquire_lease(TwoTierCache *c, const char *key) {
    unsigned int idx = hash_key(key);
    uint64_t token;

    pthread_rwlock_wrlock(&c->lock);
    token = ++c->global_lease_counter;
    snprintf(c->table[idx].key, KEY_MAX_LEN, "%s", key);
    c->table[idx].lease_token = token;
    c->table[idx].is_valid = false;
    pthread_rwlock_unlock(&c->lock);

    return token;
}

/* 4. Запис у кеш із валідацією токена оренди (Захист від Stale-Overwrite) */
bool cache_set_with_lease(TwoTierCache *c, const char *key, const char *val, uint64_t ver, uint64_t token, int ttl_sec) {
    unsigned int idx = hash_key(key);
    bool success = false;

    pthread_rwlock_wrlock(&c->lock);
    /* Запис дозволено тільки якщо токен оренди не був анульований інвалідацією */
    if (strcmp(c->table[idx].key, key) == 0 && c->table[idx].lease_token == token) {
        snprintf(c->table[idx].value, VAL_MAX_LEN, "%s", val);
        c->table[idx].version = ver;
        c->table[idx].expires_at = time(NULL) + ttl_sec;
        c->table[idx].is_valid = true;
        c->table[idx].lease_token = 0; /* Оренду успішно закрито */
        success = true;
    }
    pthread_rwlock_unlock(&c->lock);
    return success;
}
