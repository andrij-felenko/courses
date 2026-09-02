#ifndef ETH_DMA_H
#define ETH_DMA_H

#include <stdbool.h>
#include <stdint.h>

#include "lwip/pbuf.h"

/* Скільки дескрипторів у кільцях. Кожен RX-дескриптор ПОСТІЙНО тримає один
   pbuf з PBUF_POOL, тож ці числа — прямий відрахунок від бюджету RAM:
   4 + 4 буфери по 1536 байтів це вже 12 КБ, які пул ніколи не віддасть назад. */
#define ETH_RX_DESC_COUNT   4
#define ETH_TX_DESC_COUNT   4

/* Розмір буфера прийому мусить точно збігатися з PBUF_POOL_BUFSIZE із lwipopts.h.
   Менший PBUF_POOL_BUFSIZE — і pbuf_alloc віддасть ЛАНЦЮЖОК ланок, а дескриптор
   уміє тримати лише один суцільний буфер: zero-copy на цьому й закінчується. */
#define ETH_RX_BUF_SIZE     1536

/* Довжина кеш-лінії D-Cache на Cortex-M7. Усе, що бачить DMA, вирівняне по ній. */
#define ETH_CACHE_LINE      32

/* Будує обидва кільця, розвішує на них буфери з PBUF_POOL і запускає DMA.
   Викликається ПІСЛЯ ініціалізації MAC/PHY (тактування, RMII, MDIO, автопере-
   говори) — сюди належить лише прив'язка дескрипторів до пам'яті. */
bool eth_dma_init(void);

/* Знімає з кільця наступний прийнятий кадр. NULL — кадрів немає.
   Повернений pbuf уже НЕ належить дескриптору: звільняє його той, хто взяв. */
struct pbuf *eth_dma_rx_receive(void);

/* Ставить кадр (можливо, ланцюжок pbuf) у кільце передачі без копіювання. */
bool eth_dma_tx_send(struct pbuf *p);

/* Віддає в пул буфери, які DMA вже відправив. Кличеться з контексту ЗАДАЧІ. */
void eth_dma_tx_reclaim(void);

#endif /* ETH_DMA_H */
