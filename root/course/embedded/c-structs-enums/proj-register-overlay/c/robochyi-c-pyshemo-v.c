#define UART0_CONF0  (*(volatile uint32_t *)(UART0_BASE + 0x20))

// Приклад позицій прапорців у CONF0 (умовно, за даташитом свого чипа):
#define CONF0_TXFIFO_RST   (1u << 18)   // скинути передавальне FIFO
#define CONF0_RXFIFO_RST   (1u << 17)   // скинути приймальне FIFO

// Виставити біти за маскою, не чіпаючи решту:
static inline void conf0_set(uint32_t mask) {
    UART0_CONF0 = UART0_CONF0 | mask;    // читання-модифікація-запис
}

// Зняти біти за маскою:
static inline void conf0_clear(uint32_t mask) {
    UART0_CONF0 = UART0_CONF0 & ~mask;
}

// Короткий імпульс скидання приймального FIFO: підняли біт і одразу зняли.
void uart_flush_rx(void) {
    conf0_set(CONF0_RXFIFO_RST);         // 1 → почати скидання
    conf0_clear(CONF0_RXFIFO_RST);       // 0 → завершити
}
