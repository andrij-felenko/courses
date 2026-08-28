#include <stdint.h>

// Опис апаратного блоку UART через структуру
typedef struct {
    volatile uint32_t SR;    // 0x00: Регістр статусу
    volatile uint32_t DR;    // 0x04: Регістр даних
    volatile uint32_t BRR;   // 0x08: Регістр швидкості (Baud Rate)
    volatile uint32_t CR1;   // 0x0C: Регістр керування 1
    volatile uint32_t CR2;   // 0x10: Регістр керування 2
    volatile uint32_t CR3;   // 0x14: Регістр керування 3
} UART_Regs;

#define UART1_BASE (0x40013800UL)
#define UART1      ((UART_Regs *)UART1_BASE)

void uart_send_byte(UART_Regs *uart, uint8_t byte) {
    // Опитування біта передавача TXE (Transmit Data Register Empty)
    while (!(uart->SR & (1U << 7))) {
        // Очікування звільнення вихідного буфера
    }
    uart->DR = byte;
}
