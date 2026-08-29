#ifndef EDGE_RING_BUFFER_H
#define EDGE_RING_BUFFER_H

#include <stdint.h>

/* Глибина передісторії. 32 вибірки на 100 Гц — це 0.32 с сигналу ДО аварії:
   саме той шматок, якого ніколи немає в логах, коли аварія вже сталася.
   Степінь двійки навмисно: компілятор зверне % у побітове І. */
#define RING_BUFFER_CAPACITY 32u

typedef struct {
    float    data[RING_BUFFER_CAPACITY];
    uint32_t head;    /* індекс, куди ляже наступна вибірка */
    uint32_t count;   /* скільки вибірок уже лежить, не більше за CAPACITY */
} ring_buffer_t;

void ring_buffer_clear(ring_buffer_t *rb);

/* Пише вибірку, найстарішу витісняє. Перезапис — штатний режим. */
void ring_buffer_push(ring_buffer_t *rb, float sample);

/* Розгортає кільце в лінійний масив від НАЙСТАРІШОЇ вибірки до найновішої.
   Повертає, скільки насправді скопійовано (не більше за count і dest_len). */
uint32_t ring_buffer_copy(const ring_buffer_t *rb, float *dest, uint32_t dest_len);

#endif /* EDGE_RING_BUFFER_H */
