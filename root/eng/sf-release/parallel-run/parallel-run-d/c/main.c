#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    char order_id[64];
    char user_id[64];
    long long amount_cents;
} OrderRequest;

typedef struct {
    char order_id[64];
    char status[32];
    long long balance_after;
    bool success;
} OrderResponse;

typedef OrderResponse (*ProcessorFn)(const OrderRequest*, void* context);
typedef void (*DiffLoggerFn)(const char* order_id, const OrderResponse* master, const OrderResponse* cand);

typedef struct {
    ProcessorFn master_fn;
    void* master_ctx;
    ProcessorFn candidate_fn;
    void* candidate_ctx;
    DiffLoggerFn diff_fn;
} DualRunDispatcherC;

OrderResponse dual_run_process(DualRunDispatcherC* d, const OrderRequest* req) {
    /* 1. Авторитетне виконання на майстрі */
    OrderResponse master_res = d->master_fn(req, d->master_ctx);
    if (!master_res.success) {
        return master_res;
    }

    /* 2. Тіньове виконання кандидата */
    OrderResponse cand_res = d->candidate_fn(req, d->candidate_ctx);
    if (cand_res.success) {
        /* Звірка ключових бізнес-інваріантів */
        if (master_res.balance_after != cand_res.balance_after ||
            strcmp(master_res.status, cand_res.status) != 0) {
            if (d->diff_fn) {
                d->diff_fn(req->order_id, &master_res, &cand_res);
            }
        }
    }

    /* Завжди повертаємо відповідь майстра */
    return master_res;
}
