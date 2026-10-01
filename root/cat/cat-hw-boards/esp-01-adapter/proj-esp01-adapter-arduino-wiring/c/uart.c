#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdbool.h>
#include "uart.h"

// Статичні кільцеві буфери приймання та передачі
static ring_buffer_t rx_buffer = {{0}, 0, 0};
static ring_buffer_t tx_buffer = {{0}, 0, 0};

void uart_init(uint32_t baud) {
    // Обчислення значення UBRR з округленням для заданої частоти F_CPU та швидкості baud
    uint16_t ubrr_value = (uint16_t)((F_CPU + 8UL * baud) / (16UL * baud) - 1);

    // Встановлення регістра дільника швидкості UBRR0 (H та L)
    UBRR0H = (uint8_t)(ubrr_value >> 8);
    UBRR0L = (uint8_t)(ubrr_value);

    // Увімкнення приймача (RXEN0), передавача (TXEN0) та переривання по приймання (RXCIE0)
    UCSR0B = (1 << RXCIE0) | (1 << RXEN0) | (1 << TXEN0);

    // Конфігурація кадру: 8 біт даних, 1 стоп-біт, без контролю парності (8N1)
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

bool uart_getc(uint8_t *data) {
    // Перевірка порожнечі буфера
    if (rx_buffer.head == rx_buffer.tail) {
        return false;
    }

    *data = rx_buffer.buffer[rx_buffer.tail];
    rx_buffer.tail = (rx_buffer.tail + 1) % UART_RX_BUFFER_SIZE;
    return true;
}

bool uart_available(void) {
    return (rx_buffer.head != rx_buffer.tail);
}

bool uart_putc(uint8_t data) {
    uint8_t next_head = (tx_buffer.head + 1) % UART_TX_BUFFER_SIZE;

    // Перевірка переповнення буфера передачі
    if (next_head == tx_buffer.tail) {
        return false;
    }

    tx_buffer.buffer[tx_buffer.head] = data;
    tx_buffer.head = next_head;

    // Увімкнення переривання по порожньому регістру даних UDR0 (UDRIE0)
    // Це спонукає контролер викликати ISR(USART_UDRE_vect) для передачі байтів з буфера
    UCSR0B |= (1 << UDRIE0);

    return true;
}

void uart_puts(const char *str) {
    while (*str) {
        // Очікування вільного місця у буфері передачі
        while (!uart_putc((uint8_t)*str)) {
            // Зачекати, поки переривання UDRE звільнить місце
        }
        str++;
    }
}

/**
 * @brief Обробник переривання приймання нового байта через USART.
 * Викликається апаратно, коли новий байт надходить у регістр UDR0.
 */
ISR(USART_RX_vect) {
    uint8_t received_byte = UDR0;
    uint8_t next_head = (rx_buffer.head + 1) % UART_RX_BUFFER_SIZE;

    // Збереження байта, якщо буфер не переповнено
    if (next_head != rx_buffer.tail) {
        rx_buffer.buffer[rx_buffer.head] = received_byte;
        rx_buffer.head = next_head;
    }
}

/**
 * @brief Обробник переривання готовності регістра даних USART (UDRE).
 * Викликається апаратно, коли регістр UDR0 готовий прийняти наступний байт для надсилання.
 */
ISR(USART_UDRE_vect) {
    if (tx_buffer.head != tx_buffer.tail) {
        // Передача наступного байта з кільцевого буфера
        UDR0 = tx_buffer.buffer[tx_buffer.tail];
        tx_buffer.tail = (tx_buffer.tail + 1) % UART_TX_BUFFER_SIZE;
    } else {
        // Якщо буфер порожній — вимикаємо переривання UDRE для запобігання зацикленню
        UCSR0B &= ~(1 << UDRIE0);
    }
}
