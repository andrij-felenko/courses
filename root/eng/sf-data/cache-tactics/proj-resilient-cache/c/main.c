#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>

#define MAX_KEY_LEN 128
#define MAX_VAL_LEN 512
#define HASH_SIZE 1024

/* Отримання поточного монотонного часу в секундах */
static double get_monotonic_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

/* Генерація випадкового розкиду (TTL Jitter) у межах ±jitter_ratio */
static double apply_jitter(double base_ttl, double jitter_ratio) {
    double r = ((double)rand() / (double)RAND_MAX) * 2.0 - 1.0; /* [-1.0, 1.0] */
    return base_ttl * (1.0 + r * jitter_ratio);
}

typedef struct CacheEntry {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    bool is_negative;       /* Чи є це кешуванням відсутності (null) */
    double soft_expiry;     /* Час початку фонового оновлення */
    double hard_expiry;     /* Час повного виселення з пам'яті */
    bool is_refreshing;     /* Прапорець активного фонового оновлення */
    struct CacheEntry* next;
} CacheEntry;

typedef struct ResilientCache {
    CacheEntry* buckets[HASH_SIZE];
    pthread_mutex_t locks[HASH_SIZE];
    double default_ttl;
    double soft_ratio;      /* Частка від TTL для Soft Expiry (наприклад 0.75) */
    double negative_ttl;    /* Час життя для порожніх відповідей */
    double jitter_ratio;    /* Коефіцієнт розкиду (наприклад 0.15) */
} ResilientCache;

/* Проста геш-функція djb2 для ключів */
static unsigned int hash_key(const char* str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++)) hash = ((hash << 5) + hash) + c;
    return (unsigned int)(hash % HASH_SIZE);
}

ResilientCache* cache_create(double default_ttl, double negative_ttl, double jitter_ratio) {
    ResilientCache* c = (ResilientCache*)malloc(sizeof(ResilientCache));
    if (!c) return NULL;
    c->default_ttl = default_ttl;
    c->soft_ratio = 0.75;
    c->negative_ttl = negative_ttl;
    c->jitter_ratio = jitter_ratio;
    for (int i = 0; i < HASH_SIZE; ++i) {
        c->buckets[i] = NULL;
        pthread_mutex_init(&c->locks[i], NULL);
    }
    return c;
}

/* Збереження запису з розрахунком Soft/Hard TTL та джиттером */
void cache_set(ResilientCache* c, const char* key, const char* val, bool is_neg) {
    unsigned int h = hash_key(key);
    double now = get_monotonic_time();
    double base = is_neg ? c->negative_ttl : c->default_ttl;
    double actual_ttl = apply_jitter(base, c->jitter_ratio);

    pthread_mutex_lock(&c->locks[h]);
    CacheEntry* curr = c->buckets[h];
    while (curr) {
        if (strcmp(curr->key, key) == 0) {
            if (val) {
                strncpy(curr->value, val, MAX_VAL_LEN - 1);
                curr->value[MAX_VAL_LEN - 1] = '\0';
            } else {
                curr->value[0] = '\0';
            }
            curr->is_negative = is_neg;
            curr->soft_expiry = now + (actual_ttl * c->soft_ratio);
            curr->hard_expiry = now + actual_ttl;
            curr->is_refreshing = false;
            pthread_mutex_unlock(&c->locks[h]);
            return;
        }
        curr = curr->next;
    }

    /* Створення нового елемента */
    CacheEntry* entry = (CacheEntry*)malloc(sizeof(CacheEntry));
    if (!entry) {
        pthread_mutex_unlock(&c->locks[h]);
        return;
    }
    strncpy(entry->key, key, MAX_KEY_LEN - 1);
    entry->key[MAX_KEY_LEN - 1] = '\0';
    if (val) {
        strncpy(entry->value, val, MAX_VAL_LEN - 1);
        entry->value[MAX_VAL_LEN - 1] = '\0';
    } else {
        entry->value[0] = '\0';
    }
    entry->is_negative = is_neg;
    entry->soft_expiry = now + (actual_ttl * c->soft_ratio);
    entry->hard_expiry = now + actual_ttl;
    entry->is_refreshing = false;
    entry->next = c->buckets[h];
    c->buckets[h] = entry;
    pthread_mutex_unlock(&c->locks[h]);
}

/* Контекст для фонового потоку оновлення */
typedef struct AsyncArgs {
    ResilientCache* cache;
    char key[MAX_KEY_LEN];
    char* (*loader_fn)(const char* k, bool* not_found);
} AsyncArgs;

static void* async_refresh_worker(void* arg) {
    AsyncArgs* args = (AsyncArgs*)arg;
    bool not_found = false;
    char* fresh_val = args->loader_fn(args->key, &not_found);

    cache_set(args->cache, args->key, fresh_val, not_found);

    if (fresh_val) free(fresh_val);
    free(args);
    return NULL;
}

/* Отримання значення з кешу з автоматичною фоновою ревалідацією */
bool cache_get_or_load(ResilientCache* c, const char* key,
                       char* out_val, size_t out_len,
                       char* (*loader_fn)(const char* k, bool* not_found)) {
    unsigned int h = hash_key(key);
    double now = get_monotonic_time();

    pthread_mutex_lock(&c->locks[h]);
    CacheEntry* curr = c->buckets[h];
    while (curr) {
        if (strcmp(curr->key, key) == 0) {
            /* Перевірка Hard TTL (чи не виселено значення) */
            if (now < curr->hard_expiry) {
                if (curr->is_negative) {
                    /* Знайдено закешовану порожнечу (Negative Hit) */
                    pthread_mutex_unlock(&c->locks[h]);
                    return false; /* 404 Not Found */
                }
                strncpy(out_val, curr->value, out_len - 1);
                out_val[out_len - 1] = '\0';

                /* Перевірка Soft TTL: якщо застаріло і ще не оновлюється */
                if (now >= curr->soft_expiry && !curr->is_refreshing) {
                    curr->is_refreshing = true; /* Захоплюємо рейс */
                    pthread_mutex_unlock(&c->locks[h]);

                    AsyncArgs* args = (AsyncArgs*)malloc(sizeof(AsyncArgs));
                    if (args) {
                        args->cache = c;
                        strncpy(args->key, key, MAX_KEY_LEN - 1);
                        args->loader_fn = loader_fn;
                        pthread_t t;
                        pthread_create(&t, NULL, async_refresh_worker, args);
                        pthread_detach(t);
                    }
                    return true; /* Віддаємо клієнту Stale значення миттєво */
                }

                pthread_mutex_unlock(&c->locks[h]);
                return true; /* Свіже влучання (Fresh Hit) */
            }
            break; /* Вичерпано Hard TTL */
        }
        curr = curr->next;
    }
    pthread_mutex_unlock(&c->locks[h]);

    /* Синхронний промах (Hard Miss) — блокуюче звернення до джерела */
    bool not_found = false;
    char* fetched = loader_fn(key, &not_found);
    cache_set(c, key, fetched, not_found);

    if (not_found || !fetched) {
        if (fetched) free(fetched);
        return false;
    }

    strncpy(out_val, fetched, out_len - 1);
    out_val[out_len - 1] = '\0';
    free(fetched);
    return true;
}
