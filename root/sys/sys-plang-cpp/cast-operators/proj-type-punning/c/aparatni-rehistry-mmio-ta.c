#include <stdint.h>

typedef struct {
    volatile uint32_t CR1;      // Control Register 1
    volatile uint32_t CR2;      // Control Register 2
    volatile uint32_t SR;       // Status Register
    volatile uint32_t DR;       // Data Register
} UartRegistersC;

// Небезпечно: C-style cast адреси пам'яті
void uart_send_c(uintptr_t base_addr, uint8_t byte) {
    UartRegistersC* uart = (UartRegistersC*)base_addr;
    while (!(uart->SR & 0x80)) {
        // Очікування готовності передавача
    }
    uart->DR = byte;
}
