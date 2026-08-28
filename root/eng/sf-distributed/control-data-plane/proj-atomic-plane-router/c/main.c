#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_ROUTES 8
#define MAX_BACKENDS 4
#define MAX_NAME_LEN 32

typedef struct {
    char name[MAX_NAME_LEN];
    uint32_t weight;
    bool is_healthy;
} backend_t;

typedef struct {
    char path_prefix[MAX_NAME_LEN];
    backend_t backends[MAX_BACKENDS];
    size_t backend_count;
} route_rule_t;

typedef struct config_snapshot {
    uint64_t version;
    route_rule_t routes[MAX_ROUTES];
    size_t route_count;
    atomic_uint ref_count;
} config_snapshot_t;

/* Глобальний атомарний покажчик на активну конфігурацію */
static _Atomic(config_snapshot_t*) g_active_config = NULL;
static atomic_bool g_running = true;

config_snapshot_t* snapshot_create(uint64_t version) {
    config_snapshot_t* s = (config_snapshot_t*)malloc(sizeof(config_snapshot_t));
    if (!s) return NULL;
    s->version = version;
    s->route_count = 0;
    atomic_init(&s->ref_count, 1); /* 1 посилання утримує глобальний покажчик */
    return s;
}

void snapshot_add_route(config_snapshot_t* s, const char* prefix, backend_t* backends, size_t count) {
    if (s->route_count >= MAX_ROUTES) return;
    route_rule_t* r = &s->routes[s->route_count++];
    strncpy(r->path_prefix, prefix, MAX_NAME_LEN - 1);
    r->path_prefix[MAX_NAME_LEN - 1] = '\0';
    r->backend_count = (count > MAX_BACKENDS) ? MAX_BACKENDS : count;
    for (size_t i = 0; i < r->backend_count; i++) {
        r->backends[i] = backends[i];
    }
}

static void snapshot_release(config_snapshot_t* s) {
    if (!s) return;
    if (atomic_fetch_sub_explicit(&s->ref_count, 1, memory_order_acq_rel) == 1) {
        /* Останній читач або потік управління звільнив зліпок */
        free(s);
    }
}

/* =========================================================================
   ШВИДКИЙ ШЛЯХ (Data Plane Worker): обробка запитів без м'ютексів
   ========================================================================= */
const char* data_plane_route_request(const char* request_path) {
    /* 1. Атомарно отримуємо поточний зліпок із семантикою acquire */
    config_snapshot_t* snap = atomic_load_explicit(&g_active_config, memory_order_acquire);
    if (!snap) return NULL;

    /* 2. Захоплюємо посилання на зліпок, щоб потік управління не звільнив пам'ять */
    atomic_fetch_add_explicit(&snap->ref_count, 1, memory_order_relaxed);

    const char* selected_backend = "503_SERVICE_UNAVAILABLE";

    /* 3. Пошук відповідного маршруту у незмінній структурі */
    for (size_t i = 0; i < snap->route_count; i++) {
        const route_rule_t* r = &snap->routes[i];
        if (strncmp(request_path, r->path_prefix, strlen(r->path_prefix)) == 0) {
            /* Обираємо перший здоровий бекенд */
            for (size_t j = 0; j < r->backend_count; j++) {
                if (r->backends[j].is_healthy) {
                    selected_backend = r->backends[j].name;
                    break;
                }
            }
            break;
        }
    }

    /* 4. Звільняємо посилання після завершення обробки */
    snapshot_release(snap);
    return selected_backend;
}

void* data_plane_worker(void* arg) {
    int worker_id = *(int*)arg;
    uint64_t processed = 0;

    while (atomic_load_explicit(&g_running, memory_order_relaxed)) {
        const char* target = data_plane_route_request("/api/v1/checkout");
        if (target) processed++;
        usleep(50); /* Імітація надходження наступного мережевого пакета */
    }
    printf("[Data Plane Worker %d] Завершено. Оброблено запитів: %llu\n", worker_id, (unsigned long long)processed);
    return NULL;
}

/* =========================================================================
   КОНТУР УПРАВЛІННЯ (Control Plane Thread): асинхронне оновлення
   ========================================================================= */
void control_plane_publish_update(uint64_t new_version, bool add_canary) {
    /* 1. Створюємо та наповнюємо новий зліпок повністю ізольовано */
    config_snapshot_t* new_snap = snapshot_create(new_version);
    if (!new_snap) return;

    backend_t backends[2] = {
        { .name = "srv-prod-primary:8080", .weight = 100, .is_healthy = true },
        { .name = "srv-prod-canary:8080",  .weight = 10,  .is_healthy = add_canary }
    };
    snapshot_add_route(new_snap, "/api/v1", backends, add_canary ? 2 : 1);

    /* 2. Атомарно замінюємо активний покажчик з бар'єром release */
    config_snapshot_t* old_snap = atomic_exchange_explicit(&g_active_config, new_snap, memory_order_acq_rel);

    printf("[Control Plane] Опубліковано зліпок v%llu (канарка: %s)\n",
           (unsigned long long)new_version, add_canary ? "Увімкнено" : "Вимкнено");

    /* 3. Звільняємо посилання старого зліпка від імені контролера */
    if (old_snap) {
        snapshot_release(old_snap);
    }
}
