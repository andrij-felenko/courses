#ifndef AT_ENGINE_H
#define AT_ENGINE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "at_queue.h"
#include "at_ring.h"
#include "at_urc.h"

typedef enum {
    AT_STATE_IDLE = 0,           /* черга порожня */
    AT_STATE_SEND,               /* вибірка з черги й передача в UART TX */
    AT_STATE_WAIT_PROMPT,        /* очікування символу '>' перед сирими даними */
    AT_STATE_WAIT_RESPONSE,      /* розбір рядків відповіді */
    AT_STATE_RETRY_DELAY,        /* неблокуюча витримка перед повтором */
    AT_STATE_TIMEOUT_ESCALATION  /* модуль промовчав — аварійне відновлення */
} at_engine_state_t;

const char *at_state_str(at_engine_state_t state);

typedef struct {
    void     (*uart_tx)(const uint8_t *data, size_t len);
    uint32_t (*tick_ms)(void);
    /* Викликається, коли модуль не відповів AT_TIMEOUT_ESCALATION_LIMIT разів
       поспіль: місце для смикання PWRKEY або зняття живлення. Може бути NULL. */
    void     (*on_module_stuck)(void *ctx);
    void      *ctx;
} at_engine_hooks_t;

typedef struct {
    uint32_t lines_in;
    uint32_t urc_lines;
    uint32_t echo_dropped;
    uint32_t orphan_lines;   /* відповідь, що спізнилася після таймауту */
    uint32_t overflows;      /* рядок довший за AT_MAX_LINE_SIZE */
    uint32_t retries;
    uint32_t timeouts;
    uint32_t recoveries;
} at_engine_stats_t;

typedef struct {
    at_ring_t         rx;
    at_queue_t        queue;
    at_urc_table_t    urc;
    at_engine_hooks_t hooks;

    at_engine_state_t state;
    at_cmd_t          cmd;                  /* активна команда */
    uint32_t          timer_start_ms;
    char              resp_line[AT_MAX_LINE_SIZE];

    bool              echo_active;          /* модуль ще в режимі ATE1 */
    uint8_t           consecutive_timeouts;

    at_engine_stats_t stats;
} at_engine_t;

bool at_engine_init(at_engine_t *eng, const at_engine_hooks_t *hooks);

/* Куди націлити DMA й скільки байтів йому дати. */
static inline uint8_t *at_engine_rx_buffer(at_engine_t *eng) { return at_ring_dma_target(&eng->rx); }
static inline uint16_t at_engine_rx_size(void) { return at_ring_capacity(); }

bool at_engine_register_urc(at_engine_t *eng, const char *prefix,
                            at_urc_cb_t handler, void *ctx);

/* Ставить команду в чергу. Безпечно викликати з URC-колбеку.
   payload (для wait_prompt) мусить лишатися живим до виклику done. */
bool at_engine_send_cmd(at_engine_t *eng, const at_request_t *req);

/* Єдиний неблокуючий крок. dma_cndtr — вміст регістра лічильника DMA. */
void at_engine_poll(at_engine_t *eng, uint16_t dma_cndtr);

static inline bool at_engine_busy(const at_engine_t *eng) { return eng->state != AT_STATE_IDLE; }
static inline const at_engine_stats_t *at_engine_stats(const at_engine_t *eng) { return &eng->stats; }

#endif /* AT_ENGINE_H */
