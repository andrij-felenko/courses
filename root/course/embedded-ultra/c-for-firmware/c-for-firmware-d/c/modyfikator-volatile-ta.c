#include <stdint.h>

#define UART_SR_REG  (*(volatile uint32_t *)0x40013800UL)
#define UART_DR_REG  (*(volatile uint32_t *)0x40013804UL)
#define RXNE_FLAG    (1U << 5)

uint8_t uart_receive_byte_direct(void) {
    // Компілятор змушений щоразу читати реальну шину заліза
    while (!(UART_SR_REG & RXNE_FLAG)) {
        // Очікування надходження байта
    }
    // Читання DR скидає прапорець RXNE на рівні кремнію
    return (uint8_t)(UART_DR_REG & 0xFFU);
}
