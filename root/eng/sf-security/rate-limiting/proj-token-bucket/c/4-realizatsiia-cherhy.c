#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

typedef struct {
    int id;
    void *payload;
} request_item_t;

typedef struct {
    request_item_t *buffer;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} leaky_queue_t;

void leaky_queue_init(leaky_queue_t *q, size_t capacity) {
    q->buffer = (request_item_t *)malloc(sizeof(request_item_t) * capacity);
    q->capacity = capacity;
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

bool leaky_queue_push(leaky_queue_t *q, request_item_t item) {
    pthread_mutex_lock(&q->lock);
    if (q->count >= q->capacity) {
        pthread_mutex_unlock(&q->lock);
        return false; /* Переповнення: скидання запиту */
    }
    q->buffer[q->tail] = item;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

request_item_t leaky_queue_pop_rate_limited(leaky_queue_t *q, uint32_t interval_us) {
    pthread_mutex_lock(&q->lock);
    while (q->count == 0) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }
    request_item_t item = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);

    /* Шейпінг: примусова затримка між обробкою елементів */
    usleep(interval_us);
    return item;
}

void leaky_queue_destroy(leaky_queue_t *q) {
    free(q->buffer);
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);
}
