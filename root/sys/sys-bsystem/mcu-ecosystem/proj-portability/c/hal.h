// hal.h — єдиний заголовок, що бачить прикладна логіка
#pragma once
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Записати логічний рівень у ніжку
void hal_gpio_write(uint8_t pin, bool on);

// Надіслати рядок у UART (нуль-термінований)
void hal_uart_puts(const char* s);

// Призупинити виконання на ms мілісекунд
void hal_delay_ms(uint32_t ms);

// Повернути кількість мілісекунд від старту
uint32_t hal_millis(void);

#ifdef __cplusplus
}
#endif
