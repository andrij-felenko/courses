#ifndef MODEM_SIM_H
#define MODEM_SIM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "at_config.h"

/* Симулятор смарт-модуля з боку дроту.

   Він потрібен, щоб рушій можна було ганяти без заліза, і навмисно поводиться
   так само паскудно, як справжній модем: віддає луну, розриває довгу відповідь
   на два кадри, відповідає "+CME ERROR: 14" з першого разу, вимагає запрошення
   '>' перед сирими даними й іноді мовчить зовсім. Байти він кладе просто в
   масив приймача — рівно те, що робить контролер DMA. */

#define SIM_OUT_CAP   8U
#define SIM_TEXT_CAP  96U

typedef struct {
    char     text[SIM_TEXT_CAP];
    uint16_t len;
    uint16_t sent;
    uint16_t chunk;    /* 0 — віддати цілком, інакше стільки байтів за раз */
    uint32_t gap_ms;   /* пауза між шматками */
    uint32_t due_ms;
} sim_out_t;

typedef struct {
    uint8_t *dma_dst;      /* той самий масив, що бачить кільцевий буфер */
    uint16_t head;         /* апаратний покажчик запису */

    sim_out_t out[SIM_OUT_CAP];
    uint8_t   out_head;
    uint8_t   out_tail;
    uint8_t   out_count;
    uint32_t  dropped;     /* скільки відповідей не влізло в чергу симулятора */

    char     rx_line[AT_MAX_LINE_SIZE];
    uint16_t rx_len;

    bool     echo;
    uint8_t  cfun_attempts;

    bool     await_payload;
    uint16_t payload_expect;
    uint16_t payload_got;

    bool     urc_closed_done;
    bool     urc_ring_done;
} modem_sim_t;

void modem_sim_init(modem_sim_t *sim, uint8_t *dma_dst);

/* Скільки байтів DMA ще НЕ передав — саме це лежить у DMA_CNDTR. */
static inline uint16_t modem_sim_cndtr(const modem_sim_t *sim)
{
    return (uint16_t)(AT_RX_BUFFER_SIZE - sim->head);
}

/* Перехоплення передачі: сюди приходить усе, що рушій пише в UART TX. */
void modem_sim_on_tx(modem_sim_t *sim, const uint8_t *data, size_t len, uint32_t now);

/* Крок часу: віддає в «ефір» те, чому настав час. */
void modem_sim_tick(modem_sim_t *sim, uint32_t now);

#endif /* MODEM_SIM_H */
