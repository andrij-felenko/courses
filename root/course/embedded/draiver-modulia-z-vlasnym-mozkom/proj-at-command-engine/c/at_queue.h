#ifndef AT_QUEUE_H
#define AT_QUEUE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "at_config.h"

typedef enum {
    AT_STATUS_OK = 0,
    AT_STATUS_ERROR,    /* модуль відповів ERROR / +CME ERROR */
    AT_STATUS_TIMEOUT,  /* модуль промовчав */
    AT_STATUS_ABORTED   /* чергу скасовано під час аварійного відновлення */
} at_status_t;

const char *at_status_str(at_status_t status);

/* resp — останній змістовний рядок відповіді (той, що збігся з
   expect_prefix) або текст помилки; NULL для таймауту й скасування.
   Покажчик дійсний ЛИШЕ на час виклику. */
typedef void (*at_done_cb_t)(at_status_t status, const char *resp, void *ctx);

/* Заявка на команду. Заповнюється прикладним кодом, копіюється в чергу. */
typedef struct {
    const char    *text;           /* без '\r\n' — рушій допише сам */
    const char    *expect_prefix;  /* NULL, якщо даних не чекаємо */
    const uint8_t *payload;        /* сирі байти після запрошення '>' */
    uint16_t       payload_len;
    uint32_t       timeout_ms;
    uint8_t        retries;        /* лише для таймаутів і тимчасових помилок */
    bool           wait_prompt;
    at_done_cb_t   done;
    void          *ctx;
} at_request_t;

/* Те саме, але вже всередині черги: текст скопійовано, лічильник спроб живий. */
typedef struct {
    char           text[AT_MAX_CMD_SIZE];
    char           expect_prefix[AT_MAX_PREFIX_SIZE];
    const uint8_t *payload;
    uint16_t       payload_len;
    uint32_t       timeout_ms;
    uint8_t        max_retries;
    uint8_t        attempt;
    bool           wait_prompt;
    at_done_cb_t   done;
    void          *ctx;
} at_cmd_t;

typedef struct {
    at_cmd_t item[AT_QUEUE_CAPACITY];
    uint8_t  head;
    uint8_t  tail;
    uint8_t  count;
} at_queue_t;

void at_queue_init(at_queue_t *q);

/* Копіює заявку в чергу під критичною секцією: класти команду можуть із
   URC-колбеку й з переривання. Повертає false, якщо черга повна або текст
   довший за AT_MAX_CMD_SIZE — мовчазне обрізання команди гірше за відмову. */
bool at_queue_push(at_queue_t *q, const at_request_t *req);

bool at_queue_pop(at_queue_t *q, at_cmd_t *out);

static inline uint8_t at_queue_count(const at_queue_t *q) { return q->count; }
static inline bool at_queue_empty(const at_queue_t *q) { return q->count == 0U; }

#endif /* AT_QUEUE_H */
