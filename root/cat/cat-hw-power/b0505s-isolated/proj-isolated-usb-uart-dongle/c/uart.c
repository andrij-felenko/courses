#include "uart.h"

#if defined(__AVR__)
#include <avr/io.h>
#else
/* Автономна модель регістрів для збірки та тестування на хості */
typedef struct {
    volatile uint8_t ucsra;
    volatile uint8_t ucsrb;
    volatile uint8_t ucsrc;
    volatile uint8_t reserved;
    volatile uint8_t ubrrl;
    volatile uint8_t ubrrh;
    volatile uint8_t udr;
} HardwareUart;

static HardwareUart sim_uart = {
    .ucsra = (1 << 5) /* UDRE0 прапорець готовності передавача */
};

#define UCSR0A (sim_uart.ucsra)
#define UCSR0B (sim_uart.ucsrb)
#define UCSR0C (sim_uart.ucsrc)
#define UBRR0H (sim_uart.ubrrh)
#define UBRR0L (sim_uart.ubrrl)
#define UDR0   (sim_uart.udr)

#define RXC0   7
#define TXC0   6
#define UDRE0  5
#define RXEN0  4
#define TXEN0  3
#define UCSZ01 2
#define UCSZ00 1
#endif

void uart_init(uint32_t baudrate, uint32_t f_cpu) {
    /* Обчислення дільника швидкості UBRR */
    uint16_t ubrr_val = (uint16_t)((f_cpu / (16UL * baudrate)) - 1);
    
    UBRR0H = (uint8_t)(ubrr_val >> 8);
    UBRR0L = (uint8_t)(ubrr_val & 0xFF);
    
    /* Увімкнення ліній прийому (RXEN0) та передачі (TXEN0) */
    UCSR0B = (1 << RXEN0) | (1 << TXEN0);
    
    /* Формат кадру: 8 біт даних, 1 стоп-біт, без перевірки парності (8N1) */
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

bool uart_read_byte(uint8_t *byte) {
    if (!byte) {
        return false;
    }
    
    /* Перевіряємо прапорець завершення прийому байта */
    if (UCSR0A & (1 << RXC0)) {
        *byte = UDR0;
        return true;
    }
    
    return false;
}

bool uart_write_byte(uint8_t byte) {
    /* Перевіряємо прапорець готовності регістра передавача */
    if (UCSR0A & (1 << UDRE0)) {
        UDR0 = byte;
        return true;
    }
    
    return false;
}
