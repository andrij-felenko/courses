#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>

typedef struct {
    double capacity;         /* Максимальна місткість (токени) */
    double tokens;           /* Поточний залишок токенів */
    double refill_rate;      /* Токенів на секунду */
    uint64_t last_refill_ns; /* Час останнього поповнення (наносекунди) */
    pthread_mutex_t lock;    /* М'ютекс захисту стану */
} token_bucket_t;

/* Отримання монотонного часу в наносекундах */
static uint64_t get_monotonic_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

void token_bucket_init(token_bucket_t *tb, double capacity, double refill_rate) {
    tb->capacity = capacity;
    tb->tokens = capacity;
    tb->refill_rate = refill_rate;
    tb->last_refill_ns = get_monotonic_ns();
    pthread_mutex_init(&tb->lock, NULL);
}

void token_bucket_destroy(token_bucket_t *tb) {
    pthread_mutex_destroy(&tb->lock);
}

bool token_bucket_try_consume(token_bucket_t *tb, double tokens_to_consume) {
    pthread_mutex_lock(&tb->lock);

    uint64_t now_ns = get_monotonic_ns();
    uint64_t elapsed_ns = now_ns - tb->last_refill_ns;
    tb->last_refill_ns = now_ns;

    /* Поповнення токенів за минулий інтервал часу */
    double delta_sec = (double)elapsed_ns / 1000000000.0;
    tb->tokens += delta_sec * tb->refill_rate;
    if (tb->tokens > tb->capacity) {
        tb->tokens = tb->capacity;
    }

    bool allowed = false;
    if (tb->tokens >= tokens_to_consume) {
        tb->tokens -= tokens_to_consume;
        allowed = true;
    }

    pthread_mutex_unlock(&tb->lock);
    return allowed;
}
