#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RXBUF_SIZE 256              // степінь двійки → загортання через маску
#define RXBUF_MASK (RXBUF_SIZE - 1)

static volatile uint8_t  rxbuf[RXBUF_SIZE];
static volatile uint16_t rx_head;  // пише ISR
static volatile uint16_t rx_tail;  // читає головний цикл
static volatile uint32_t rx_overruns;  // лічильник утрачених байтів — для діагностики

// Викликається з обробника переривання приймача UART: забрати байт і покласти в буфер.
// Нічого важкого тут робити НЕ можна — лише записати й вийти.
void uart_rx_isr(uint8_t b) {
    uint16_t next = (uint16_t)((rx_head + 1) & RXBUF_MASK);
    if (next == rx_tail) {         // буфер повний — місця немає
        rx_overruns++;             // чесно рахуємо втрату, але байт мусимо відкинути
        return;
    }
    rxbuf[rx_head] = b;
    rx_head = next;                // зсув head — остання дія, після запису байта
}

// Чи є непрочитані байти у буфері (виклик із головного циклу).
static inline bool rx_available(void) {
    return rx_head != rx_tail;
}

// Забрати один байт із буфера. Викликати лише коли rx_available() == true.
static inline uint8_t rx_get(void) {
    uint8_t b = rxbuf[rx_tail];
    rx_tail = (uint16_t)((rx_tail + 1) & RXBUF_MASK);
    return b;
}
