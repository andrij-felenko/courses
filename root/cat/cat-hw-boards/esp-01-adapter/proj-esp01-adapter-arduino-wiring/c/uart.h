#ifndef UART_H_
#define UART_H_

#include <stdint.h>
#include <stdbool.h>

// Розмірність кільцевих буферів (має бути ступенем двійки для ефективної обробки)
#define UART_RX_BUFFER_SIZE 64
#define UART_TX_BUFFER_SIZE 64

// Структура кільцевого буфера FIFO для обробки в перериваннях
typedef struct {
    volatile uint8_t buffer[UART_RX_BUFFER_SIZE];
    volatile uint8_t head;
    volatile uint8_t tail;
} ring_buffer_t;

/**
 * @brief Ініціалізація модуля USART мікроконтролера AVR.
 * @param baud Швидкість передачі даних у бодах (наприклад, 115200 для ESP-01).
 */
void uart_init(uint32_t baud);

/**
 * @brief Неблокувальне зчитування байта з кільцевого буфера приймача.
 * @param data Вказівник на змінну для збереження отриманого байта.
 * @return true якщо байт успішно прочитано, false якщо буфер порожній.
 */
bool uart_getc(uint8_t *data);

/**
 * @brief Неблокувальне додавання байта у кільцевий буфер передавача.
 * @param data Байт для надсилання.
 * @return true якщо байт додано в буфер, false якщо буфер переповнений.
 */
bool uart_putc(uint8_t data);

/**
 * @brief Передача нуль-термінованого рядка через UART.
 * @param str Вказівник на рядок для надсилання.
 */
void uart_puts(const char *str);

/**
 * @brief Перевірка наявності непрочитаних даних у буфері приймача.
 * @return true якщо в буфері є принаймні один байт, інакше false.
 */
bool uart_available(void);

#endif // UART_H_
