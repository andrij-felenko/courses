#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

typedef enum {
    LONG_OP_STATE_PENDING = 0,
    LONG_OP_STATE_RUNNING,
    LONG_OP_STATE_SUCCEEDED,
    LONG_OP_STATE_FAILED,
    LONG_OP_STATE_CANCELLED
} long_op_state_t;

typedef struct {
    char error_type[64];
    char title[128];
    int status_code;
    char detail[256];
} long_op_error_t;

typedef struct {
    char operation_id[37];
    char idempotency_key[64];
    long_op_state_t state;
    float progress;              /* 0.0f .. 1.0f */
    uint32_t attempt_count;
    uint64_t lease_token;
    time_t lease_expires_at;
    time_t created_at;
    time_t updated_at;
    bool cancel_requested;
    char result_url[256];
    long_op_error_t error;
} long_op_context_t;

/* Перевірка допустимості переходу між станами */
bool long_op_can_transition(long_op_state_t from, long_op_state_t to) {
    switch (from) {
        case LONG_OP_STATE_PENDING:
            return (to == LONG_OP_STATE_RUNNING || 
                    to == LONG_OP_STATE_CANCELLED || 
                    to == LONG_OP_STATE_FAILED);
        case LONG_OP_STATE_RUNNING:
            return (to == LONG_OP_STATE_SUCCEEDED || 
                    to == LONG_OP_STATE_FAILED || 
                    to == LONG_OP_STATE_CANCELLED ||
                    to == LONG_OP_STATE_PENDING); /* Повернення в чергу при спливу оренди */
        case LONG_OP_STATE_SUCCEEDED:
        case LONG_OP_STATE_FAILED:
        case LONG_OP_STATE_CANCELLED:
            return false; /* Фінальні стани незмінні */
        default:
            return false;
    }
}

/* Обчислення паузи опитування з повним джитером (Full Jitter) */
uint32_t long_op_calc_backoff_jitter(uint32_t attempt, uint32_t base_sec, uint32_t max_sec) {
    if (attempt > 20) attempt = 20;
    uint64_t raw_backoff = (uint64_t)base_sec * (1ULL << attempt);
    uint32_t capped = (raw_backoff > max_sec) ? max_sec : (uint32_t)raw_backoff;
    if (capped == 0) return 0;
    return (uint32_t)(rand() % (capped + 1));
}

/* Захоплення оренди воркером */
bool long_op_claim_lease(long_op_context_t *ctx, uint64_t worker_token, uint32_t lease_dur_sec, time_t now) {
    if (!ctx) return false;
    
    bool is_pending = (ctx->state == LONG_OP_STATE_PENDING);
    bool is_expired = (ctx->state == LONG_OP_STATE_RUNNING && ctx->lease_expires_at < now);
    
    if (!is_pending && !is_expired) return false;
    if (!long_op_can_transition(ctx->state, LONG_OP_STATE_RUNNING)) return false;
    
    ctx->state = LONG_OP_STATE_RUNNING;
    ctx->lease_token = worker_token;
    ctx->lease_expires_at = now + lease_dur_sec;
    ctx->attempt_count++;
    ctx->updated_at = now;
    return true;
}

/* Поновлення оренди через серцебиття */
bool long_op_heartbeat(long_op_context_t *ctx, uint64_t worker_token, float progress, uint32_t lease_ext_sec, time_t now) {
    if (!ctx) return false;
    if (ctx->state != LONG_OP_STATE_RUNNING) return false;
    if (ctx->lease_token != worker_token) return false;
    if (ctx->lease_expires_at < now) return false;

    ctx->lease_expires_at = now + lease_ext_sec;
    if (progress >= 0.0f && progress <= 1.0f) {
        ctx->progress = progress;
    }
    ctx->updated_at = now;
    return true;
}

/* Фіксація успішного завершення під захистом токена оренди */
bool long_op_complete_success(long_op_context_t *ctx, uint64_t worker_token, const char *result_url, time_t now) {
    if (!ctx || !result_url) return false;
    if (ctx->state != LONG_OP_STATE_RUNNING) return false;
    if (ctx->lease_token != worker_token) return false;
    if (ctx->lease_expires_at < now) return false;

    if (!long_op_can_transition(ctx->state, LONG_OP_STATE_SUCCEEDED)) return false;

    ctx->state = LONG_OP_STATE_SUCCEEDED;
    ctx->progress = 1.0f;
    strncpy(ctx->result_url, result_url, sizeof(ctx->result_url) - 1);
    ctx->result_url[sizeof(ctx->result_url) - 1] = '\0';
    ctx->updated_at = now;
    return true;
}

/* Фіксація помилки */
bool long_op_complete_failure(long_op_context_t *ctx, uint64_t worker_token, const long_op_error_t *err, time_t now) {
    if (!ctx || !err) return false;
    if (ctx->state != LONG_OP_STATE_RUNNING) return false;
    if (ctx->lease_token != worker_token) return false;

    if (!long_op_can_transition(ctx->state, LONG_OP_STATE_FAILED)) return false;

    ctx->state = LONG_OP_STATE_FAILED;
    memcpy(&ctx->error, err, sizeof(long_op_error_t));
    ctx->updated_at = now;
    return true;
}
