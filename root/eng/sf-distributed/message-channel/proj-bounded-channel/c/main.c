#include <pthread.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>
#include <errno.h>

typedef enum {
    CHAN_OK = 0,
    CHAN_EMPTY = 1,
    CHAN_FULL = 2,
    CHAN_CLOSED = 3,
    CHAN_TIMEOUT = 4
} chan_status_t;

typedef struct {
    void **buffer;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
    bool closed;

    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} bounded_channel_t;

bounded_channel_t* channel_create(size_t capacity) {
    if (capacity == 0) return NULL;

    bounded_channel_t *ch = (bounded_channel_t*)malloc(sizeof(bounded_channel_t));
    if (!ch) return NULL;

    ch->buffer = (void**)malloc(sizeof(void*) * capacity);
    if (!ch->buffer) {
        free(ch);
        return NULL;
    }

    ch->capacity = capacity;
    ch->head = 0;
    ch->tail = 0;
    ch->count = 0;
    ch->closed = false;

    pthread_mutex_init(&ch->lock, NULL);
    pthread_cond_init(&ch->not_empty, NULL);
    pthread_cond_init(&ch->not_full, NULL);

    return ch;
}

chan_status_t channel_send(bounded_channel_t *ch, void *item) {
    pthread_mutex_lock(&ch->lock);

    while (ch->count == ch->capacity && !ch->closed) {
        pthread_cond_wait(&ch->not_full, &ch->lock);
    }

    if (ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_CLOSED;
    }

    ch->buffer[ch->tail] = item;
    ch->tail = (ch->tail + 1) % ch->capacity;
    ch->count++;

    pthread_cond_signal(&ch->not_empty);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t channel_try_send(bounded_channel_t *ch, void *item) {
    pthread_mutex_lock(&ch->lock);

    if (ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_CLOSED;
    }

    if (ch->count == ch->capacity) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_FULL;
    }

    ch->buffer[ch->tail] = item;
    ch->tail = (ch->tail + 1) % ch->capacity;
    ch->count++;

    pthread_cond_signal(&ch->not_empty);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t channel_recv(bounded_channel_t *ch, void **item) {
    pthread_mutex_lock(&ch->lock);

    while (ch->count == 0 && !ch->closed) {
        pthread_cond_wait(&ch->not_empty, &ch->lock);
    }

    if (ch->count == 0 && ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        *item = NULL;
        return CHAN_CLOSED;
    }

    *item = ch->buffer[ch->head];
    ch->head = (ch->head + 1) % ch->capacity;
    ch->count--;

    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t channel_try_recv(bounded_channel_t *ch, void **item) {
    pthread_mutex_lock(&ch->lock);

    if (ch->count == 0) {
        chan_status_t res = ch->closed ? CHAN_CLOSED : CHAN_EMPTY;
        pthread_mutex_unlock(&ch->lock);
        *item = NULL;
        return res;
    }

    *item = ch->buffer[ch->head];
    ch->head = (ch->head + 1) % ch->capacity;
    ch->count--;

    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t channel_recv_timeout(bounded_channel_t *ch, void **item, long timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    pthread_mutex_lock(&ch->lock);

    while (ch->count == 0 && !ch->closed) {
        int rc = pthread_cond_timedwait(&ch->not_empty, &ch->lock, &ts);
        if (rc == ETIMEDOUT) {
            pthread_mutex_unlock(&ch->lock);
            *item = NULL;
            return CHAN_TIMEOUT;
        }
    }

    if (ch->count == 0 && ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        *item = NULL;
        return CHAN_CLOSED;
    }

    *item = ch->buffer[ch->head];
    ch->head = (ch->head + 1) % ch->capacity;
    ch->count--;

    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

void channel_close(bounded_channel_t *ch) {
    pthread_mutex_lock(&ch->lock);
    ch->closed = true;
    pthread_cond_broadcast(&ch->not_empty);
    pthread_cond_broadcast(&ch->not_full);
    pthread_mutex_unlock(&ch->lock);
}

void channel_destroy(bounded_channel_t *ch) {
    if (!ch) return;
    pthread_mutex_destroy(&ch->lock);
    pthread_cond_destroy(&ch->not_empty);
    pthread_cond_destroy(&ch->not_full);
    free(ch->buffer);
    free(ch);
}
