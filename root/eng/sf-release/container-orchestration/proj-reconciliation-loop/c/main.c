#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

#define MAX_NAME_LEN 64
#define MAX_PODS 64
#define MAX_QUEUE_SIZE 128
#define INITIAL_BACKOFF_MS 50
#define MAX_BACKOFF_MS 2000

/* Структура бажаного стану розгортання */
typedef struct {
    char name[MAX_NAME_LEN];
    int desired_replicas;
    char image[MAX_NAME_LEN];
    uint64_t resource_version;
    int current_replicas;
    int ready_replicas;
} Deployment;

/* Стан одного екземпляра контейнера */
typedef struct {
    char name[MAX_NAME_LEN];
    char owner[MAX_NAME_LEN];
    char image[MAX_NAME_LEN];
    bool is_ready;
    bool is_terminating;
} Pod;

/* Спільне сховище кластера */
typedef struct {
    pthread_mutex_t lock;
    Deployment deployment;
    Pod pods[MAX_PODS];
    size_t pod_count;
    uint64_t global_version_seq;
} ClusterStore;

/* Елемент черги завдань із контролем затримки повторів */
typedef struct {
    char deployment_name[MAX_NAME_LEN];
    int retry_count;
    struct timespec process_after;
} QueueItem;

typedef struct {
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    QueueItem items[MAX_QUEUE_SIZE];
    size_t count;
    bool shutdown;
} WorkQueue;

/* Допоміжні функції часу */
static struct timespec get_current_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts;
}

static struct timespec add_ms_to_time(struct timespec ts, int ms) {
    ts.tv_nsec += (long)ms * 1000000L;
    if (ts.tv_nsec >= 1000000000L) {
        ts.tv_sec += ts.tv_nsec / 1000000000L;
        ts.tv_nsec %= 1000000000L;
    }
    return ts;
}

static bool is_time_reached(struct timespec current, struct timespec target) {
    if (current.tv_sec > target.tv_sec) return true;
    if (current.tv_sec == target.tv_sec && current.tv_nsec >= target.tv_nsec) return true;
    return false;
}

/* Ініціалізація черги */
void queue_init(WorkQueue *q) {
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    q->count = 0;
    q->shutdown = false;
}

void queue_push(WorkQueue *q, const char *name, int retry_count, int delay_ms) {
    pthread_mutex_lock(&q->lock);
    if (q->count < MAX_QUEUE_SIZE) {
        QueueItem *item = &q->items[q->count++];
        strncpy(item->deployment_name, name, MAX_NAME_LEN - 1);
        item->deployment_name[MAX_NAME_LEN - 1] = '\0';
        item->retry_count = retry_count;
        item->process_after = add_ms_to_time(get_current_time(), delay_ms);
        pthread_cond_signal(&q->not_empty);
    }
    pthread_mutex_unlock(&q->lock);
}

bool queue_pop(WorkQueue *q, QueueItem *out_item) {
    pthread_mutex_lock(&q->lock);
    while (q->count == 0 && !q->shutdown) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }
    if (q->shutdown && q->count == 0) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    /* Знаходимо першу задачу, час обробки якої настав */
    struct timespec now = get_current_time();
    size_t ready_idx = (size_t)-1;
    for (size_t i = 0; i < q->count; ++i) {
        if (is_time_reached(now, q->items[i].process_after)) {
            ready_idx = i;
            break;
        }
    }

    if (ready_idx == (size_t)-1) {
        pthread_mutex_unlock(&q->lock);
        usleep(10000); /* 10 мс пауза, якщо елементи ще в стадії backoff */
        return queue_pop(q, out_item);
    }

    *out_item = q->items[ready_idx];
    for (size_t i = ready_idx; i < q->count - 1; ++i) {
        q->items[i] = q->items[i + 1];
    }
    q->count--;

    pthread_mutex_unlock(&q->lock);
    return true;
}

/* Ядро узгодження (Reconciliation Logic) */
typedef enum { RECONCILE_SUCCESS, RECONCILE_CONFLICT, RECONCILE_ERROR } ReconcileResult;

ReconcileResult reconcile_deployment(ClusterStore *store, const char *dep_name) {
    pthread_mutex_lock(&store->lock);

    /* 1. Фаза спостереження: читання знімка бажаного стану */
    if (strcmp(store->deployment.name, dep_name) != 0) {
        pthread_mutex_unlock(&store->lock);
        return RECONCILE_ERROR; /* Об'єкт не знайдено */
    }

    Deployment dep_snapshot = store->deployment;
    uint64_t expected_version = dep_snapshot.resource_version;

    /* Підрахунок активних здорових подів */
    int active_pods = 0;
    int matching_image_pods = 0;
    for (size_t i = 0; i < store->pod_count; ++i) {
        if (strcmp(store->pods[i].owner, dep_name) == 0 && !store->pods[i].is_terminating) {
            active_pods++;
            if (strcmp(store->pods[i].image, dep_snapshot.image) == 0) {
                matching_image_pods++;
            }
        }
    }

    printf("[Reconciler] '%s' | Desired: %d | Active: %d (Ver: %lu)\n",
           dep_name, dep_snapshot.desired_replicas, active_pods, expected_version);

    /* 2. Фаза аналізу та дій: усунення розбіжності */
    int delta = dep_snapshot.desired_replicas - active_pods;

    if (delta > 0) {
        /* Дефіцит: створюємо нові поди */
        for (int k = 0; k < delta && store->pod_count < MAX_PODS; ++k) {
            Pod *new_pod = &store->pods[store->pod_count++];
            snprintf(new_pod->name, sizeof(new_pod->name), "%s-%lu-%d", dep_name, store->global_version_seq, k);
            strncpy(new_pod->owner, dep_name, sizeof(new_pod->owner) - 1);
            strncpy(new_pod->image, dep_snapshot.image, sizeof(new_pod->image) - 1);
            new_pod->is_ready = true;
            new_pod->is_terminating = false;
            printf("  -> Створено Pod: %s [%s]\n", new_pod->name, new_pod->image);
        }
    } else if (delta < 0) {
        /* Надлишок: видаляємо зайві поди */
        int to_remove = -delta;
        for (size_t i = store->pod_count; i > 0 && to_remove > 0; --i) {
            size_t idx = i - 1;
            if (strcmp(store->pods[idx].owner, dep_name) == 0 && !store->pods[idx].is_terminating) {
                printf("  -> Вилучено надлишковий Pod: %s\n", store->pods[idx].name);
                /* Зсув масиву для видалення */
                for (size_t j = idx; j < store->pod_count - 1; ++j) {
                    store->pods[j] = store->pods[j + 1];
                }
                store->pod_count--;
                to_remove--;
            }
        }
    }

    /* 3. Фіксація статусу з перевіркою CAS (Optimistic Locking) */
    if (store->deployment.resource_version != expected_version) {
        /* Стан змінився паралельно — відхиляємо транзакцію */
        printf("  [!] Конфлікт версій (CAS fail): очікувалась %lu, знайдено %lu\n",
               expected_version, store->deployment.resource_version);
        pthread_mutex_unlock(&store->lock);
        return RECONCILE_CONFLICT;
    }

    /* Оновлюємо статус і збільшуємо лічильник версії */
    store->global_version_seq++;
    store->deployment.resource_version = store->global_version_seq;
    store->deployment.current_replicas = dep_snapshot.desired_replicas;
    store->deployment.ready_replicas = dep_snapshot.desired_replicas;

    printf("  [OK] Статус оновлено. Нова версія: %lu\n", store->deployment.resource_version);
    pthread_mutex_unlock(&store->lock);
    return RECONCILE_SUCCESS;
}

/* Робочий потік контролера */
typedef struct {
    ClusterStore *store;
    WorkQueue *queue;
} ControllerContext;

void *controller_worker(void *arg) {
    ControllerContext *ctx = (ControllerContext *)arg;
    QueueItem item;

    while (queue_pop(ctx->queue, &item)) {
        ReconcileResult res = reconcile_deployment(ctx->store, item.deployment_name);
        if (res == RECONCILE_CONFLICT || res == RECONCILE_ERROR) {
            /* Експоненційний розрахунок затримки (Exponential Backoff) */
            int next_retry = item.retry_count + 1;
            int backoff = INITIAL_BACKOFF_MS * (1 << (next_retry > 5 ? 5 : next_retry));
            if (backoff > MAX_BACKOFF_MS) backoff = MAX_BACKOFF_MS;

            printf("  [Retry] Повторна постановка '%s' у чергу через %d мс (спроба %d)\n",
                   item.deployment_name, backoff, next_retry);
            queue_push(ctx->queue, item.deployment_name, next_retry, backoff);
        }
    }
    return NULL;
}

int main(void) {
    ClusterStore store;
    pthread_mutex_init(&store.lock, NULL);
    store.global_version_seq = 1;
    store.pod_count = 0;

    /* Створення початкового маніфесту */
    strncpy(store.deployment.name, "web-api", sizeof(store.deployment.name) - 1);
    store.deployment.desired_replicas = 3;
    strncpy(store.deployment.image, "nginx:1.24", sizeof(store.deployment.image) - 1);
    store.deployment.resource_version = 1;
    store.deployment.current_replicas = 0;
    store.deployment.ready_replicas = 0;

    WorkQueue queue;
    queue_init(&queue);

    ControllerContext ctx = { .store = &store, .queue = &queue };
    pthread_t worker;
    pthread_create(&worker, NULL, controller_worker, &ctx);

    /* 1. Подія створення: надсилаємо задачу на первинне розгортання */
    printf("\n=== Подія 1: Створення Deployment 'web-api' на 3 репліки ===\n");
    queue_push(&queue, "web-api", 0, 0);
    usleep(100000);

    /* 2. Збій вузла: аварійно знищуємо 2 поди без відома специфікації */
    printf("\n=== Подія 2: Аварійне падіння 2 подів (Simulated Crash) ===\n");
    pthread_mutex_lock(&store.lock);
    store.pod_count -= 2; /* 2 поди загинули */
    pthread_mutex_unlock(&store.lock);

    /* Watch-тригер сповіщає контролер про зміну стану */
    queue_push(&queue, "web-api", 0, 0);
    usleep(100000);

    /* 3. Масштабування вгору: користувач змінив replicas до 5 */
    printf("\n=== Подія 3: Масштабування до 5 реплік ===\n");
    pthread_mutex_lock(&store.lock);
    store.deployment.desired_replicas = 5;
    store.global_version_seq++;
    store.deployment.resource_version = store.global_version_seq;
    pthread_mutex_unlock(&store.lock);

    queue_push(&queue, "web-api", 0, 0);
    usleep(100000);

    /* Зупинка черги та прибирання ресурсів */
    pthread_mutex_lock(&queue.lock);
    queue.shutdown = true;
    pthread_cond_broadcast(&queue.not_empty);
    pthread_mutex_unlock(&queue.lock);

    pthread_join(worker, NULL);
    pthread_mutex_destroy(&store.lock);
    pthread_mutex_destroy(&queue.lock);
    pthread_cond_destroy(&queue.not_empty);

    printf("\n[Тест завершено] Усі фази узгодження виконано успішно.\n");
    return 0;
}
