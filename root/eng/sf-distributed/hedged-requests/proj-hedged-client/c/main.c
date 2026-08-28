#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/time.h>
#include <errno.h>

typedef struct {
    pthread_mutex_t mutex;
    double max_tokens;
    double tokens;
    double refill_ratio;
} token_bucket_t;

void token_bucket_init(token_bucket_t *b, double max_t, double ratio) {
    pthread_mutex_init(&b->mutex, NULL);
    b->max_tokens = max_t;
    b->tokens = max_t;
    b->refill_ratio = ratio;
}

bool token_bucket_try_consume(token_bucket_t *b) {
    pthread_mutex_lock(&b->mutex);
    bool ok = false;
    if (b->tokens >= 1.0) {
        b->tokens -= 1.0;
        ok = true;
    }
    pthread_mutex_unlock(&b->mutex);
    return ok;
}

void token_bucket_record_success(token_bucket_t *b) {
    pthread_mutex_lock(&b->mutex);
    b->tokens += b->refill_ratio;
    if (b->tokens > b->max_tokens) {
        b->tokens = b->max_tokens;
    }
    pthread_mutex_unlock(&b->mutex);
}

typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    bool completed;
    char result[256];
    bool cancel_requested;
} hedged_context_t;

typedef struct {
    const char *endpoint;
    int simulated_delay_ms;
    hedged_context_t *ctx;
} worker_args_t;

void* replica_worker(void *arg) {
    worker_args_t *args = (worker_args_t*)arg;
    int step = 5;
    int elapsed = 0;

    while (elapsed < args->simulated_delay_ms) {
        pthread_mutex_lock(&args->ctx->mutex);
        if (args->ctx->cancel_requested) {
            pthread_mutex_unlock(&args->ctx->mutex);
            return NULL; // Скасовано іншою реплікою
        }
        pthread_mutex_unlock(&args->ctx->mutex);

        usleep(step * 1000);
        elapsed += step;
    }

    pthread_mutex_lock(&args->ctx->mutex);
    if (!args->ctx->completed) {
        args->ctx->completed = true;
        snprintf(args->ctx->result, sizeof(args->ctx->result),
                 "Response from %s", args->endpoint);
        pthread_cond_broadcast(&args->ctx->cond);
    }
    pthread_mutex_unlock(&args->ctx->mutex);
    return NULL;
}

bool execute_hedged_call_c(
    const char *ep1, int delay1_ms,
    const char *ep2, int delay2_ms,
    int hedge_delay_ms, int timeout_ms,
    token_bucket_t *budget, char *out_buf, size_t out_len)
{
    hedged_context_t ctx;
    pthread_mutex_init(&ctx.mutex, NULL);
    pthread_cond_init(&ctx.cond, NULL);
    ctx.completed = false;
    ctx.cancel_requested = false;
    ctx.result[0] = '\0';

    pthread_t t1, t2;
    bool t2_started = false;

    worker_args_t args1 = { ep1, delay1_ms, &ctx };
    pthread_create(&t1, NULL, replica_worker, &args1);

    // Очікуємо P95 затримку
    struct timeval now;
    struct timespec ts;
    gettimeofday(&now, NULL);
    ts.tv_sec = now.tv_sec + (now.tv_usec + hedge_delay_ms * 1000) / 1000000;
    ts.tv_nsec = ((now.tv_usec + hedge_delay_ms * 1000) % 1000000) * 1000;

    pthread_mutex_lock(&ctx.mutex);
    while (!ctx.completed) {
        int rc = pthread_cond_timedwait(&ctx.cond, &ctx.mutex, &ts);
        if (rc == ETIMEDOUT) break;
    }

    // Якщо первинний встиг
    if (ctx.completed) {
        token_bucket_record_success(budget);
        snprintf(out_buf, out_len, "%s", ctx.result);
        ctx.cancel_requested = true;
        pthread_mutex_unlock(&ctx.mutex);
        pthread_join(t1, NULL);
        return true;
    }

    // Відкладений гедж
    if (token_bucket_try_consume(budget)) {
        worker_args_t args2 = { ep2, delay2_ms, &ctx };
        pthread_create(&t2, NULL, replica_worker, &args2);
        t2_started = true;
    }

    // Залишковий таймаут
    gettimeofday(&now, NULL);
    int rem_ms = timeout_ms - hedge_delay_ms;
    ts.tv_sec = now.tv_sec + (now.tv_usec + rem_ms * 1000) / 1000000;
    ts.tv_nsec = ((now.tv_usec + rem_ms * 1000) % 1000000) * 1000;

    while (!ctx.completed) {
        int rc = pthread_cond_timedwait(&ctx.cond, &ctx.mutex, &ts);
        if (rc == ETIMEDOUT) break;
    }

    bool success = false;
    if (ctx.completed) {
        snprintf(out_buf, out_len, "%s", ctx.result);
        success = true;
    }

    ctx.cancel_requested = true;
    pthread_mutex_unlock(&ctx.mutex);

    pthread_join(t1, NULL);
    if (t2_started) {
        pthread_join(t2, NULL);
    }
    pthread_mutex_destroy(&ctx.mutex);
    pthread_cond_destroy(&ctx.cond);
    return success;
}

int main(void) {
    token_bucket_t budget;
    token_bucket_init(&budget, 10.0, 0.1);

    char response[256];
    bool ok = execute_hedged_call_c(
        "replica-1.internal", 80,  // повільна
        "replica-2.internal", 10,  // швидка
        25, 200, &budget, response, sizeof(response));

    if (ok) {
        printf("Успіх (C): %s\n", response);
    } else {
        printf("Помилка (C): Timeout\n");
    }
    return 0;
}
