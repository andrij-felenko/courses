#ifndef LWIP_DIAG_H
#define LWIP_DIAG_H

/* Знімок підсистеми lwip_stats: скільки блоків у кожному пулі зайнято,
 * який був пік від старту й скільки разів пул відмовив. Це єдиний спосіб
 * дізнатися, чому з'єднання «зависає» на робочій платі без відлагоджувача. */

#include "lwip/opt.h"
#include "lwip/stats.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Пули, за якими стежимо. Більше сімох у цій конфігурації не буває. */
#define LWIP_DIAG_MAX_POOLS 7

typedef enum {
  LWIP_DIAG_POOL_PBUF_POOL = 0, /* вхідні кадри від DMA */
  LWIP_DIAG_POOL_PBUF,          /* PBUF_ROM/PBUF_REF на передачі */
  LWIP_DIAG_POOL_TCP_PCB,       /* активні з'єднання */
  LWIP_DIAG_POOL_TCP_LISTEN,    /* слухачі портів */
  LWIP_DIAG_POOL_TCP_SEG,       /* дескриптори черги відправлення */
  LWIP_DIAG_POOL_UDP_PCB,
  LWIP_DIAG_POOL_NETCONN
} lwip_diag_pool_id_t;

typedef enum {
  LWIP_DIAG_HEALTHY = 0,
  LWIP_DIAG_RX_POOL_STARVED,   /* кадри відкидаються ще до входу в стек */
  LWIP_DIAG_HEAP_EXHAUSTED,    /* MEM_SIZE замалий або фрагментований */
  LWIP_DIAG_SEGS_EXHAUSTED,    /* черга TX упирається в MEMP_NUM_TCP_SEG */
  LWIP_DIAG_SOCKETS_EXHAUSTED  /* пік дійшов до стелі MEMP_NUM_TCP_PCB */
} lwip_diag_verdict_t;

typedef struct {
  lwip_diag_pool_id_t id;
  const char *name;
  u32_t avail;    /* скільки блоків (для купи — байтів) є всього */
  u32_t used;     /* зайнято на момент знімка */
  u32_t peak;     /* пік від старту системи: поле max у stats_mem */
  u32_t failures; /* поле err: скільки разів виділення не вдалося */
} lwip_diag_pool_t;

typedef struct {
  lwip_diag_pool_t pools[LWIP_DIAG_MAX_POOLS];
  u8_t pool_count;
  lwip_diag_pool_t heap; /* купа mem.c, лічильники в байтах */
  lwip_diag_verdict_t verdict;
} lwip_diag_report_t;

/* Знімає стан пулів. Повертає 0, або -1, якщо статистику вимкнено
 * в lwipopts.h чи передано NULL. Бере core-lock, тож викликати можна
 * з будь-якої задачі, крім самої tcpip_thread. */
int lwip_diag_collect(lwip_diag_report_t *report);

/* Друкує таблицю пулів і присуд. NULL терпить мовчки. */
void lwip_diag_print(const lwip_diag_report_t *report);

const char *lwip_diag_verdict_str(lwip_diag_verdict_t verdict);

/* Повний дамп: наша таблиця плюс рідний stats_display(), якщо він увімкнений. */
void lwip_diag_dump(void);

#ifdef __cplusplus
}
#endif

#endif /* LWIP_DIAG_H */
