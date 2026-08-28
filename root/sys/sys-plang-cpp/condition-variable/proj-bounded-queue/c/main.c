#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct {
    void** buffer;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
    bool stopped;
    pthread_mutex_t mutex;
    pthread_cond_t cv_not_empty;
    pthread_cond_t cv_not_full;
} bounded_queue_t;

bounded_queue_t* queue_create(size_t capacity) {
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
    q->stopped = false;

    pthread_mutex_init(&q->mutex, NULL);
    pthread_cond_init(&q->cv_not_empty, NULL);
    pthread_cond_init(&q->cv_not_full, NULL);

    return q;
}

bool queue_push(bounded_queue_t* q, void* data) {
    pthread_mutex_lock(&q->mutex);

    while (q->count == q->capacity && !q->stopped) {
        pthread_cond_wait(&q->cv_not_full, &q->mutex);
    }

    if (q->stopped) {
        pthread_mutex_unlock(&q->mutex);
        return false;
    }

    q->buffer[q->tail] = data;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;

    pthread_cond_signal(&q->cv_not_empty);
    pthread_mutex_unlock(&q->mutex);
    return true;
}

void* queue_pop(bounded_queue_t* q) {
    pthread_mutex_lock(&q->mutex);

    while (q->count == 0 && !q->stopped) {
        pthread_cond_wait(&q->cv_not_empty, &q->mutex);
    }

    if (q->count == 0 && q->stopped) {
        pthread_mutex_unlock(&q->mutex);
        return NULL;
    }

    void* data = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;

    pthread_cond_signal(&q->cv_not_full);
    pthread_mutex_unlock(&q->mutex);
    return data;
}

void queue_shutdown(bounded_queue_t* q) {
    pthread_mutex_lock(&q->mutex);
    if (q->stopped) {
        pthread_mutex_unlock(&q->mutex);
        return;
    }
    q->stopped = true;
    pthread_mutex_unlock(&q->mutex);

    pthread_cond_broadcast(&q->cv_not_empty);
    pthread_cond_broadcast(&q->cv_not_full);
}

void queue_destroy(bounded_queue_t* q) {
    if (!q) return;
    queue_shutdown(q);

    pthread_mutex_destroy(&q->mutex);
    pthread_cond_destroy(&q->cv_not_empty);
    pthread_cond_destroy(&q->cv_not_full);

    free(q->buffer);
    free(q);
}
