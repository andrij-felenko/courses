#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>

/* Стани скінченного автомата запобіжника (Circuit Breaker) */
typedef enum {
    CB_STATE_CLOSED,    /* Нормальний режим: пропускає всі запити */
    CB_STATE_OPEN,      /* Режим ізоляції: миттєво відхиляє запити */
    CB_STATE_HALF_OPEN  /* Пробний режим: пропускає один тестовий запит */
} CircuitState;

typedef struct {
    CircuitState state;
    uint32_t failure_count;
    uint32_t failure_threshold;
    uint64_t open_time_ms;
    uint64_t cooloff_period_ms;
} CircuitBreaker;

typedef struct {
    uint64_t deadline_ms;
    uint32_t max_retries;
    uint64_t base_backoff_ms;
    uint64_t max_backoff_ms;
} RpcPolicy;

typedef struct {
    char idempotency_key[37];
    const char *payload;
    size_t payload_len;
} RpcRequest;

typedef struct {
    int status_code;
    char body[256];
    bool is_success;
} RpcResponse;

/* Отримання монотонного часу в мілісекундах для виключення дрейфу NTP */
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Генерація псевдовипадкового джитера у діапазоні [0, max_val] */
static uint64_t full_jitter(uint64_t base_ms, uint64_t max_ms, uint32_t attempt) {
    uint64_t exp_limit = base_ms * (1ULL << (attempt > 20 ? 20 : attempt));
    if (exp_limit > max_ms) {
        exp_limit = max_ms;
    }
    double r = (double)rand() / (double)RAND_MAX;
    return (uint64_t)(r * (double)exp_limit);
}

void cb_init(CircuitBreaker *cb, uint32_t threshold, uint64_t cooloff_ms) {
    cb->state = CB_STATE_CLOSED;
    cb->failure_count = 0;
    cb->failure_threshold = threshold;
    cb->open_time_ms = 0;
    cb->cooloff_period_ms = cooloff_ms;
}

bool cb_allow_request(CircuitBreaker *cb) {
    uint64_t now = get_monotonic_ms();
    if (cb->state == CB_STATE_OPEN) {
        if (now - cb->open_time_ms >= cb->cooloff_period_ms) {
            cb->state = CB_STATE_HALF_OPEN;
            return true;
        }
        return false;
    }
    return true;
}

void cb_record_result(CircuitBreaker *cb, bool success) {
    if (success) {
        cb->failure_count = 0;
        cb->state = CB_STATE_CLOSED;
    } else {
        cb->failure_count++;
        if (cb->state == CB_STATE_HALF_OPEN || cb->failure_count >= cb->failure_threshold) {
            cb->state = CB_STATE_OPEN;
            cb->open_time_ms = get_monotonic_ms();
        }
    }
}

/* Імітація ненадійного віддаленого виклику з імовірністю відмови */
static bool mock_network_call(const RpcRequest *req, RpcResponse *res) {
    /* 40% імовірність мережевого скидання / таймауту */
    int roll = rand() % 100;
    if (roll < 40) {
        res->status_code = 503;
        res->is_success = false;
        snprintf(res->body, sizeof(res->body), "Service Unavailable (Timeout)");
        return false;
    }
    res->status_code = 200;
    res->is_success = true;
    snprintf(res->body, sizeof(res->body), "Processed [%s] OK", req->idempotency_key);
    return true;
}

bool rpc_invoke_resilient(CircuitBreaker *cb, const RpcPolicy *policy,
                          const RpcRequest *req, RpcResponse *out_res) {
    uint64_t start_time = get_monotonic_ms();
    uint64_t deadline = start_time + policy->deadline_ms;

    for (uint32_t attempt = 0; attempt < policy->max_retries; attempt++) {
        uint64_t now = get_monotonic_ms();
        if (now >= deadline) {
            out_res->status_code = 504;
            out_res->is_success = false;
            snprintf(out_res->body, sizeof(out_res->body), "Client Deadline Exceeded");
            return false;
        }

        if (!cb_allow_request(cb)) {
            out_res->status_code = 503;
            out_res->is_success = false;
            snprintf(out_res->body, sizeof(out_res->body), "Circuit Breaker OPEN - Short Circuited");
            return false;
        }

        bool ok = mock_network_call(req, out_res);
        cb_record_result(cb, ok);

        if (ok) {
            return true;
        }

        /* Неповторювані клієнтські помилки (4xx) не потребують ретраю */
        if (out_res->status_code >= 400 && out_res->status_code < 500) {
            return false;
        }

        /* Обчислення інтервалу паузи з урахуванням залишку бюджету часу */
        uint64_t sleep_ms = full_jitter(policy->base_backoff_ms, policy->max_backoff_ms, attempt);
        now = get_monotonic_ms();
        if (now + sleep_ms >= deadline) {
            out_res->status_code = 504;
            out_res->is_success = false;
            snprintf(out_res->body, sizeof(out_res->body), "Deadline would be exceeded during backoff");
            return false;
        }

        usleep((useconds_t)(sleep_ms * 1000ULL));
    }
    return false;
}
