#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <stdbool.h>
#include <unistd.h>
#include <time.h>

#define MAX_BATCH_SIZE 8
#define FLUSH_TIMEOUT_MS 20

typedef struct {
    int item_id;
    int price_cents;
    int status_code; // 200 = OK, 404 = Not Found
} ItemResult;

typedef struct {
    int item_id;
    ItemResult result;
    bool completed;
    pthread_cond_t done_cond;
    pthread_mutex_t done_mutex;
} PendingRequest;

typedef struct {
    PendingRequest* queue[MAX_BATCH_SIZE];
    size_t count;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    bool running;
    pthread_t worker;
} RequestBatcher;

/* Імітація віддаленого фасаду: один мережевий рейс обробляє масив ID */
static void remote_facade_get_prices(const int* ids, size_t count, ItemResult* out_results) {
    /* Імітація затримки мережі (RTT = 15 мс) */
    struct timespec ts = {0, 15 * 1000000};
    nanosleep(&ts, NULL);

    for (size_t i = 0; i < count; ++i) {
        out_results[i].item_id = ids[i];
        if (ids[i] <= 0) {
            out_results[i].status_code = 404;
            out_results[i].price_cents = 0;
        } else {
            out_results[i].status_code = 200;
            out_results[i].price_cents = ids[i] * 100 + 99; // Умовна ціна
        }
    }
}

static void* batcher_worker(void* arg) {
    RequestBatcher* batcher = (RequestBatcher*)arg;

    while (true) {
        PendingRequest* local_batch[MAX_BATCH_SIZE];
        size_t batch_size = 0;

        pthread_mutex_lock(&batcher->mutex);
        while (batcher->running && batcher->count == 0) {
            pthread_cond_wait(&batcher->cond, &batcher->mutex);
        }

        if (!batcher->running && batcher->count == 0) {
            pthread_mutex_unlock(&batcher->mutex);
            break;
        }

        /* Очікуємо наповнення або таймауту */
        struct timespec deadline;
        clock_gettime(CLOCK_REALTIME, &deadline);
        deadline.tv_nsec += FLUSH_TIMEOUT_MS * 1000000;
        if (deadline.tv_nsec >= 1000000000) {
            deadline.tv_sec += 1;
            deadline.tv_nsec -= 1000000000;
        }

        while (batcher->count < MAX_BATCH_SIZE) {
            int res = pthread_cond_timedwait(&batcher->cond, &batcher->mutex, &deadline);
            if (res != 0) {
                break; // Сплив таймаут скидання
            }
        }

        /* Забираємо накопичені запити */
        batch_size = batcher->count;
        for (size_t i = 0; i < batch_size; ++i) {
            local_batch[i] = batcher->queue[i];
        }
        batcher->count = 0;
        pthread_mutex_unlock(&batcher->mutex);

        if (batch_size == 0) {
            continue;
        }

        /* Формуємо масив ID для віддаленого фасаду */
        int ids[MAX_BATCH_SIZE];
        ItemResult results[MAX_BATCH_SIZE];
        for (size_t i = 0; i < batch_size; ++i) {
            ids[i] = local_batch[i]->item_id;
        }

        /* Виконуємо 1 грубозернистий мережевий виклик */
        remote_facade_get_prices(ids, batch_size, results);

        /* Демультиплексуємо відповіді та сповіщаємо потоки */
        for (size_t i = 0; i < batch_size; ++i) {
            PendingRequest* req = local_batch[i];
            pthread_mutex_lock(&req->done_mutex);
            req->result = results[i];
            req->completed = true;
            pthread_cond_signal(&req->done_cond);
            pthread_mutex_unlock(&req->done_mutex);
        }
    }
    return NULL;
}

void batcher_init(RequestBatcher* batcher) {
    batcher->count = 0;
    batcher->running = true;
    pthread_mutex_init(&batcher->mutex, NULL);
    pthread_cond_init(&batcher->cond, NULL);
    pthread_create(&batcher->worker, NULL, batcher_worker, batcher);
}

void batcher_destroy(RequestBatcher* batcher) {
    pthread_mutex_lock(&batcher->mutex);
    batcher->running = false;
    pthread_cond_broadcast(&batcher->cond);
    pthread_mutex_unlock(&batcher->mutex);

    pthread_join(batcher->worker, NULL);
    pthread_mutex_destroy(&batcher->mutex);
    pthread_cond_destroy(&batcher->cond);
}

/* Дрібнозернистий клієнтський метод: блокує лише свій потік до отримання результату */
ItemResult batcher_get_price(RequestBatcher* batcher, int item_id) {
    PendingRequest req;
    req.item_id = item_id;
    req.completed = false;
    pthread_mutex_init(&req.done_mutex, NULL);
    pthread_cond_init(&req.done_cond, NULL);

    pthread_mutex_lock(&batcher->mutex);
    while (batcher->count >= MAX_BATCH_SIZE) {
        /* Якщо буфер переповнений, чекаємо або форсуємо скидання */
        pthread_cond_signal(&batcher->cond);
        pthread_mutex_unlock(&batcher->mutex);
        usleep(1000);
        pthread_mutex_lock(&batcher->mutex);
    }
    batcher->queue[batcher->count++] = &req;
    pthread_cond_signal(&batcher->cond);
    pthread_mutex_unlock(&batcher->mutex);

    /* Очікуємо готовності свого результату */
    pthread_mutex_lock(&req.done_mutex);
    while (!req.completed) {
        pthread_cond_wait(&req.done_cond, &req.done_mutex);
    }
    pthread_mutex_unlock(&req.done_mutex);

    ItemResult res = req.result;
    pthread_mutex_destroy(&req.done_mutex);
    pthread_cond_destroy(&req.done_cond);
    return res;
}
