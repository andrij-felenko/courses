#include <stdint.h>
#include <stdbool.h>

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
} SimpleUart_t;

#define UART_SR_TXE (1u << 7)

bool Uart_PollSendByte(SimpleUart_t *uart, uint8_t byte, uint32_t timeout_ticks) {
    volatile uint32_t *DWT_CYCCNT = (volatile uint32_t *)0xE0001004;
    uint32_t start = *DWT_CYCCNT;

    while (!(uart->SR & UART_SR_TXE)) {
        if ((*DWT_CYCCNT - start) >= timeout_ticks) {
            return false; // Таймаут: периферія не відповідає
        }
    }
    uart->DR = byte;
    return true;
}
