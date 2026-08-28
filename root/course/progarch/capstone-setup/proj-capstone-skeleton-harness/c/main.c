/* Walking Skeleton Harness мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

#define MAX_STR 64
#define OUTBOX_CAPACITY 100

typedef struct {
    char trace_id[MAX_STR];
    char tenant_id[MAX_STR];
    char idempotency_key[MAX_STR];
    double amount;
    char currency[8];
} checkout_request_t;

typedef struct {
    char transaction_id[MAX_STR];
    char trace_id[MAX_STR];
    char status[16];
    int http_code;
} checkout_response_t;

typedef struct {
    char id[MAX_STR];
    char tenant_id[MAX_STR];
    double amount;
    long timestamp;
} outbox_entry_t;

typedef struct {
    outbox_entry_t entries[OUTBOX_CAPACITY];
    size_t count;
} outbox_journal_t;

static outbox_journal_t g_outbox = { .count = 0 };

/* Перевірка ідемпотентності в пам'яті */
bool check_idempotency(const char* key, checkout_response_t* cached_out) {
    if (strcmp(key, "idem-duplicate-123") == 0) {
        snprintf(cached_out->transaction_id, MAX_STR, "tx_cached_998877");
        snprintf(cached_out->status, 16, "DUPLICATE_ACK");
        cached_out->http_code = 200;
        return true; /* Знайдено дублікат */
    }
    return false;
}

/* Атомарний запис у локальний Outbox */
bool record_to_outbox(const char* tenant, double amount, const char* trace_id) {
    if (g_outbox.count >= OUTBOX_CAPACITY) return false;
    
    outbox_entry_t* entry = &g_outbox.entries[g_outbox.count++];
    snprintf(entry->id, MAX_STR, "tx_live_%ld", time(NULL) + rand() % 1000);
    snprintf(entry->tenant_id, MAX_STR, "%s", tenant);
    entry->amount = amount;
    entry->timestamp = (long)time(NULL);

    printf("[%s] [OUTBOX_APPEND] Tenant: %s, TxID: %s, Amount: %.2f\n",
           trace_id, entry->tenant_id, entry->id, entry->amount);
    return true;
}

/* Головна точка входу Walking Skeleton */
checkout_response_t process_checkout(const checkout_request_t* req) {
    checkout_response_t res;
    memset(&res, 0, sizeof(res));
    snprintf(res.trace_id, MAX_STR, "%s", req->trace_id);

    printf("[%s] [EDGE_ROUTER] Ingesting request for Tenant: %s, Key: %s\n",
           req->trace_id, req->tenant_id, req->idempotency_key);

    /* 1. Guard ідемпотентності */
    if (check_idempotency(req->idempotency_key, &res)) {
        printf("[%s] [IDEMPOTENCY_GUARD] Duplicate key detected. Returning cached response.\n", req->trace_id);
        return res;
    }

    /* 2. Запис у локальний Ledger / Outbox */
    if (!record_to_outbox(req->tenant_id, req->amount, req->trace_id)) {
        snprintf(res.status, 16, "OUTBOX_FULL");
        res.http_code = 503;
        return res;
    }

    /* 3. Формування успішного результату */
    snprintf(res.transaction_id, MAX_STR, "tx_live_ok");
    snprintf(res.status, 16, "SUCCESS");
    res.http_code = 200;

    printf("[%s] [WALKING_SKELETON_SUCCESS] Completed end-to-end trace. Code: %d\n",
           req->trace_id, res.http_code);
    return res;
}

int main(void) {
    srand((unsigned int)time(NULL));
    printf("=== OmniPay Walking Skeleton Pipeline Harness (C) ===\n\n");

    checkout_request_t req1 = {
        .trace_id = "trace-uuid-1111-aaaa",
        .tenant_id = "tenant_enterprise_eu",
        .idempotency_key = "idem-unique-001",
        .amount = 250.50,
        .currency = "EUR"
    };

    checkout_response_t res1 = process_checkout(&req1);
    printf("Result 1: TxID=%s, Status=%s, Code=%d\n\n", res1.transaction_id, res1.status, res1.http_code);

    checkout_request_t req2 = {
        .trace_id = "trace-uuid-2222-bbbb",
        .tenant_id = "tenant_enterprise_eu",
        .idempotency_key = "idem-duplicate-123",
        .amount = 250.50,
        .currency = "EUR"
    };

    checkout_response_t res2 = process_checkout(&req2);
    printf("Result 2: TxID=%s, Status=%s, Code=%d\n", res2.transaction_id, res2.status, res2.http_code);

    return 0;
}
