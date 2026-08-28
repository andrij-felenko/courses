#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PENDING_REQUESTS 4

typedef enum {
    RPC_EVT_SUCCESS = 0,
    RPC_EVT_TIMEOUT,
    RPC_EVT_REMOTE_ERROR
} RpcEventStatus_t;

/* Структура результату відповіді */
typedef struct {
    uint16_t trans_id;
    RpcEventStatus_t status;
    const uint8_t *data;
    size_t length;
} RpcAsyncResult_t;

/* Сигнатура користувацького callback */
typedef void (*RpcCallback_t)(const RpcAsyncResult_t *result, void *context);

typedef struct {
    bool in_use;
    uint16_t trans_id;
    uint32_t timeout_ms;
    RpcCallback_t callback;
    void *context;
} RpcSlot_t;

typedef struct {
    RpcSlot_t pool[MAX_PENDING_REQUESTS];
    uint16_t id_counter;
} AsyncRpcEngine_t;

void rpc_engine_init(AsyncRpcEngine_t *engine) {
    memset(engine, 0, sizeof(AsyncRpcEngine_t));
    engine->id_counter = 1;
}

/* Асинхронний виклик: повертає ID транзакції або 0, якщо немає слотів */
uint16_t rpc_call_async(AsyncRpcEngine_t *engine, 
                        uint32_t timeout_ms, 
                        RpcCallback_t cb, 
                        void *ctx) {
    if (!engine || !cb) return 0;

    for (size_t i = 0; i < MAX_PENDING_REQUESTS; ++i) {
        if (!engine->pool[i].in_use) {
            uint16_t tid = engine->id_counter++;
            if (engine->id_counter == 0) engine->id_counter = 1;

            engine->pool[i].in_use = true;
            engine->pool[i].trans_id = tid;
            engine->pool[i].timeout_ms = timeout_ms;
            engine->pool[i].callback = cb;
            engine->pool[i].context = ctx;

            /* Тут формується і відправляється фізичний кадр у чергу TX */
            return tid;
        }
    }
    return 0; /* Пул переповнений: зворотний тиск */
}

/* Обробник вхідного кадру відповіді з послідовного порту */
void rpc_on_rx_frame(AsyncRpcEngine_t *engine, 
                     uint16_t trans_id, 
                     const uint8_t *payload, 
                     size_t len) {
    if (!engine || trans_id == 0) return;

    for (size_t i = 0; i < MAX_PENDING_REQUESTS; ++i) {
        if (engine->pool[i].in_use && engine->pool[i].trans_id == trans_id) {
            RpcAsyncResult_t res = {
                .trans_id = trans_id,
                .status = RPC_EVT_SUCCESS,
                .data = payload,
                .length = len
            };

            RpcCallback_t cb = engine->pool[i].callback;
            void *ctx = engine->pool[i].context;

            /* Звільняємо слот перед викликом, щоб уникнути блокування */
            engine->pool[i].in_use = false;

            if (cb) {
                cb(&res, ctx);
            }
            return;
        }
    }
}

/* Періодичне обслуговування дедлайнів (виклик раз на 10 мс) */
void rpc_engine_poll_timeouts(AsyncRpcEngine_t *engine, uint32_t step_ms) {
    if (!engine) return;

    for (size_t i = 0; i < MAX_PENDING_REQUESTS; ++i) {
        if (engine->pool[i].in_use) {
            if (engine->pool[i].timeout_ms <= step_ms) {
                RpcAsyncResult_t timeout_res = {
                    .trans_id = engine->pool[i].trans_id,
                    .status = RPC_EVT_TIMEOUT,
                    .data = NULL,
                    .length = 0
                };

                RpcCallback_t cb = engine->pool[i].callback;
                void *ctx = engine->pool[i].context;
                engine->pool[i].in_use = false;

                if (cb) {
                    cb(&timeout_res, ctx);
                }
            } else {
                engine->pool[i].timeout_ms -= step_ms;
            }
        }
    }
}
