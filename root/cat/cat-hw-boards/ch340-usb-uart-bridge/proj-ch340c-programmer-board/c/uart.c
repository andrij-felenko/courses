#include "uart.h"
#include <avr/io.h>

/* Робоча частота тактування мікроконтролера за замовчуванням (16 МГц) */
#ifndef F_CPU
#define F_CPU 16000000UL
#endif

void uart_init(uint32_t baud_rate) {
    /* Обчислення значення прескалера для регістру швидкості UBRR (розмір кадру в режимі 16x) */
    uint16_t ubrr_value = (uint16_t)((F_CPU / (16UL * baud_rate)) - 1);

    /* Запис старшого та молодшого байтів значення UBRR */
    UBRR0H = (uint8_t)(ubrr_value >> 8);
    UBRR0L = (uint8_t)(ubrr_value);

    /* Дозвіл роботи приймача (RXEN0) та передавача (TXEN0) */
    UCSR0B = (1 << RXEN0) | (1 << TXEN0);

    /* Налаштування формату кадру: 8 біт даних, 1 стоп-біт, без парності (8N1) */
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

bool uart_is_data_available(void) {
    /* Прапорець RXC0 встановлюється в 1, коли є незчитані дані в регістрі UDR0 */
    return (UCSR0A & (1 << RXC0)) != 0;
}

uint8_t uart_receive_byte(void) {
    /* Очікування завершення прийому байта від мікросхеми CH340 */
    while (!uart_is_data_available()) {
        /* Блокуюче очікування прапорця RXC0 */
    }
    
    /* Зчитання байта з буферного регістру даних UDR0 */
    return UDR0;
}

bool uart_receive_byte_nonblocking(uint8_t *out_data) {
    if (out_data == NULL) {
        return false;
    }

    if (!uart_is_data_available()) {
        return false;
    }

    *out_data = UDR0;
    return true;
}

void uart_send_byte(uint8_t data) {
    /* Очікування звільнення буфера передачі (прапорець UDRE0) */
    while (!(UCSR0A & (1 << UDRE0))) {
        /* Блокуюче очікування готовності регістру UDR0 */
    }

    /* Запис байта в регістр UDR0 для автоматичної відправки через TXD до CH340 */
    UDR0 = data;
}

void uart_send_string(const char *str) {
    if (str == NULL) {
        return;
    }

    while (*str != '\0') {
        uart_send_byte((uint8_t)*str);
        str++;
    }
}
