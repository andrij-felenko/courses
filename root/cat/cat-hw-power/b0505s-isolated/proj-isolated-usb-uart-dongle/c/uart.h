#ifndef UART_H
#define UART_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Ініціалізація апаратного модуля UART.
 * @param baudrate Швидкість передачі даних у бодах (115200).
 * @param f_cpu Тактова частота ядра мікроконтролера в Гц (16000000UL).
 */
void uart_init(uint32_t baudrate, uint32_t f_cpu);

/**
 * @brief Неблокуюча перевірка та зчитування прийнятого байта.
 * @param[out] byte Вказівник на змінну для збереження отриманого байта.
 * @return true якщо байт успішно зчитано з регістра прийому;
 *         false якщо буфер прийому порожній.
 */
bool uart_read_byte(uint8_t *byte);

/**
 * @brief Неблокуюча відправка байта у передавач.
 * @param byte Байт даних для передачі хосту.
 * @return true якщо байт успішно поміщено в регістр передавача;
 *         false якщо передавач зайнятий.
 */
bool uart_write_byte(uint8_t byte);

#endif /* UART_H */
