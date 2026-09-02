#ifndef SUPERLOOP_DISPLAY_H
#define SUPERLOOP_DISPLAY_H

#include <stdbool.h>
#include <stdint.h>

bool display_init(void);
void display_clear(void);

/* Малює число у кадровий буфер; decimals — скільки останніх цифр після коми. */
void display_number(uint8_t x, uint8_t page, int32_t value, uint8_t decimals);

/* Горизонтальна смуга від lo до hi — шкала без шрифту. */
void display_bar(uint8_t page, int32_t value, int32_t lo, int32_t hi);

/* Блокуючий вивід усього кадру на шину. Саме тут цикл і стоїть. */
bool display_flush(void);

#endif /* SUPERLOOP_DISPLAY_H */
