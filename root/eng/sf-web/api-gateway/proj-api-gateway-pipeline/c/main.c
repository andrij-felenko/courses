#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>

#define MAX_HEADERS 32
#define MAX_HEADER_LEN 128
#define MAX_PATH_LEN 256
#define MAX_BODY_LEN 1024

// ── 1. Структури даних протоколу ───────────────────────────────────────────
typedef enum {
    HTTP_OK = 200,
    HTTP_UNAUTHORIZED = 401,
    HTTP_NOT_FOUND = 404,
    HTTP_TOO_MANY_REQUESTS = 429,
    HTTP_SERVICE_UNAVAILABLE = 503
} http_status_t;

typedef struct {
    char key[MAX_HEADER_LEN];
    char value[MAX_HEADER_LEN];
} http_header_t;

typedef struct {
    char method[16];
    char path[MAX_PATH_LEN];
    http_header_t headers[MAX_HEADERS];
    size_t header_count;
    char body[MAX_BODY_LEN];
} http_request_t;

typedef struct {
    http_status_t status;
    http_header_t headers[MAX_HEADERS];
    size_t header_count;
    char body[MAX_BODY_LEN];
} http_response_t;

// ── 2. Алгоритм Token Bucket на C з м'ютексом ──────────────────────────────
typedef struct {
    double capacity;
    double refill_rate_per_sec;
    double tokens;
    struct timespec last_refill;
    pthread_mutex_t lock;
} token_bucket_t;

void token_bucket_init(token_bucket_t *tb, double capacity, double refill_rate) {
    tb->capacity = capacity;
    tb->refill_rate_per_sec = refill_rate;
    tb->tokens = capacity;
    clock_gettime(CLOCK_MONOTONIC, &tb->last_refill);
    pthread_mutex_init(&tb->lock, NULL);
}

bool token_bucket_try_acquire(token_bucket_t *tb, double cost) {
    pthread_mutex_lock(&tb->lock);
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    double elapsed = (now.tv_sec - tb->last_refill.tv_sec) +
                     (now.tv_nsec - tb->last_refill.tv_nsec) / 1e9;
    tb->last_refill = now;

    tb->tokens += elapsed * tb->refill_rate_per_sec;
    if (tb->tokens > tb->capacity) {
        tb->tokens = tb->capacity;
    }

    if (tb->tokens >= cost) {
        tb->tokens -= cost;
        pthread_mutex_unlock(&tb->lock);
        return true;
    }

    pthread_mutex_unlock(&tb->lock);
    return false;
}

// ── 3. Очищення небезпечних заголовків та автентифікація ───────────────────
void req_remove_header(http_request_t *req, const char *key) {
    for (size_t i = 0; i < req->header_count; ++i) {
        if (strcasecmp(req->headers[i].key, key) == 0) {
            req->headers[i] = req->headers[req->header_count - 1];
            req->header_count--;
            i--;
        }
    }
}

void req_set_header(http_request_t *req, const char *key, const char *value) {
    for (size_t i = 0; i < req->header_count; ++i) {
        if (strcasecmp(req->headers[i].key, key) == 0) {
            snprintf(req->headers[i].value, sizeof(req->headers[i].value), "%s", value);
            return;
        }
    }
    if (req->header_count < MAX_HEADERS) {
        snprintf(req->headers[req->header_count].key, sizeof(req->headers[req->header_count].key), "%s", key);
        snprintf(req->headers[req->header_count].value, sizeof(req->headers[req->header_count].value), "%s", value);
        req->header_count++;
    }
}

const char* req_get_header(const http_request_t *req, const char *key) {
    for (size_t i = 0; i < req->header_count; ++i) {
        if (strcasecmp(req->headers[i].key, key) == 0) {
            return req->headers[i].value;
        }
    }
    return NULL;
}

bool auth_filter_process(http_request_t *req) {
    // Безпека: стираємо заголовок ідентичності, який клієнт міг підробити
    req_remove_header(req, "x-authenticated-user");
    req_remove_header(req, "x-tenant-id");

    const char *auth = req_get_header(req, "authorization");
    if (!auth || strncmp(auth, "Bearer ", 7) != 0) {
        return false;
    }

    const char *token = auth + 7;
    if (strcmp(token, "valid.jwt.token") != 0) {
        return false;
    }

    // Впорскуємо довірені дані про ідентичність для внутрішніх сервісів
    req_set_header(req, "x-authenticated-user", "usr_89412");
    req_set_header(req, "x-tenant-id", "tenant_eu_west");
    return true;
}

// ── 4. Маршрутизація та обробка запиту ─────────────────────────────────────
void gateway_handle_request(token_bucket_t *tb, http_request_t *req, http_response_t *resp) {
    memset(resp, 0, sizeof(*resp));

    // 1. Перевірка ліміту швидкості
    if (!token_bucket_try_acquire(tb, 1.0)) {
        resp->status = HTTP_TOO_MANY_REQUESTS;
        snprintf(resp->body, sizeof(resp->body), "{\"error\": \"Rate limit exceeded\"}");
        return;
    }

    // 2. Перевірка маршруту
    if (strncmp(req->path, "/api/v1/orders", 14) != 0) {
        resp->status = HTTP_NOT_FOUND;
        snprintf(resp->body, sizeof(resp->body), "{\"error\": \"Route not found\"}");
        return;
    }

    // 3. Автентифікація
    if (!auth_filter_process(req)) {
        resp->status = HTTP_UNAUTHORIZED;
        snprintf(resp->body, sizeof(resp->body), "{\"error\": \"Unauthorized\"}");
        return;
    }

    // 4. Успішне пересилання до бекенда
    resp->status = HTTP_OK;
    const char *user = req_get_header(req, "x-authenticated-user");
    snprintf(resp->body, sizeof(resp->body), "{\"status\": \"ok\", \"user\": \"%s\"}", user ? user : "unknown");
}

int main(void) {
    token_bucket_t tb;
    token_bucket_init(&tb, 10.0, 5.0);

    http_request_t req;
    memset(&req, 0, sizeof(req));
    snprintf(req.method, sizeof(req.method), "GET");
    snprintf(req.path, sizeof(req.path), "/api/v1/orders/5512");
    req_set_header(&req, "Authorization", "Bearer valid.jwt.token");
    req_set_header(&req, "X-Authenticated-User", "spoofed_attacker");

    http_response_t resp;
    gateway_handle_request(&tb, &req, &resp);

    printf("Response Code: %d\n", resp->status);
    printf("Response Body: %s\n", resp->body);

    return 0;
}
