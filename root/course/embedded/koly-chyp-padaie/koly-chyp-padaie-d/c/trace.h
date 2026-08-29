#ifndef TRACE_H
#define TRACE_H

#include <stdint.h>

/*
 * Аварійний канал діагностики: USART2 (PA2 — TX, PA3 — RX), 115200 8N1.
 * Усі передавання — суто опитуванням прапорців, без переривань і без DMA:
 * друкувати доводиться з обробника HardFault, де решта системи вже мертва.
 */

void trace_init(void);

void trace_str(const char *text);
void trace_char(char c);

/* Друк 32-бітного значення у вигляді 0xXXXXXXXX. */
void trace_hex32(uint32_t value);

/* Рядок "name=0xXXXXXXXX\r\n" — основна форма аварійного звіту. */
void trace_kv(const char *name, uint32_t value);

/* Неблокуюче читання: -1, якщо байта немає. */
int trace_getc(void);

/* Дочекатися, доки останній байт фізично вийде з зсувного регістра. */
void trace_flush(void);

#endif /* TRACE_H */
