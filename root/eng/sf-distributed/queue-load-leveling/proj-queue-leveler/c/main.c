#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAX_QUEUE_CAPACITY 1024
#define MAX_PAYLOAD_LEN    256

/* Статуси операції постановки в чергу */
typedef enum {
    LEVELER_SUCCESS = 0,
    LEVELER_QUEUE_FULL = 1,
    LEVELER_SHUTDOWN = 2
} LevelerStatus;

/* Структура завдання */
typedef struct {
    uint64_t task_id;
    char     payload[MAX_PAYLOAD_LEN];
    uint64_t enqueue_time_ms;
    uint64_t deadline_ms; /* Абсолютний дедлайн у мілісекундах */
} Task;

/* Допоміжна функція отримання монотонного часу в мілісекундах */
static uint64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

/* Маркерний кошик для регулювання темпу споживання (Token Bucket) */
typedef struct {
    pthread_mutex_t lock;
    double          tokens;
    double          capacity;
    double          fill_rate_per_sec;
    uint64_t        last_refill_ms;
} TokenBucket;

static void token_bucket_init(TokenBucket *tb, double rate_rps, double capacity) {
    pthread_mutex_init(&tb->lock, NULL);
    tb->tokens = capacity;
    tb->capacity = capacity;
    tb->fill_rate_per_sec = rate_rps;
    tb->last_refill_ms = current_time_ms();
}

static void token_bucket_destroy(TokenBucket *tb) {
    pthread_mutex_destroy(&tb->lock);
}

/* Спроба взяти токен з очікуванням */
static void token_bucket_consume(TokenBucket *tb) {
    while (1) {
        pthread_mutex_lock(&tb->lock);
        uint64_t now = current_time_ms();
        double elapsed_sec = (double)(now - tb->last_refill_ms) / 1000.0;
        tb->tokens += elapsed_sec * tb->fill_rate_per_sec;
        if (tb->tokens > tb->capacity) {
            tb->tokens = tb->capacity;
        }
        tb->last_refill_ms = now;

        if (tb->tokens >= 1.0) {
            tb->tokens -= 1.0;
            pthread_mutex_unlock(&tb->lock);
            return;
        }

        /* Розрахунок часу очікування до появи наступного токена */
        double needed = 1.0 - tb->tokens;
        useconds_t wait_us = (useconds_t)((needed / tb->fill_rate_per_sec) * 1000000.0);
        pthread_mutex_unlock(&tb->lock);

        if (wait_us < 1000) wait_us = 1000;
        usleep(wait_us);
    }
}

/* Обмежений кільцевий буфер черги з демпфуванням */
typedef struct {
    Task            ring[MAX_QUEUE_CAPACITY];
    size_t          head;
    size_t          tail;
    size_t          count;
    size_t          max_capacity;
    bool            shutdown;

    pthread_mutex_t lock;
    pthread_cond_t  not_empty;

    TokenBucket     rate_limiter;

    /* Метрики */
    uint64_t        tasks_processed;
    uint64_t        tasks_rejected;
    uint64_t        tasks_expired;
} QueueLoadLeveler;

void leveler_init(QueueLoadLeveler *ql, size_t capacity, double max_rate_rps) {
    memset(ql, 0, sizeof(*ql));
    ql->max_capacity = (capacity > MAX_QUEUE_CAPACITY) ? MAX_QUEUE_CAPACITY : capacity;
    pthread_mutex_init(&ql->lock, NULL);
    pthread_cond_init(&ql->not_empty, NULL);
    token_bucket_init(&ql->rate_limiter, max_rate_rps, max_rate_rps * 0.2); /* Бурст 20% */
}

void leveler_destroy(QueueLoadLeveler *ql) {
    pthread_mutex_destroy(&ql->lock);
    pthread_cond_destroy(&ql->not_empty);
    token_bucket_destroy(&ql->rate_limiter);
}

/* Неблокуюча постановка задачі у чергу (Ingress) */
LevelerStatus leveler_enqueue(QueueLoadLeveler *ql, const char *payload, uint64_t timeout_ms) {
    pthread_mutex_lock(&ql->lock);

    if (ql->shutdown) {
        pthread_mutex_unlock(&ql->lock);
        return LEVELER_SHUTDOWN;
    }

    /* Якщо буфер переповнений — негайний бекпреше (Load Shedding) */
    if (ql->count >= ql->max_capacity) {
        ql->tasks_rejected++;
        pthread_mutex_unlock(&ql->lock);
        return LEVELER_QUEUE_FULL;
    }

    uint64_t now = current_time_ms();
    Task *t = &ql->ring[ql->tail];
    t->task_id = ql->tasks_processed + ql->count + 1;
    strncpy(t->payload, payload, MAX_PAYLOAD_LEN - 1);
    t->payload[MAX_PAYLOAD_LEN - 1] = '\0';
    t->enqueue_time_ms = now;
    t->deadline_ms = now + timeout_ms;

    ql->tail = (ql->tail + 1) % ql->max_capacity;
    ql->count++;

    pthread_cond_signal(&ql->not_empty);
    pthread_mutex_unlock(&ql->lock);

    return LEVELER_SUCCESS;
}

/* Вичитування задачі воркером з контролем темпу та дедлайну */
bool leveler_dequeue(QueueLoadLeveler *ql, Task *out_task) {
    while (1) {
        pthread_mutex_lock(&ql->lock);

        while (ql->count == 0 && !ql->shutdown) {
            pthread_cond_wait(&ql->not_empty, &ql->lock);
        }

        if (ql->count == 0 && ql->shutdown) {
            pthread_mutex_unlock(&ql->lock);
            return false;
        }

        /* Забираємо задачу з черги */
        *out_task = ql->ring[ql->head];
        ql->head = (ql->head + 1) % ql->max_capacity;
        ql->count--;

        pthread_mutex_unlock(&ql->lock);

        /* Перевірка дедлайну (чи не застаріла задача в черзі) */
        uint64_t now = current_time_ms();
        if (now > out_task->deadline_ms) {
            pthread_mutex_lock(&ql->lock);
            ql->tasks_expired++;
            pthread_mutex_unlock(&ql->lock);
            continue; /* Пропускаємо протерміновану задачу */
        }

        /* Застосування токен-бакета: воркер затримується до дозволеного темпу */
        token_bucket_consume(&ql->rate_limiter);

        pthread_mutex_lock(&ql->lock);
        ql->tasks_processed++;
        pthread_mutex_unlock(&ql->lock);

        return true;
    }
}

void leveler_stop(QueueLoadLeveler *ql) {
    pthread_mutex_lock(&ql->lock);
    ql->shutdown = true;
    pthread_cond_broadcast(&ql->not_empty);
    pthread_mutex_unlock(&ql->lock);
}
