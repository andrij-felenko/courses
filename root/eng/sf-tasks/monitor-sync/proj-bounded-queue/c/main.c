#include <pthread.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>
#include <errno.h>

typedef struct {
    void** buffer;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
    bool shutdown;

    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} bounded_queue_t;

bounded_queue_t* bqueue_create(size_t capacity) {
    if (capacity == 0) return NULL;

    bounded_queue_t* q = (bounded_queue_t*)malloc(sizeof(bounded_queue_t));
    if (!q) return NULL;

    q->buffer = (void**)malloc(sizeof(void*) * capacity);
    if (!q->buffer) {
        free(q);
        return NULL;
    }

    q->capacity = capacity;
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->shutdown = false;

    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);

    return q;
}

bool bqueue_push(bounded_queue_t* q, void* item) {
    pthread_mutex_lock(&q->lock);

    while (q->count == q->capacity && !q->shutdown) {
        pthread_cond_wait(&q->not_full, &q->lock);
    }

    if (q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    q->buffer[q->tail] = item;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;

    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

bool bqueue_pop(bounded_queue_t* q, void** item) {
    pthread_mutex_lock(&q->lock);

    while (q->count == 0 && !q->shutdown) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }

    if (q->count == 0 && q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    *item = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;

    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return true;
}

bool bqueue_pop_timeout(bounded_queue_t* q, void** item, long timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    pthread_mutex_lock(&q->lock);

    while (q->count == 0 && !q->shutdown) {
        int rc = pthread_cond_timedwait(&q->not_empty, &q->lock, &ts);
        if (rc == ETIMEDOUT) {
            break;
        }
    }

    if (q->count == 0) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    *item = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;

    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return true;
}

void bqueue_shutdown(bounded_queue_t* q) {
    pthread_mutex_lock(&q->lock);
    q->shutdown = true;
    pthread_cond_broadcast(&q->not_empty);
    pthread_cond_broadcast(&q->not_full);
    pthread_mutex_unlock(&q->lock);
}

void bqueue_destroy(bounded_queue_t* q) {
    if (!q) return;

    bqueue_shutdown(q);

    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);

    free(q->buffer);
    free(q);
}
