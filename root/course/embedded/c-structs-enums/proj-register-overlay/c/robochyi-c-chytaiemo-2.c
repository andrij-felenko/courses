#include <stddef.h>

// Регістр даних FIFO — за зсувом 0x00 від бази UART0:
#define UART0_FIFO   (*(volatile uint32_t *)(UART0_BASE + 0x00))

// Забрати всі готові байти з FIFO у буфер; повертає, скільки забрали.
size_t uart_drain(uint8_t *buf, size_t cap) {
    size_t n = 0;
    while (n < cap && uart_rx_count() > 0) {   // поки є що читати й куди
        buf[n++] = (uint8_t)(UART0_FIFO & 0xFF);
    }
    return n;
}
