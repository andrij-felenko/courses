#ifndef UART_HAL_H
#define UART_HAL_H

#include <stdint.h>
#include <stdbool.h>

// Приклад того, які функції має реалізувати користувач для своєї платформи
void platform_uart_write(const uint8_t *data, uint16_t len);
bool platform_uart_read_char(uint8_t *c);
uint32_t platform_get_tick_ms(void);

#endif // UART_HAL_H
