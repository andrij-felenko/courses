#ifndef UART_H
#define UART_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Значення швидкості за замовчуванням для віртуального послідовного порту
#define UART_DEFAULT_BAUDRATE 115200U

// Ініціалізація модуля UART та підготовка виводів GPIO
void uart_init(uint32_t baudrate);

// Відправка одного символу через апаратний регістр даних
void uart_send_char(char c);

// Відправка нуль-термінованого текстового рядка
void uart_send_string(const char *str);

// Відправка сирого буфера даних вказаної довжини
void uart_send_buffer(const uint8_t *data, size_t length);

// Неблокувальне читання символу з буфера прийому UART
bool uart_receive_char(char *out_c);

#endif // UART_H
