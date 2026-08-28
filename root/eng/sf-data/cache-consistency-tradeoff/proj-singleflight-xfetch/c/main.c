/* Реалізація Singleflight + XFetch мовою C (POSIX Threads, C11) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>

#define HASH_SIZE 1024
#define MAX_KEY_LEN 128
#define MAX_VAL_LEN 256

/* Отримання поточного часу в секундах з високою точністю */
static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

/* Генерація випадкового числа U in (0, 1] */
static double get_random_uniform(unsigned int *seed) {
    double u = ((double)rand_r(seed) + 1.0) / ((double)RAND_MAX + 1.0);
    return u > 1.0 ? 1.0 : u;
}

/* Запис у кеші з метаданими XFetch та токеном лізи */
typedef struct CacheEntry {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    double expiry_time;    /* Номінальний час смерті (секунди) */
    double compute_time;   /* Час обчислення delta (секунди) */
    uint64_t lease_token;  /* Токен покоління запису */
    struct CacheEntry *next;
} CacheEntry;

/* Стан активного польоту Singleflight */
typedef struct InFlightCall {
    char key[MAX_KEY_LEN];
    char val[MAX_VAL_LEN];
    bool done;
    int waiters;
    pthread_cond_t cond;
    struct InFlightCall *next;
} InFlightCall;

/* Головна структура кешу з Singleflight */
typedef struct ResilientCache {
    CacheEntry *entries[HASH_SIZE];
    InFlightCall *in_flight[HASH_SIZE];
    pthread_mutex_t cache_mutex;
    pthread_mutex_t flight_mutex;
    uint64_t next_lease;
    double beta;           /* Коефіцієнт XFetch (1.0) */
} ResilientCache;

/* Ініціалізація кешу */
void cache_init(ResilientCache *c, double beta) {
    memset(c->entries, 0, sizeof(c->entries));
    memset(c->in_flight, 0, sizeof(c->in_flight));
    pthread_mutex_init(&c->cache_mutex, NULL);
    pthread_mutex_init(&c->flight_mutex, NULL);
    c->next_lease = 1;
    c->beta = beta;
}

/* Простий хеш djb2 для ключів */
static unsigned int hash_key(const char *str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++)) hash = ((hash << 5) + hash) + c;
    return hash % HASH_SIZE;
}

/* Перевірка правила XFetch: повертає true, якщо треба оновити */
static bool xfetch_should_refresh(double expiry, double delta, double beta, unsigned int *seed) {
    double now = get_time_sec();
    double time_left = expiry - now;
    if (time_left <= 0.0) return true; /* TTL уже вичерпано */
    
    double u = get_random_uniform(seed);
    /* Формула: -beta * delta * ln(u) > time_left */
    return (-beta * delta * log(u)) > time_left;
}

/* Збереження значення в кеш із валідацією токена лізи */
bool cache_set(ResilientCache *c, const char *key, const char *val, 
               double ttl, double delta, uint64_t lease_token) {
    unsigned int h = hash_key(key);
    pthread_mutex_lock(&c->cache_mutex);

    CacheEntry *e = c->entries[h];
    while (e && strcmp(e->key, key) != 0) e = e->next;

    /* Якщо запис уже існує і токен застарілий — відхиляємо збереження */
    if (e && e->lease_token != lease_token) {
        pthread_mutex_unlock(&c->cache_mutex);
        return false; /* Гонка: хтось уже інвалідував або оновив ключ */
    }

    if (!e) {
        e = (CacheEntry *)malloc(sizeof(CacheEntry));
        strncpy(e->key, key, MAX_KEY_LEN - 1);
        e->next = c->entries[h];
        c->entries[h] = e;
    }

    strncpy(e->value, val, MAX_VAL_LEN - 1);
    e->expiry_time = get_time_sec() + ttl;
    e->compute_time = delta;
    e->lease_token = ++c->next_lease;

    pthread_mutex_unlock(&c->cache_mutex);
    return true;
}

/* Інвалідація ключа в кеші (скасовує всі активні лізи) */
void cache_invalidate(ResilientCache *c, const char *key) {
    unsigned int h = hash_key(key);
    pthread_mutex_lock(&c->cache_mutex);

    CacheEntry **curr = &c->entries[h];
    while (*curr) {
        CacheEntry *entry = *curr;
        if (strcmp(entry->key, key) == 0) {
            *curr = entry->next;
            free(entry);
            break;
        }
        curr = &entry->next;
    }
    c->next_lease++; /* Зміна глобального покоління */

    pthread_mutex_unlock(&c->cache_mutex);
}

/* Симуляція повільного читання з бази даних (Source of Truth) */
static void db_fetch(const char *key, char *out_val, double *out_delta) {
    double t0 = get_time_sec();
    usleep(50000); /* 50 мілісекунд затримки бази */
    snprintf(out_val, MAX_VAL_LEN, "DataFor(%s)_v%ld", key, (long)time(NULL));
    *out_delta = get_time_sec() - t0;
}

/* Отримання значення з Singleflight + XFetch */
bool cache_get_or_fetch(ResilientCache *c, const char *key, char *out_val, 
                        double ttl, unsigned int *seed) {
    unsigned int h = hash_key(key);

    /* 1. Спроба швидкого читання з кешу */
    pthread_mutex_lock(&c->cache_mutex);
    CacheEntry *e = c->entries[h];
    while (e && strcmp(e->key, key) != 0) e = e->next;

    if (e) {
        bool need_refresh = xfetch_should_refresh(e->expiry_time, e->compute_time, c->beta, seed);
        if (!need_refresh) {
            strncpy(out_val, e->value, MAX_VAL_LEN - 1);
            pthread_mutex_unlock(&c->cache_mutex);
            return true; /* Швидке влучання */
        }
    }
    pthread_mutex_unlock(&c->cache_mutex);

    /* 2. Потрібно обчислення: вхід у Singleflight */
    pthread_mutex_lock(&c->flight_mutex);
    InFlightCall *call = c->in_flight[h];
    while (call && strcmp(call->key, key) != 0) call = call->next;

    if (call) {
        /* Інший потік уже виконує запит: стаємо в чергу очікування */
        call->waiters++;
        while (!call->done) {
            pthread_cond_wait(&call->cond, &c->flight_mutex);
        }
        strncpy(out_val, call->val, MAX_VAL_LEN - 1);
        call->waiters--;
        if (call->waiters == 0) {
            /* Останній очікувач прибирає структуру */
            pthread_cond_destroy(&call->cond);
            free(call);
        }
        pthread_mutex_unlock(&c->flight_mutex);
        return true;
    }

    /* Ми — лідер виклику: реєструємо політ */
    call = (InFlightCall *)malloc(sizeof(InFlightCall));
    strncpy(call->key, key, MAX_KEY_LEN - 1);
    call->done = false;
    call->waiters = 1; /* Самі себе рахуємо */
    pthread_cond_init(&call->cond, NULL);
    call->next = c->in_flight[h];
    c->in_flight[h] = call;
    pthread_mutex_unlock(&c->flight_mutex);

    /* 3. Виконання важкого запиту до джерела правди */
    char db_val[MAX_VAL_LEN];
    double delta = 0.0;
    db_fetch(key, db_val, &delta);

    /* 4. Збереження результату в кеш */
    cache_set(c, key, db_val, ttl, delta, 0);

    /* 5. Сповіщення всіх очікувачів */
    pthread_mutex_lock(&c->flight_mutex);
    strncpy(call->val, db_val, MAX_VAL_LEN - 1);
    call->done = true;

    /* Видаляємо з активного списку in_flight */
    InFlightCall **curr = &c->in_flight[h];
    while (*curr) {
        if (*curr == call) {
            *curr = call->next;
            break;
        }
        curr = &(*curr)->next;
    }

    pthread_cond_broadcast(&call->cond);
    call->waiters--;
    if (call->waiters == 0) {
        pthread_cond_destroy(&call->cond);
        free(call);
    }
    pthread_mutex_unlock(&c->flight_mutex);

    strncpy(out_val, db_val, MAX_VAL_LEN - 1);
    return true;
}
