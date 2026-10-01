#ifndef UART_H
#define UART_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file uart.h
 * @brief Драйвер апаратного модуля UART для зв'язку через міст CH340 USB-UART.
 */

/**
 * @brief Ініціалізує апаратний модуль UART мікроконтролера.
 * 
 * Налаштовує швидкість передачі (baud rate), формат кадру (8 data bits, 1 stop bit, no parity)
 * та вмикає модулі приймача (RX) і передавача (TX).
 * 
 * @param baud_rate Необхідна швидкість обміну даними в бодах (наприклад, 9600 або 115200).
 */
void uart_init(uint32_t baud_rate);

/**
 * @brief Перевіряє, чи є доступні вхідні байти у приймальному регістрі UART.
 * 
 * @return true, якщо байт отримано і він готовий до зчитання, інакше false.
 */
bool uart_is_data_available(void);

/**
 * @brief Синхронно (блокуюче) зчитує один байт з UART.
 * 
 * Очікує на надходження даних від CH340 у нескінченному циклі.
 * 
 * @return Отриманий байт.
 */
uint8_t uart_receive_byte(void);

/**
 * @brief Спроба неблокуючого зчитування байта з UART.
 * 
 * @param out_data Вказівник на змінну для збереження отриманого байта.
 * @return true, якщо байт успішно зчитано, false якщо даних немає.
 */
bool uart_receive_byte_nonblocking(uint8_t *out_data);

/**
 * @brief Передає один байт через UART до мікросхеми CH340.
 * 
 * @param data Байт для відправки.
 */
void uart_send_byte(uint8_t data);

/**
 * @brief Передає нуль-термінований рядок через UART.
 * 
 * @param str Вказівник на C-рядок для відправлення.
 */
void uart_send_string(const char *str);

#endif /* UART_H */
