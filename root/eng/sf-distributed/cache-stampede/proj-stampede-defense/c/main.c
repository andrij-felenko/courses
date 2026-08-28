#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <math.h>
#include <unistd.h>

#define MAX_KEY_LEN 128
#define MAX_ENTRIES 1024

// Запис кешу C-рівня
typedef struct {
    char key[MAX_KEY_LEN];
    char value[256];
    struct timespec expiry;
    double delta_sec;
    int is_valid;
} C_CacheEntry;

// Об'єкт активного рейсу (Single-Flight)
typedef struct {
    char key[MAX_KEY_LEN];
    pthread_cond_t cond;
    pthread_mutex_t mutex;
    int completed;
    char result[256];
    int active;
} C_FlightCall;

typedef struct {
    C_CacheEntry cache[MAX_ENTRIES];
    pthread_mutex_t cache_mutex;
    C_FlightCall flights[MAX_ENTRIES];
    pthread_mutex_t flights_mutex;
    double beta;
} C_StampedeGuard;

void guard_init(C_StampedeGuard* g, double beta) {
    memset(g, 0, sizeof(C_StampedeGuard));
    g->beta = beta;
    pthread_mutex_init(&g->cache_mutex, NULL);
    pthread_mutex_init(&g->flights_mutex, NULL);
}

// Перевірка умови XFetch
int guard_should_recompute(C_StampedeGuard* g, const C_CacheEntry* e) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    double now_sec = now.tv_sec + now.tv_nsec / 1e9;
    double exp_sec = e->expiry.tv_sec + e->expiry.tv_nsec / 1e9;

    if (now_sec >= exp_sec) return 1;
    if (e->delta_sec <= 0.0) return 0;

    double u = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double shift = -e->delta_sec * g->beta * log(u);

    return (now_sec + shift) > exp_sec;
}

// Запит даних із блокуванням і дедуплікацією
void guard_get(C_StampedeGuard* g, const char* key, int ttl_sec,
               void (*fetcher)(const char*, char*), char* out_buf) {
    // 1. Пошук у кеші
    pthread_mutex_lock(&g->cache_mutex);
    for (int i = 0; i < MAX_ENTRIES; ++i) {
        if (g->cache[i].is_valid && strcmp(g->cache[i].key, key) == 0) {
            if (!guard_should_recompute(g, &g->cache[i])) {
                strcpy(out_buf, g->cache[i].value);
                pthread_mutex_unlock(&g->cache_mutex);
                return;
            }
            break;
        }
    }
    pthread_mutex_unlock(&g->cache_mutex);

    // 2. Single-Flight дедуплікація
    pthread_mutex_lock(&g->flights_mutex);
    C_FlightCall* flight = NULL;
    for (int i = 0; i < MAX_ENTRIES; ++i) {
        if (g->flights[i].active && strcmp(g->flights[i].key, key) == 0) {
            flight = &g->flights[i];
            break;
        }
    }

    if (flight != NULL) {
        // Ми — підписник: очікуємо завершення рейсу лідером
        pthread_mutex_unlock(&g->flights_mutex);
        pthread_mutex_lock(&flight->mutex);
        while (!flight->completed) {
            pthread_cond_wait(&flight->cond, &flight->mutex);
        }
        strcpy(out_buf, flight->result);
        pthread_mutex_unlock(&flight->mutex);
        return;
    }

    // Ми — лідер: створюємо новий рейс
    for (int i = 0; i < MAX_ENTRIES; ++i) {
        if (!g->flights[i].active) {
            flight = &g->flights[i];
            flight->active = 1;
            flight->completed = 0;
            strcpy(flight->key, key);
            pthread_mutex_init(&flight->mutex, NULL);
            pthread_cond_init(&flight->cond, NULL);
            break;
        }
    }
    pthread_mutex_unlock(&g->flights_mutex);

    // 3. Виконання важкого обчислення
    struct timespec t_start, t_end;
    clock_gettime(CLOCK_MONOTONIC, &t_start);

    char fetched_val[256];
    fetcher(key, fetched_val);

    clock_gettime(CLOCK_MONOTONIC, &t_end);
    double delta = (t_end.tv_sec - t_start.tv_sec) + (t_end.tv_nsec - t_start.tv_nsec) / 1e9;

    // 4. Оновлення кешу
    pthread_mutex_lock(&g->cache_mutex);
    for (int i = 0; i < MAX_ENTRIES; ++i) {
        if (!g->cache[i].is_valid || strcmp(g->cache[i].key, key) == 0) {
            g->cache[i].is_valid = 1;
            strcpy(g->cache[i].key, key);
            strcpy(g->cache[i].value, fetched_val);
            g->cache[i].delta_sec = delta;
            clock_gettime(CLOCK_MONOTONIC, &g->cache[i].expiry);
            g->cache[i].expiry.tv_sec += ttl_sec;
            break;
        }
    }
    pthread_mutex_unlock(&g->cache_mutex);

    // 5. Оповіщення всіх очікувачів
    pthread_mutex_lock(&flight->mutex);
    strcpy(flight->result, fetched_val);
    flight->completed = 1;
    pthread_cond_broadcast(&flight->cond);
    pthread_mutex_unlock(&flight->mutex);

    // Очищення рейсу
    pthread_mutex_lock(&g->flights_mutex);
    flight->active = 0;
    pthread_mutex_unlock(&g->flights_mutex);

    strcpy(out_buf, fetched_val);
}
