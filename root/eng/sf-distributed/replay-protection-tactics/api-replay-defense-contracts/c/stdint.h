#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <stddef.h>

typedef enum {
    DECISION_ALLOW_FIRST_TIME,
    DECISION_SERVE_CACHED_RESPONSE,
    DECISION_REJECT_DUPLICATE_IN_FLIGHT,
    DECISION_REJECT_EXPIRED_TIMESTAMP,
    DECISION_REJECT_INVALID_SIGNATURE,
    DECISION_REJECT_STALE_FENCING_TOKEN
} validation_decision_t;

typedef struct {
    const char* idempotency_key;
    const char* nonce;
    const char* signature;
    int64_t timestamp_ms;
    uint64_t fencing_token;
    const char* body;
    size_t body_len;
} request_context_t;

typedef struct {
    validation_decision_t decision;
    int http_status_code;
    const char* cached_payload;
    size_t cached_payload_len;
    char error_message[128];
} interceptor_result_t;

typedef struct replay_interceptor_vtable {
    interceptor_result_t (*pre_handle)(void* ctx, const request_context_t* req);
    void (*post_handle_success)(void* ctx, const char* idemp_key, int status, const char* resp, size_t resp_len);
    void (*post_handle_failure)(void* ctx, const char* idemp_key);
} replay_interceptor_vtable_t;

typedef struct {
    const replay_interceptor_vtable_t* vtable;
    void* impl_context;
} replay_interceptor_t;
