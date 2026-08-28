#include <pthread.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int* data;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;

    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} queue_t;

queue_t* queue_create(size_t capacity) {
    queue_t* q = (queue_t*)malloc(sizeof(queue_t));
    if (!q) return NULL;

    q->data = (int*)malloc(sizeof(int) * capacity);
    if (!q->data) {
        free(q);
        return NULL;
    }

    q->capacity = capacity;
    q->head = 0;
    q->tail = 0;
    q->count = 0;

    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);

    return q;
}

void queue_push(queue_t* q, int value) {
    pthread_mutex_lock(&q->lock);

    /* Захист Mesa: перевірка місткості тільки в циклі while */
    while (q->count == q->capacity) {
        pthread_cond_wait(&q->not_full, &q->lock);
    }

    q->data[q->tail] = value;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;

    /* Будимо рівно одного очікуючого споживача */
    pthread_cond_signal(&q->not_empty);

    pthread_mutex_unlock(&q->lock);
}

int queue_pop(queue_t* q) {
    pthread_mutex_lock(&q->lock);

    /* Захист Mesa: перевірка наявності тільки в циклі while */
    while (q->count == 0) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }

    int value = q->data[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;

    /* Будимо рівно одного очікуючого виробника */
    pthread_cond_signal(&q->not_full);

    pthread_mutex_unlock(&q->lock);
    return value;
}

void queue_destroy(queue_t* q) {
    if (!q) return;
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);
    free(q->data);
    free(q);
}
