#include <pthread.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct {
    void** buffer;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
    bool is_closed;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} BoundedQueueC;

BoundedQueueC* bq_create(size_t capacity) {
    if (capacity == 0) return NULL;
    BoundedQueueC* q = (BoundedQueueC*)malloc(sizeof(BoundedQueueC));
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
    q->is_closed = false;

    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
    return q;
}

bool bq_push(BoundedQueueC* q, void* item) {
    pthread_mutex_lock(&q->lock);

    // Семантика Меса: обов'язковий цикл while для перевірки умови
    while (q->count == q->capacity && !q->is_closed) {
        pthread_cond_wait(&q->not_full, &q->lock);
    }

    if (q->is_closed) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    q->buffer[q->tail] = item;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;

    // Сповіщаємо одного сплячого споживача
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

bool bq_pop(BoundedQueueC* q, void** out_item) {
    pthread_mutex_lock(&q->lock);

    while (q->count == 0 && !q->is_closed) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }

    if (q->count == 0 && q->is_closed) {
        pthread_mutex_unlock(&q->lock);
        return false; // Черга закрита і повністю вичерпана
    }

    *out_item = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;

    // Сповіщаємо одного сплячого виробника
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return true;
}

void bq_close(BoundedQueueC* q) {
    pthread_mutex_lock(&q->lock);
    q->is_closed = true;
    // Будимо абсолютно всі заблоковані потоки
    pthread_cond_broadcast(&q->not_empty);
    pthread_cond_broadcast(&q->not_full);
    pthread_mutex_unlock(&q->lock);
}

void bq_destroy(BoundedQueueC* q) {
    if (!q) return;
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);
    free(q->buffer);
    free(q);
}
