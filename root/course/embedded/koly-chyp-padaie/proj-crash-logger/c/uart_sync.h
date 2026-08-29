// Синхронний UART без переривань і DMA — єдиний вивід, дозволений в аварійному
// обробнику: побайтовий запис у регістр даних із опитуванням прапорця готовності.
#ifndef UART_SYNC_H
#define UART_SYNC_H

#include <stdbool.h>
#include <stdint.h>

// pclk2_hz — частота шини APB2, на якій висить USART1.
void uart_sync_init(uint32_t pclk2_hz, uint32_t baud);

// Усі write повертають false, якщо передавач не звільнився за відведений час:
// в аварії гірше зависнути назавжди, ніж загубити рядок звіту.
bool uart_sync_write(const char *text);
bool uart_sync_write_n(const char *data, uint32_t len);

// Друк без printf: жодного форматування зі стеком і буферами на кілобайти.
bool uart_sync_hex32(uint32_t value);
bool uart_sync_dec(uint32_t value);
bool uart_sync_newline(void);

// Неблокуюче читання: false, якщо в приймачі нічого немає.
bool uart_sync_read(char *out);

#endif // UART_SYNC_H
