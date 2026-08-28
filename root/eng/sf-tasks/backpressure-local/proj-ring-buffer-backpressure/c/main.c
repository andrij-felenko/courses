#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <errno.h>

typedef enum {
    DROP_NONE = 0,    /* Блокуючий протитиск (чекати LWM) */
    DROP_NEWEST = 1,  /* Відхилити вхідний елемент */
    DROP_OLDEST = 2   /* Перетерти найстаріший елемент (Head drop) */
} drop_policy_t;

typedef struct {
    int64_t *data;
    size_t capacity;
    size_t mask;
    size_t head;
    size_t tail;
    size_t hwm;
    size_t lwm;
    bool is_paused;
    bool is_closed;

    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t can_produce;
} ring_buffer_t;

/* Ініціалізація кільцевого буфера */
int ring_buffer_init(ring_buffer_t *rb, size_t capacity, size_t hwm, size_t lwm) {
    if ((capacity & (capacity - 1)) != 0 || capacity == 0) {
        return -EINVAL; /* Ємність мусить бути степенем двійки */
    }
    if (hwm > capacity || lwm >= hwm) {
        return -EINVAL; /* Некоректні водяні знаки */
    }

    rb->data = (int64_t *)malloc(capacity * sizeof(int64_t));
    if (!rb->data) return -ENOMEM;

    rb->capacity = capacity;
    rb->mask = capacity - 1;
    rb->head = 0;
    rb->tail = 0;
    rb->hwm = hwm;
    rb->lwm = lwm;
    rb->is_paused = false;
    rb->is_closed = false;

    pthread_mutex_init(&rb->lock, NULL);
    pthread_cond_init(&rb->not_empty, NULL);
    pthread_cond_init(&rb->can_produce, NULL);

    return 0;
}

/* Звільнення ресурсів */
void ring_buffer_destroy(ring_buffer_t *rb) {
    pthread_mutex_lock(&rb->lock);
    rb->is_closed = true;
    pthread_cond_broadcast(&rb->not_empty);
    pthread_cond_broadcast(&rb->can_produce);
    pthread_mutex_unlock(&rb->lock);

    pthread_mutex_destroy(&rb->lock);
    pthread_cond_destroy(&rb->not_empty);
    pthread_cond_destroy(&rb->can_produce);
    free(rb->data);
}

/* Блокуючий запис із контролем HWM/LWM протитиску */
int ring_buffer_push_blocking(ring_buffer_t *rb, int64_t item) {
    pthread_mutex_lock(&rb->lock);

    while (!rb->is_closed) {
        size_t count = rb->tail - rb->head;

        /* Якщо буфер досяг HWM, активуємо паузу */
        if (count >= rb->hwm) {
            rb->is_paused = true;
        }

        /* Якщо пауза активна, виробник спить до опускання нижче LWM */
        if (rb->is_paused) {
            pthread_cond_wait(&rb->can_produce, &rb->lock);
            continue;
        }

        /* Запис елемента */
        rb->data[rb->tail & rb->mask] = item;
        rb->tail++;

        /* Сповіщення споживача */
        pthread_cond_signal(&rb->not_empty);
        pthread_mutex_unlock(&rb->lock);
        return 0;
    }

    pthread_mutex_unlock(&rb->lock);
    return -EPIPE; /* Чергу закрито */
}

/* Неблокуючий запис із політикою скидання */
int ring_buffer_try_push(ring_buffer_t *rb, int64_t item, drop_policy_t policy) {
    pthread_mutex_lock(&rb->lock);

    if (rb->is_closed) {
        pthread_mutex_unlock(&rb->lock);
        return -EPIPE;
    }

    size_t count = rb->tail - rb->head;

    if (count >= rb->capacity) {
        if (policy == DROP_NEWEST) {
            pthread_mutex_unlock(&rb->lock);
            return -EAGAIN; /* Відкинути новий пакет */
        } else if (policy == DROP_OLDEST) {
            /* Витіснити найстаріший елемент */
            rb->head++;
        } else {
            pthread_mutex_unlock(&rb->lock);
            return -EBUSY;
        }
    }

    rb->data[rb->tail & rb->mask] = item;
    rb->tail++;

    pthread_cond_signal(&rb->not_empty);
    pthread_mutex_unlock(&rb->lock);
    return 0;
}

/* Блокуюче читання споживача з перевіркою LWM для пробудження */
int ring_buffer_pop_blocking(ring_buffer_t *rb, int64_t *out_item) {
    pthread_mutex_lock(&rb->lock);

    while (rb->tail == rb->head && !rb->is_closed) {
        pthread_cond_wait(&rb->not_empty, &rb->lock);
    }

    if (rb->tail == rb->head && rb->is_closed) {
        pthread_mutex_unlock(&rb->lock);
        return -EPIPE;
    }

    *out_item = rb->data[rb->head & rb->mask];
    rb->head++;

    size_t count = rb->tail - rb->head;

    /* Якщо виробник спав і черга опустилася до LWM — будимо виробника */
    if (rb->is_paused && count <= rb->lwm) {
        rb->is_paused = false;
        pthread_cond_broadcast(&rb->can_produce);
    }

    pthread_mutex_unlock(&rb->lock);
    return 0;
}
