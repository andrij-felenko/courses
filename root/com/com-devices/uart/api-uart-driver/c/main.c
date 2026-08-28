#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define UART_RING_BUFFER_SIZE 128U

/* Структура кільцевого буфера */
typedef struct {
    uint8_t buffer[UART_RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} uart_ring_buffer_t;

/* Коди помилок драйвера */
typedef enum {
    UART_ERR_NONE = 0x00,
    UART_ERR_OVERRUN = 0x01,
    UART_ERR_FRAMING = 0x02,
    UART_ERR_PARITY = 0x04,
    UART_ERR_BUFFER_FULL = 0x08
} uart_error_flags_t;

/* Структура стану екземпляра UART */
typedef struct {
    void *hardware_base;                 /* Базова адреса регістрів */
    uart_ring_buffer_t rx_ring;          /* Буфер приймача */
    uart_ring_buffer_t tx_ring;          /* Буфер передавача */
    volatile uint32_t error_counters;    /* Лічильник помилок */
    bool hw_flow_control;                /* Прапор RTS/CTS */
} uart_driver_t;

/* API Функції */
void uart_driver_init(uart_driver_t *dev, void *hw_base, uint32_t baud_rate, bool use_flow_control);
bool uart_send_byte(uart_driver_t *dev, uint8_t byte);
size_t uart_send_buffer(uart_driver_t *dev, const uint8_t *data, size_t length);
bool uart_receive_byte(uart_driver_t *dev, uint8_t *out_byte);
size_t uart_rx_available(const uart_driver_t *dev);
void uart_isr_handler(uart_driver_t *dev);

/* Внутрішні допоміжні функції буфера */
static inline bool ring_push(uart_ring_buffer_t *ring, uint8_t byte) {
    uint16_t next_head = (ring->head + 1U) % UART_RING_BUFFER_SIZE;
    if (next_head == ring->tail) {
        return false; /* Буфер повний */
    }
    ring->buffer[ring->head] = byte;
    ring->head = next_head;
    return true;
}

static inline bool ring_pop(uart_ring_buffer_t *ring, uint8_t *out_byte) {
    if (ring->head == ring->tail) {
        return false; /* Буфер порожній */
    }
    *out_byte = ring->buffer[ring->tail];
    ring->tail = (ring->tail + 1U) % UART_RING_BUFFER_SIZE;
    return true;
}

/* Реалізація обробника переривань (ISR) */
void uart_isr_handler(uart_driver_t *dev) {
    /* Псевдокод доступу до регістрів конкретного HW */
    volatile uint32_t *sr = (volatile uint32_t *)(dev->hardware_base);
    volatile uint32_t *dr = (volatile uint32_t *)(dev->hardware_base + 0x04);
    volatile uint32_t *cr1 = (volatile uint32_t *)(dev->hardware_base + 0x0C);

    uint32_t status = *sr;

    /* 1. Обробка приймання RXNE */
    if ((status & (1U << 5U)) != 0U) { /* RXNE bit */
        uint8_t received_byte = (uint8_t)(*dr);
        if (!ring_push(&dev->rx_ring, received_byte)) {
            dev->error_counters |= UART_ERR_BUFFER_FULL;
        }
    }

    /* 2. Обробка помилок кадру/переповнення */
    if ((status & (1U << 3U)) != 0U) { dev->error_counters |= UART_ERR_OVERRUN; }
    if ((status & (1U << 1U)) != 0U) { dev->error_counters |= UART_ERR_FRAMING; }
    if ((status & (1U << 0U)) != 0U) { dev->error_counters |= UART_ERR_PARITY; }

    /* 3. Обробка передачі TXE */
    if ((status & (1U << 7U)) != 0U && (*cr1 & (1U << 7U)) != 0U) { /* TXEIE bit */
        uint8_t byte_to_send;
        if (ring_pop(&dev->tx_ring, &byte_to_send)) {
            *dr = byte_to_send;
        } else {
            /* Буфер передачі порожній — вимикаємо переривання TXEIE */
            *cr1 &= ~(1U << 7U);
        }
    }
}
