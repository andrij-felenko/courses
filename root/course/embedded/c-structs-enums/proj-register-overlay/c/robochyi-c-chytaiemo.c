#include <stdint.h>

// Базова адреса UART0 на APB-шині ESP32 (з даташита):
#define UART0_BASE   0x3FF40000u

// Регістр статусу — за зсувом 0x1C від бази.
// volatile: значення регістра може змінитися БЕЗ участі нашого коду
// (залізо саме кладе туди лічильники), тож компілятор не має права
// кешувати прочитане чи викидати «зайве» повторне читання.
#define UART0_STATUS  (*(volatile uint32_t *)(UART0_BASE + 0x1C))

// Позиції й маски полів — рівно за даташитом:
#define RXFIFO_CNT_SHIFT   0
#define RXFIFO_CNT_MASK    0xFFu          // 8 бітів
#define TXFIFO_CNT_SHIFT   16
#define TXFIFO_CNT_MASK    0xFFu          // 8 бітів

// Скільки байтів чекає в приймальному FIFO:
static inline uint8_t uart_rx_count(void) {
    uint32_t w = UART0_STATUS;                       // одне читання слова
    return (uint8_t)((w >> RXFIFO_CNT_SHIFT) & RXFIFO_CNT_MASK);
}

// Скільки байтів ще не відіслано з передавального FIFO:
static inline uint8_t uart_tx_count(void) {
    uint32_t w = UART0_STATUS;
    return (uint8_t)((w >> TXFIFO_CNT_SHIFT) & TXFIFO_CNT_MASK);
}
