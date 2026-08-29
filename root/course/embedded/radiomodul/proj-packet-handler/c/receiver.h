#ifndef RECEIVER_H
#define RECEIVER_H

#include <stdbool.h>
#include <stdint.h>

#include "packet.h"
#include "whitening.h"

/* Скільки чергувань 0/1 треба побачити, щоб узагалі ввімкнути корелятор
   синхрослова. Апаратний аналог — Preamble Detect / Carrier Sense. */
#define PREAMBLE_DETECT_BITS 16
/* Вікно пошуку синхрослова після преамбули; вийшло — роззброюємось. */
#define SYNC_SEARCH_BITS 256
/* Глибина пакетного FIFO трансивера. */
#define RX_FIFO_DEPTH 2

typedef struct {
    uint32_t arms;     /* спрацювань детектора преамбули */
    uint32_t syncs;    /* спрацювань корелятора синхрослова */
    uint32_t good;     /* кадрів із правильним CRC */
    uint32_t crc_errs; /* кадрів, відкинутих по CRC */
    uint32_t len_errs; /* неможлива довжина в заголовку */
    uint32_t overruns; /* кадрів, загублених через переповнення FIFO */
} rx_stats_t;

typedef struct {
    /* --- бітовий рівень --- */
    uint32_t shift;       /* зсувний регістр корелятора */
    uint16_t alt_run;     /* довжина поточної серії чергувань 0/1 */
    uint16_t search_left; /* скільки бітів вікна пошуку лишилось */
    uint8_t  last_bit;
    bool     armed;

    /* --- байтовий рівень --- */
    uint8_t byte_acc;
    uint8_t bit_count;

    /* --- кадровий автомат --- */
    int         state;
    whitening_t w;
    uint16_t    crc;
    uint8_t     need; /* скільки байтів даних обіцяв заголовок */
    uint8_t     body[PACKET_MAX_PAYLOAD];
    uint8_t     body_pos;
    uint8_t     crc_rx[2];
    uint8_t     crc_pos;

    /* --- пакетний FIFO --- */
    packet_t fifo[RX_FIFO_DEPTH];
    uint8_t  head;
    uint8_t  count;
    bool     overrun;

    rx_stats_t stats;
} receiver_t;

void receiver_init(receiver_t *rx);

/* Приймач їсть саме БІТИ: межі байта в ефірі не існує, її створює
   лише строб корелятора. */
void receiver_push_bit(receiver_t *rx, uint8_t bit);
void receiver_push_byte_msb(receiver_t *rx, uint8_t byte);

/* Забирає найстаріший кадр із FIFO; false — FIFO порожній. */
bool receiver_pop(receiver_t *rx, packet_t *out);
bool receiver_overrun(const receiver_t *rx);

/* Строб CMD_FLUSHRX: скидає FIFO, ознаку переповнення й кадровий автомат. */
void receiver_flush(receiver_t *rx);

#endif /* RECEIVER_H */
