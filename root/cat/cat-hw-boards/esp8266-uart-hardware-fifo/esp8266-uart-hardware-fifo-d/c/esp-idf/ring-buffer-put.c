#include "esp8266/uart_register.h"
#include "esp_attr.h"

#define RING_BUF_SIZE 1024
typedef struct {
    uint8_t buffer[RING_BUF_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} ring_buffer_t;

static ring_buffer_t rx_ring_buf = { .head = 0, .tail = 0 };

static inline void ring_buffer_put(uint8_t byte) {
    uint16_t next = (rx_ring_buf.head + 1) % RING_BUF_SIZE;
    if (next != rx_ring_buf.tail) {
        rx_ring_buf.buffer[rx_ring_buf.head] = byte;
        rx_ring_buf.head = next;
    }
}

void IRAM_ATTR uart0_isr_handler(void *arg) {
    uint32_t int_status = READ_PERI_REG(UART_INT_ST_REG(0));

    // Обробка прийому за порогом заповнення або таймаутом простою
    if (int_status & (UART_RXFIFO_FULL_INT_ST | UART_RXFIFO_TOUT_INT_ST)) {
        while ((READ_PERI_REG(UART_STATUS_REG(0)) >> UART_RXFIFO_CNT_S) & UART_RXFIFO_CNT_V) {
            uint8_t ch = READ_PERI_REG(UART_FIFO_REG(0)) & 0xFF;
            ring_buffer_put(ch);
        }
        // Очищення прапорів переривань ПІСЛЯ зчитування даних
        WRITE_PERI_REG(UART_INT_CLR_REG(0), UART_RXFIFO_FULL_INT_CLR | UART_RXFIFO_TOUT_INT_CLR);
    }

    // Обробка помилки переповнення буфера (overrun error)
    if (int_status & UART_RXFIFO_OVF_INT_ST) {
        SET_PERI_REG_MASK(UART_CONF0_REG(0), UART_RXFIFO_RST);
        CLEAR_PERI_REG_MASK(UART_CONF0_REG(0), UART_RXFIFO_RST);
        WRITE_PERI_REG(UART_INT_CLR_REG(0), UART_RXFIFO_OVF_INT_CLR);
    }
}

void uart0_hardware_init(uint32_t baud_rate) {
    // 1. Налаштування дільника бодової швидкості (при APB clock 80 МГц)
    uint32_t clk_div = (80000000 << 7) / baud_rate;
    WRITE_PERI_REG(UART_CLKDIV_REG(0), ((clk_div >> 7) << UART_CLKDIV_INT_S) | ((clk_div & 0x7F) << UART_CLKDIV_FRAC_S));

    // 2. Встановлення порогів RX FIFO (watermark = 116, timeout = 10)
    WRITE_PERI_REG(UART_CONF1_REG(0),
        ((116 & UART_RXFIFO_FULL_THRHD_V) << UART_RXFIFO_FULL_THRHD_S) |
        ((10 & UART_RX_TOUT_THRHD_V) << UART_RX_TOUT_THRHD_S));

    // 3. Дозвіл таймауту простою та апаратного контролю потоку RTS/CTS
    SET_PERI_REG_MASK(UART_CONF0_REG(0), UART_RX_TOUT_EN | UART_RTS_FLOW_EN | UART_TX_FLOW_EN);
    SET_PERI_REG_BITS(UART_CONF0_REG(0), UART_RTS_TOUT_THRHD_V, 100, UART_RTS_TOUT_THRHD_S);

    // 4. Скидання апаратних FIFO перед запуском
    SET_PERI_REG_MASK(UART_CONF0_REG(0), UART_RXFIFO_RST | UART_TXFIFO_RST);
    CLEAR_PERI_REG_MASK(UART_CONF0_REG(0), UART_RXFIFO_RST | UART_TXFIFO_RST);

    // 5. Очищення та дозвіл апаратних переривань
    WRITE_PERI_REG(UART_INT_CLR_REG(0), 0xFFFF);
    WRITE_PERI_REG(UART_INT_ENA_REG(0), UART_RXFIFO_FULL_INT_ENA | UART_RXFIFO_TOUT_INT_ENA | UART_RXFIFO_OVF_INT_ENA);
}
