#ifndef CDC_UART_H
#define CDC_UART_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file cdc_uart.h
 * @brief Заголовний файл модуля віртуального послідовного порту CDC UART
 *        з оголошеннями функцій буферизації та налаштування USART.
 */

/* Розмір кільцевих буферів (повинен бути ступенем двійки) */
#define CDC_UART_RING_BUF_SIZE 256U
#define CDC_UART_BUF_MASK      (CDC_UART_RING_BUF_SIZE - 1U)

/**
 * @brief Структура кільцевого буфера
 */
typedef struct {
    uint8_t data[CDC_UART_RING_BUF_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} ring_buffer_t;

/**
 * @brief Ініціалізація перифірійного модуля USART1 для роботи віртуального COM-порту.
 * 
 * @param baud_rate Швидкість передачі даних у бодах (наприклад, 115200).
 */
void cdc_uart_init(uint32_t baud_rate);

/**
 * @brief Запис байта в буфер передачі CDC UART.
 * 
 * @param byte Байт для відправки на ПК/цільовий пристрій.
 * @return true при успішному додаванні у буфер, false якщо буфер переповнений.
 */
bool cdc_uart_write_byte(uint8_t byte);

/**
 * @brief Читання байта з буфера прийому CDC UART.
 * 
 * @param byte Вказівник на змінну для запису збереженого байта.
 * @return true якщо байт прочитано, false якщо буфер порожній.
 */
bool cdc_uart_read_byte(uint8_t *byte);

/**
 * @brief Отримання кількості доступних байтів у приймальному буфері.
 * 
 * @return Кількість байтів, готових до зчитання.
 */
uint16_t cdc_uart_rx_available(void);

/**
 * @brief Очищення приймального та передавального буферів.
 */
void cdc_uart_flush(void);

/**
 * @brief Обробник переривання USART1_IRQHandler (викликається з векторної таблиці).
 */
void cdc_uart_irq_handler(void);

#endif /* CDC_UART_H */
