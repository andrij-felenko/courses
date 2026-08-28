#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <errno.h>

typedef enum {
    CHAN_OK = 0,
    CHAN_CLOSED = -1,
    CHAN_WOULDBLOCK = -2,
    CHAN_ERR = -3
} chan_status_t;

typedef struct {
    void **buffer;
    size_t capacity;
    size_t size;
    size_t head;
    size_t tail;
    bool closed;
    pthread_mutex_t lock;
    pthread_cond_t not_full;
    pthread_cond_t not_empty;
} chan_t;

chan_t *chan_create(size_t capacity) {
    if (capacity == 0) {
        capacity = 1; // Уніфіковане представлення для буферизованої черги
    }
    chan_t *ch = (chan_t *)malloc(sizeof(chan_t));
    if (!ch) return NULL;

    ch->buffer = (void **)malloc(sizeof(void *) * capacity);
    if (!ch->buffer) {
        free(ch);
        return NULL;
    }

    ch->capacity = capacity;
    ch->size = 0;
    ch->head = 0;
    ch->tail = 0;
    ch->closed = false;

    pthread_mutex_init(&ch->lock, NULL);
    pthread_cond_init(&ch->not_full, NULL);
    pthread_cond_init(&ch->not_empty, NULL);

    return ch;
}

chan_status_t chan_send(chan_t *ch, void *data) {
    pthread_mutex_lock(&ch->lock);

    while (ch->size == ch->capacity && !ch->closed) {
        pthread_cond_wait(&ch->not_full, &ch->lock);
    }

    if (ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_CLOSED;
    }

    ch->buffer[ch->tail] = data;
    ch->tail = (ch->tail + 1) % ch->capacity;
    ch->size++;

    pthread_cond_signal(&ch->not_empty);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t chan_recv(chan_t *ch, void **out_data) {
    pthread_mutex_lock(&ch->lock);

    while (ch->size == 0 && !ch->closed) {
        pthread_cond_wait(&ch->not_empty, &ch->lock);
    }

    if (ch->size == 0 && ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        *out_data = NULL;
        return CHAN_CLOSED;
    }

    *out_data = ch->buffer[ch->head];
    ch->head = (ch->head + 1) % ch->capacity;
    ch->size--;

    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t chan_try_send(chan_t *ch, void *data) {
    pthread_mutex_lock(&ch->lock);

    if (ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_CLOSED;
    }

    if (ch->size == ch->capacity) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_WOULDBLOCK;
    }

    ch->buffer[ch->tail] = data;
    ch->tail = (ch->tail + 1) % ch->capacity;
    ch->size++;

    pthread_cond_signal(&ch->not_empty);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t chan_try_recv(chan_t *ch, void **out_data) {
    pthread_mutex_lock(&ch->lock);

    if (ch->size == 0) {
        bool is_closed = ch->closed;
        pthread_mutex_unlock(&ch->lock);
        *out_data = NULL;
        return is_closed ? CHAN_CLOSED : CHAN_WOULDBLOCK;
    }

    *out_data = ch->buffer[ch->head];
    ch->head = (ch->head + 1) % ch->capacity;
    ch->size--;

    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

void chan_close(chan_t *ch) {
    pthread_mutex_lock(&ch->lock);
    if (!ch->closed) {
        ch->closed = true;
        pthread_cond_broadcast(&ch->not_full);
        pthread_cond_broadcast(&ch->not_empty);
    }
    pthread_mutex_unlock(&ch->lock);
}

void chan_destroy(chan_t *ch) {
    if (!ch) return;
    pthread_mutex_destroy(&ch->lock);
    pthread_cond_destroy(&ch->not_full);
    pthread_cond_destroy(&ch->not_empty);
    free(ch->buffer);
    free(ch);
}
