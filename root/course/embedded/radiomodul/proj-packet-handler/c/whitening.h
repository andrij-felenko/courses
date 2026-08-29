#ifndef WHITENING_H
#define WHITENING_H

#include <stddef.h>
#include <stdint.h>

/* Скремблер даних (Data Whitening) на 7-бітному LFSR з поліномом
   x^7 + x^4 + 1. Початкове заповнення 0x7F, період послідовності
   2^7 - 1 = 127 бітів. Операція самозворотна (A ^ B ^ B = A), тож той
   самий код служить і передавачу, і приймачу. */
#define LFSR_SEED 0x7Fu

typedef struct {
    uint8_t lfsr; /* сім молодших бітів; bit6 — старший розряд регістра */
} whitening_t;

void whitening_init(whitening_t *w);

/* Проганяє один байт крізь маску. Стан лишається в об'єкті: маска
   тече крізь увесь кадр підряд і НЕ починається наново на кожному байті. */
uint8_t whitening_byte(whitening_t *w, uint8_t byte);

/* Прохід по готовому буферу з чистого стану — зручно передавачу. */
void whitening_block(uint8_t *data, size_t len);

#endif /* WHITENING_H */
