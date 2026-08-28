#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <unistd.h>
#include <pthread.h>
#include <stdbool.h>

typedef enum {
    ERR_TRANSIENT,
    ERR_PERMANENT
} ErrorKind;

typedef struct {
    int status_code;
    char body[256];
} HttpResponse;

typedef struct {
    ErrorKind kind;
    int status_code;
    char message[256];
} RequestError;

typedef struct {
    int max_attempts;
    long base_backoff_ms;
    long max_backoff_ms;
    double multiplier;
    double deposit_per_success;
    double withdraw_per_retry;
    double max_tokens;
} RetryPolicy;

typedef struct {
    pthread_mutex_t lock;
    double tokens;
    double max_tokens;
} TokenBucket;

void token_bucket_init(TokenBucket* tb, double max_tokens, double initial) {
    pthread_mutex_init(&tb->lock, NULL);
    tb->max_tokens = max_tokens;
    tb->tokens = initial;
}

void token_bucket_record_success(TokenBucket* tb, double deposit) {
    pthread_mutex_lock(&tb->lock);
    tb->tokens += deposit;
    if (tb->tokens > tb->max_tokens) tb->tokens = tb->max_tokens;
    pthread_mutex_unlock(&tb->lock);
}

bool token_bucket_try_withdraw(TokenBucket* tb, double cost) {
    bool ok = false;
    pthread_mutex_lock(&tb->lock);
    if (tb->tokens >= cost) {
        tb->tokens -= cost;
        ok = true;
    }
    pthread_mutex_unlock(&tb->lock);
    return ok;
}

long calculate_full_jitter(const RetryPolicy* p, int attempt_index) {
    double factor = pow(p->multiplier, attempt_index);
    double max_ms = (double)p->base_backoff_ms * factor;
    if (max_ms > (double)p->max_backoff_ms) max_ms = (double)p->max_backoff_ms;
    
    double r = (double)rand() / (double)RAND_MAX;
    return (long)(r * max_ms);
}

ErrorKind classify_status(int status_code) {
    if (status_code == 408 || status_code == 429 || status_code == 502 || 
        status_code == 503 || status_code == 504) {
        return ERR_TRANSIENT;
    }
    if (status_code >= 400 && status_code < 500) {
        return ERR_PERMANENT;
    }
    if (status_code >= 500) {
        return ERR_TRANSIENT;
    }
    return ERR_PERMANENT;
}

// Монотонний годинник у мілісекундах без стрибків NTP
long get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

// Емуляція мережевого транспорту з тимчасовим збоєм
bool mock_transport(const char* url, const char* key, int* out_status, char* out_body) {
    static int attempt_count = 0;
    attempt_count++;
    if (attempt_count <= 2) {
        *out_status = 503;
        snprintf(out_body, 256, "Service Busy");
        return true;
    }
    *out_status = 200;
    snprintf(out_body, 256, "{\"status\":\"success\"}");
    return true;
}

int main(void) {
    srand((unsigned)time(NULL));
    
    RetryPolicy policy = {
        .max_attempts = 4,
        .base_backoff_ms = 100,
        .max_backoff_ms = 3000,
        .multiplier = 2.0,
        .deposit_per_success = 0.10,
        .withdraw_per_retry = 1.00,
        .max_tokens = 100.0
    };
    
    TokenBucket budget;
    token_bucket_init(&budget, policy.max_tokens, 15.0);
    
    long start_time = get_monotonic_ms();
    long deadline_ms = start_time + 5000; // 5 секунд загальний дедлайн
    
    int status = 0;
    char body[256] = {0};
    bool request_succeeded = false;
    
    for (int attempt = 0; attempt < policy.max_attempts; ++attempt) {
        long now = get_monotonic_ms();
        if (now >= deadline_ms) {
            printf("Дедлайн операції вичерпано!\n");
            break;
        }
        
        if (attempt > 0) {
            // Перевірка наявності токенів у бюджеті повторів
            if (!token_bucket_try_withdraw(&budget, policy.withdraw_per_retry)) {
                printf("Бюджет повторів вичерпано (Fast-Fail захист)!\n");
                break;
            }
            
            long backoff_ms = calculate_full_jitter(&policy, attempt - 1);
            if (now + backoff_ms >= deadline_ms) {
                printf("Розрахована затримка відступу виходить за межі дедлайну!\n");
                break;
            }
            
            usleep((useconds_t)(backoff_ms * 1000));
        }
        
        if (mock_transport("https://api.payments.internal/v1/charge", "req-key-123", &status, body)) {
            if (status >= 200 && status < 300) {
                token_bucket_record_success(&budget, policy.deposit_per_success);
                request_succeeded = true;
                break;
            }
            
            ErrorKind k = classify_status(status);
            if (k == ERR_PERMANENT) {
                printf("Постійна помилка HTTP %d, скасування повторів.\n", status);
                break;
            }
            printf("  [Спроба %d] Тимчасова помилка HTTP %d -> планування повтору\n", attempt + 1, status);
        }
    }
    
    if (request_succeeded) {
        printf("Успішно отримано відповідь: %s\n", body);
    } else {
        printf("Операція завершилася відмовою.\n");
    }
    
    pthread_mutex_destroy(&budget.lock);
    return 0;
}
