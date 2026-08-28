#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

#define MAX_INSTANCES 16
#define MAX_STR_LEN 64

/* Дескриптор екземпляра мікросервісу */
typedef struct {
    char id[MAX_STR_LEN];
    char host[MAX_STR_LEN];
    int port;
    int active_conns;
    bool is_healthy;
} ServiceInstance;

/* Потокобезпечний локальний кеш топології */
typedef struct {
    ServiceInstance instances[MAX_INSTANCES];
    size_t count;
    uint64_t revision;
    pthread_rwlock_t lock;
} ServiceCache;

/* Реєстр сервісів (імітація сервера) */
typedef struct {
    ServiceInstance remote_db[MAX_INSTANCES];
    size_t remote_count;
    uint64_t current_revision;
    bool is_online;
    pthread_mutex_t reg_mutex;
} MockRegistry;

static MockRegistry g_registry;

/* Ініціалізація локального кешу */
void cache_init(ServiceCache *cache) {
    cache->count = 0;
    cache->revision = 0;
    pthread_rwlock_init(&cache->lock, NULL);
}

void cache_destroy(ServiceCache *cache) {
    pthread_rwlock_destroy(&cache->lock);
}

/* Балансування навантаження: Power of Two Random Choices (P2C) */
bool cache_select_p2c(ServiceCache *cache, ServiceInstance *selected) {
    pthread_rwlock_rdlock(&cache->lock);

    if (cache->count == 0) {
        pthread_rwlock_unlock(&cache->lock);
        return false;
    }

    if (cache->count == 1) {
        *selected = cache->instances[0];
        pthread_rwlock_unlock(&cache->lock);
        return true;
    }

    /* Обираємо два випадкові різні індекси */
    size_t idx1 = rand() % cache->count;
    size_t idx2 = rand() % cache->count;
    while (idx2 == idx1 && cache->count > 1) {
        idx2 = rand() % cache->count;
    }

    ServiceInstance *inst1 = &cache->instances[idx1];
    ServiceInstance *inst2 = &cache->instances[idx2];

    /* Вибираємо екземпляр з меншою кількістю активних підключень */
    if (inst1->active_conns <= inst2->active_conns) {
        *selected = *inst1;
    } else {
        *selected = *inst2;
    }

    pthread_rwlock_unlock(&cache->lock);
    return true;
}

/* Оновлення локального кешу зі списку від реєстру */
void cache_update(ServiceCache *cache, const ServiceInstance *new_list, size_t new_count, uint64_t rev) {
    pthread_rwlock_wrlock(&cache->lock);

    cache->count = new_count < MAX_INSTANCES ? new_count : MAX_INSTANCES;
    for (size_t i = 0; i < cache->count; ++i) {
        cache->instances[i] = new_list[i];
    }
    cache->revision = rev;

    pthread_rwlock_unlock(&cache->lock);
}

/* Фоновий потік синхронізації з реєстром (Long Polling / Refresh) */
typedef struct {
    ServiceCache *cache;
    bool *running;
} WorkerArgs;

void* sync_worker(void *arg) {
    WorkerArgs *args = (WorkerArgs*)arg;
    ServiceInstance local_fetch[MAX_INSTANCES];
    size_t fetch_count = 0;
    uint64_t fetched_rev = 0;

    while (*args->running) {
        bool fetch_success = false;

        /* Імітація виклику GET /v1/health/service */
        pthread_mutex_lock(&g_registry.reg_mutex);
        if (g_registry.is_online) {
            fetch_count = g_registry.remote_count;
            fetched_rev = g_registry.current_revision;
            for (size_t i = 0; i < fetch_count; ++i) {
                local_fetch[i] = g_registry.remote_db[i];
            }
            fetch_success = true;
        }
        pthread_mutex_unlock(&g_registry.reg_mutex);

        if (fetch_success) {
            cache_update(args->cache, local_fetch, fetch_count, fetched_rev);
            printf("[Sync-Worker] Кеш успішно оновлено (ревізія %lu, інстансів: %zu)\n",
                   fetched_rev, fetch_count);
        } else {
            /* Падіння реєстру: НЕ скидаємо кеш, працюємо на збережених даних */
            printf("[Sync-Worker] УВАГА: Реєстр недоступний! Робота на закешованій топології (Stale Cache)\n");
        }

        sleep(1);
    }
    return NULL;
}

int main(void) {
    srand((unsigned int)time(NULL));

    /* Ініціалізація імітації реєстру */
    pthread_mutex_init(&g_registry.reg_mutex, NULL);
    g_registry.is_online = true;
    g_registry.current_revision = 1;
    g_registry.remote_count = 3;

    snprintf(g_registry.remote_db[0].id, MAX_STR_LEN, "payment-01");
    snprintf(g_registry.remote_db[0].host, MAX_STR_LEN, "10.0.1.10");
    g_registry.remote_db[0].port = 8080;
    g_registry.remote_db[0].active_conns = 12;
    g_registry.remote_db[0].is_healthy = true;

    snprintf(g_registry.remote_db[1].id, MAX_STR_LEN, "payment-02");
    snprintf(g_registry.remote_db[1].host, MAX_STR_LEN, "10.0.1.11");
    g_registry.remote_db[1].port = 8080;
    g_registry.remote_db[1].active_conns = 3;  /* Менш завантажений */
    g_registry.remote_db[1].is_healthy = true;

    snprintf(g_registry.remote_db[2].id, MAX_STR_LEN, "payment-03");
    snprintf(g_registry.remote_db[2].host, MAX_STR_LEN, "10.0.1.12");
    g_registry.remote_db[2].port = 8080;
    g_registry.remote_db[2].active_conns = 25;
    g_registry.remote_db[2].is_healthy = true;

    ServiceCache cache;
    cache_init(&cache);

    bool running = true;
    WorkerArgs args = { .cache = &cache, .running = &running };
    pthread_t thread;
    pthread_create(&thread, NULL, sync_worker, &args);

    /* Чекаємо першої синхронізації */
    sleep(2);

    /* Виконуємо серію запитів через балансувальник P2C */
    printf("\n--- Маршрутизація запитів через P2C ---\n");
    for (int i = 0; i < 5; ++i) {
        ServiceInstance target;
        if (cache_select_p2c(&cache, &target)) {
            printf("Запит #%d спрямовано на: %s (%s:%d) [активних з'єднань: %d]\n",
                   i + 1, target.id, target.host, target.port, target.active_conns);
        }
    }

    /* Імітуємо аварію реєстру */
    printf("\n--- Імітація аварії центрального реєстру ---\n");
    pthread_mutex_lock(&g_registry.reg_mutex);
    g_registry.is_online = false;
    pthread_mutex_unlock(&g_registry.reg_mutex);

    sleep(2);

    /* Перевіряємо роботу на Stale Cache */
    printf("\n--- Маршрутизація під час збою реєстру (Stale Routing) ---\n");
    for (int i = 0; i < 3; ++i) {
        ServiceInstance target;
        if (cache_select_p2c(&cache, &target)) {
            printf("Stale-запит #%d успішно надіслано на: %s (%s:%d)\n",
                   i + 1, target.id, target.host, target.port);
        }
    }

    running = false;
    pthread_join(thread, NULL);
    cache_destroy(&cache);
    pthread_mutex_destroy(&g_registry.reg_mutex);

    return 0;
}
