#define UART_SR    (*(volatile uint32_t*)0x40011000)  // регістр стану
#define UART_DR    (*(volatile uint32_t*)0x40011004)  // регістр даних
#define SR_RXNE    (1u << 5)   // RX FIFO не порожня: є що читати
#define SR_TXFF    (1u << 7)   // TX FIFO повна: писати нікуди

// Забрати все, що встигло накопичитись у приймальній черзі.
void uart_drain_rx(uint8_t *buf, uint32_t cap, uint32_t *len)
{
    uint32_t n = 0;
    // Поки прапорець «не порожня» стоїть — черга віддає слово за словом.
    while ((UART_SR & SR_RXNE) && n < cap) {
        buf[n++] = (uint8_t)UART_DR;   // читання DR зсуває rd_ptr у залізі
    }
    *len = n;
}
