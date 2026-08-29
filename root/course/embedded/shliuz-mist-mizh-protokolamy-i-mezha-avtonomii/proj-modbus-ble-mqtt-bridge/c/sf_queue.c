#define _POSIX_C_SOURCE 200809L

#include "sf_queue.h"

#include <string.h>
#include <time.h>

int64_t sf_now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static void ring_bind(sf_ring_t *r, telemetry_msg_t *storage, size_t cap)
{
    r->items = storage;
    r->cap = cap;
    r->head = 0;
    r->tail = 0;
    r->count = 0;
}

static void ring_push(sf_ring_t *r, const telemetry_msg_t *msg)
{
    r->items[r->head] = *msg;
    r->head = (r->head + 1) % r->cap;
    r->count++;
}

static void ring_pop(sf_ring_t *r, telemetry_msg_t *out)
{
    if (out)
        *out = r->items[r->tail];
    r->tail = (r->tail + 1) % r->cap;
    r->count--;
}

void sf_init(sf_queue_t *q)
{
    memset(q, 0, sizeof(*q));
    ring_bind(&q->fresh, q->fresh_storage, FRESH_CAPACITY);
    ring_bind(&q->backlog, q->backlog_storage, BUFFER_CAPACITY);
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
}

void sf_destroy(sf_queue_t *q)
{
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
}

void sf_publish(sf_queue_t *q, const telemetry_msg_t *msg)
{
    pthread_mutex_lock(&q->lock);

    if (q->fresh.count == q->fresh.cap) {
        /* Свіжа черга заповнилася — канал стоїть. Найстаріше з неї стає
         * історією й переїжджає в архів. */
        telemetry_msg_t aged;
        ring_pop(&q->fresh, &aged);
        if (q->backlog.count == q->backlog.cap) {
            /* Архів теж повний: жертвуємо найдавнішим (FIFO Drop). Розрив
             * у номерах послідовності побачить сервер і знатиме про втрату. */
            ring_pop(&q->backlog, NULL);
            q->dropped++;
        }
        ring_push(&q->backlog, &aged);
    }

    ring_push(&q->fresh, msg);
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
}

bool sf_peek(sf_queue_t *q, telemetry_msg_t *out, bool *from_backlog, unsigned wait_ms)
{
    pthread_mutex_lock(&q->lock);

    if (q->fresh.count == 0 && q->backlog.count == 0) {
        struct timespec deadline;
        clock_gettime(CLOCK_REALTIME, &deadline);
        deadline.tv_sec += wait_ms / 1000;
        deadline.tv_nsec += (long)(wait_ms % 1000) * 1000000L;
        if (deadline.tv_nsec >= 1000000000L) {
            deadline.tv_sec++;
            deadline.tv_nsec -= 1000000000L;
        }
        while (q->fresh.count == 0 && q->backlog.count == 0) {
            if (pthread_cond_timedwait(&q->not_empty, &q->lock, &deadline) != 0)
                break;   /* вийшов час або хибне пробудження за дедлайном */
        }
    }

    bool have = true;
    if (q->fresh.count > 0) {
        *out = q->fresh.items[q->fresh.tail];
        *from_backlog = false;
    } else if (q->backlog.count > 0) {
        *out = q->backlog.items[q->backlog.tail];
        *from_backlog = true;
    } else {
        have = false;
    }

    pthread_mutex_unlock(&q->lock);
    return have;
}

void sf_commit(sf_queue_t *q, bool from_backlog, uint32_t seq)
{
    pthread_mutex_lock(&q->lock);
    sf_ring_t *r = from_backlog ? &q->backlog : &q->fresh;
    /* Поки ми чекали PUBACK, витіснення могло зсунути хвіст. Знімаємо лише
     * те саме повідомлення, яке справді пішло в сокет. */
    if (r->count > 0 && r->items[r->tail].seq == seq)
        ring_pop(r, NULL);
    pthread_mutex_unlock(&q->lock);
}

void sf_stats(sf_queue_t *q, size_t *fresh, size_t *backlog, uint32_t *dropped)
{
    pthread_mutex_lock(&q->lock);
    if (fresh)
        *fresh = q->fresh.count;
    if (backlog)
        *backlog = q->backlog.count;
    if (dropped)
        *dropped = q->dropped;
    pthread_mutex_unlock(&q->lock);
}
