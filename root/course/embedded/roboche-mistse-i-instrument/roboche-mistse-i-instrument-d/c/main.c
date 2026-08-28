#include <stdint.h>
#include <stdbool.h>

/* Базова структура регістрів апаратного блоку UART */
typedef struct {
    volatile uint32_t SR;   /* Регістр статусу */
    volatile uint32_t DR;   /* Регістр даних */
    volatile uint32_t BRR;  /* Регістр швидкості */
    volatile uint32_t CR1;  /* Регістр керування */
} UartRegs;

#define UART_SR_TXE   (1U << 7)  /* Прапорець: буфер передавача порожній */

void uart_write_byte(UartRegs *uart, uint8_t byte) {
    /* Очікуємо готовності буфера перед записом */
    while (!(uart->SR & UART_SR_TXE)) {
        /* Активне очікування прапорця апаратного буфера */
    }
    uart->DR = byte;
}

void uart_write_str(UartRegs *uart, const char *str) {
    while (*str) {
        uart_write_byte(uart, (uint8_t)(*str++));
    }
}
