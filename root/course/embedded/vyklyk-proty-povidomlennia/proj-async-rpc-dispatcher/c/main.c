#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CORRELATOR_MAX_PENDING 8
#define CORRELATOR_INVALID_ID  0

typedef enum {
    CORR_STATUS_OK = 0,
    CORR_STATUS_TIMEOUT,
    CORR_STATUS_ERROR_REMOTE,
    CORR_STATUS_BUSY,
    CORR_STATUS_INVALID_ARG
} CorrStatus_t;

/* Опис відповіді віддаленого вузла */
typedef struct {
    uint16_t trans_id;
    CorrStatus_t status;
    const uint8_t *payload;
    size_t payload_len;
} CorrResponse_t;

/* Сигнатура функції зворотного виклику */
typedef void (*CorrCallback_t)(const CorrResponse_t *response, void *user_arg);

typedef enum {
    SLOT_FREE = 0,
    SLOT_PENDING
} SlotState_t;

typedef struct {
    SlotState_t state;
    uint16_t trans_id;
    uint32_t timeout_remaining_ms;
    CorrCallback_t callback;
    void *user_arg;
} PendingSlot_t;

typedef struct {
    PendingSlot_t slots[CORRELATOR_MAX_PENDING];
    uint16_t next_trans_id;
} AsyncCorrelator_t;

/* Ініціалізація структури корелятора */
void correlator_init(AsyncCorrelator_t *corr) {
    if (!corr) return;
    memset(corr, 0, sizeof(AsyncCorrelator_t));
    corr->next_trans_id = 1;
}

/* Генерація унікального ненульового Transaction ID з перевіркою зайнятості */
static uint16_t generate_unique_id(AsyncCorrelator_t *corr) {
    for (size_t attempts = 0; attempts < 65535; ++attempts) {
        uint16_t candidate = corr->next_trans_id++;
        if (corr->next_trans_id == CORRELATOR_INVALID_ID) {
            corr->next_trans_id = 1;
        }

        /* Перевіряємо, чи цей ID вже не зайнятий іншою довгою транзакцією */
        bool in_use = false;
        for (size_t i = 0; i < CORRELATOR_MAX_PENDING; ++i) {
            if (corr->slots[i].state == SLOT_PENDING && 
                corr->slots[i].trans_id == candidate) {
                in_use = true;
                break;
            }
        }

        if (!in_use) {
            return candidate;
        }
    }
    return CORRELATOR_INVALID_ID;
}

/* Реєстрація нового асинхронного запиту */
CorrStatus_t correlator_register_request(AsyncCorrelator_t *corr,
                                        uint32_t timeout_ms,
                                        CorrCallback_t callback,
                                        void *user_arg,
                                        uint16_t *out_trans_id) {
    if (!corr || !callback || !out_trans_id || timeout_ms == 0) {
        return CORR_STATUS_INVALID_ARG;
    }

    /* Пошук вільного слота у статичному масиві */
    for (size_t i = 0; i < CORRELATOR_MAX_PENDING; ++i) {
        if (corr->slots[i].state == SLOT_FREE) {
            uint16_t id = generate_unique_id(corr);
            if (id == CORRELATOR_INVALID_ID) {
                return CORR_STATUS_BUSY;
            }

            corr->slots[i].state = SLOT_PENDING;
            corr->slots[i].trans_id = id;
            corr->slots[i].timeout_remaining_ms = timeout_ms;
            corr->slots[i].callback = callback;
            corr->slots[i].user_arg = user_arg;

            *out_trans_id = id;
            return CORR_STATUS_OK;
        }
    }

    /* Всі слоти зайняті: зворотний тиск (Backpressure) */
    return CORR_STATUS_BUSY;
}

/* Маршрутизація вхідного кадру відповіді */
bool correlator_dispatch_response(AsyncCorrelator_t *corr,
                                  uint16_t trans_id,
                                  CorrStatus_t status,
                                  const uint8_t *payload,
                                  size_t payload_len) {
    if (!corr || trans_id == CORRELATOR_INVALID_ID) {
        return false;
    }

    for (size_t i = 0; i < CORRELATOR_MAX_PENDING; ++i) {
        if (corr->slots[i].state == SLOT_PENDING && 
            corr->slots[i].trans_id == trans_id) {
            
            CorrResponse_t resp = {
                .trans_id = trans_id,
                .status = status,
                .payload = payload,
                .payload_len = payload_len
            };

            CorrCallback_t cb = corr->slots[i].callback;
            void *arg = corr->slots[i].user_arg;

            /* Звільняємо слот ДО виклику callback */
            corr->slots[i].state = SLOT_FREE;

            if (cb) {
                cb(&resp, arg);
            }
            return true;
        }
    }

    /* Відповідь для невідомого або вже скасованого за таймаутом запиту */
    return false;
}

/* Періодичний тік таймера дедлайнів (наприклад, раз на 10 мс) */
void correlator_tick(AsyncCorrelator_t *corr, uint32_t elapsed_ms) {
    if (!corr || elapsed_ms == 0) return;

    for (size_t i = 0; i < CORRELATOR_MAX_PENDING; ++i) {
        if (corr->slots[i].state == SLOT_PENDING) {
            if (corr->slots[i].timeout_remaining_ms <= elapsed_ms) {
                CorrResponse_t timeout_resp = {
                    .trans_id = corr->slots[i].trans_id,
                    .status = CORR_STATUS_TIMEOUT,
                    .payload = NULL,
                    .payload_len = 0
                };

                CorrCallback_t cb = corr->slots[i].callback;
                void *arg = corr->slots[i].user_arg;

                corr->slots[i].state = SLOT_FREE;

                if (cb) {
                    cb(&timeout_resp, arg);
                }
            } else {
                corr->slots[i].timeout_remaining_ms -= elapsed_ms;
            }
        }
    }
}
