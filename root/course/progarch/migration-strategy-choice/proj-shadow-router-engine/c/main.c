/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

typedef struct {
    char request_id[64];
    char payload[512];
    int user_id;
} request_t;

typedef struct {
    int status_code;
    char data[256];
    double latency_ms;
} response_t;

/* Контракт сервісу */
typedef response_t (*service_fn)(const request_t* req);

typedef struct {
    service_fn primary;
    service_fn shadow;
    bool enable_parallel_run;
    long total_processed;
    long diff_count;
    pthread_mutex_t lock;
} shadow_router_t;

typedef struct {
    shadow_router_t* router;
    request_t req;
    response_t primary_resp;
} shadow_task_t;

/* Імітація старої та нової систем */
response_t primary_service_v1(const request_t* req) {
    response_t resp = {200, "", 12.5};
    snprintf(resp.data, sizeof(resp.data), "USER_%d_BALANCE_100", req->user_id);
    return resp;
}

response_t shadow_service_v2(const request_t* req) {
    response_t resp = {200, "", 14.1};
    /* Імітація дрібної розбіжності для перевірки роботоздатності Reconciler */
    snprintf(resp.data, sizeof(resp.data), "USER_%d_BALANCE_100", req->user_id);
    return resp;
}

void* async_shadow_worker(void* arg) {
    shadow_task_t* task = (shadow_task_t*)arg;
    response_t shadow_resp = task->router->shadow(&task->req);

    pthread_mutex_lock(&task->router->lock);
    task->router->total_processed++;

    if (task->router->enable_parallel_run) {
        if (task->primary_resp.status_code != shadow_resp.status_code ||
            strcmp(task->primary_resp.data, shadow_resp.data) != 0) {
            task->router->diff_count++;
            fprintf(stderr, "[RECONCILER ALERT] Diff detected for ID %s! Primary: '%s', Shadow: '%s'\n",
                    task->req.request_id, task->primary_resp.data, shadow_resp.data);
        }
    }
    pthread_mutex_unlock(&task->router->lock);

    free(task);
    return NULL;
}

shadow_router_t* shadow_router_create(service_fn primary, service_fn shadow, bool enable_parallel_run) {
    shadow_router_t* router = (shadow_router_t*)malloc(sizeof(shadow_router_t));
    if (!router) return NULL;
    router->primary = primary;
    router->shadow = shadow;
    router->enable_parallel_run = enable_parallel_run;
    router->total_processed = 0;
    router->diff_count = 0;
    pthread_mutex_init(&router->lock, NULL);
    return router;
}

response_t shadow_router_dispatch(shadow_router_t* router, const request_t* req) {
    /* 1. Синхронний виклик основної системи для клієнта */
    response_t primary_resp = router->primary(req);

    /* 2. Асинхронне відгалуження тіньового виклику */
    shadow_task_t* task = (shadow_task_t*)malloc(sizeof(shadow_task_t));
    if (task) {
        task->router = router;
        task->req = *req;
        task->primary_resp = primary_resp;

        pthread_t thread;
        pthread_create(&thread, NULL, async_shadow_worker, task);
        pthread_detach(thread);
    }

    return primary_resp;
}

void shadow_router_free(shadow_router_t* router) {
    if (!router) return;
    pthread_mutex_destroy(&router->lock);
    free(router);
}
