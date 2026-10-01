#include "cdc_uart.h"

/**
 * @file cdc_uart.c
 * @brief Реалізація обробників переривань USART та кільцевої буферизації даних
 *        для прозорого обміну між ПК і цільовим пристроєм.
 */

#define APB2PERIPH_BASE       0x40010000UL
#define USART1_BASE           (APB2PERIPH_BASE + 0x3800UL)

#define USART1_SR             (*(volatile uint32_t *)(USART1_BASE + 0x00UL))
#define USART1_DR             (*(volatile uint32_t *)(USART1_BASE + 0x04UL))
#define USART1_BRR            (*(volatile uint32_t *)(USART1_BASE + 0x08UL))
#define USART1_CR1            (*(volatile uint32_t *)(USART1_BASE + 0x0CUL))

/* Прапорці SR та CR1 */
#define USART_SR_RXNE         (1UL << 5)
#define USART_SR_TXE          (1UL << 7)
#define USART_CR1_UE          (1UL << 13)
#define USART_CR1_TE          (1UL << 3)
#define USART_CR1_RE          (1UL << 2)
#define USART_CR1_RXNEIE      (1UL << 5)
#define USART_CR1_TXEIE       (1UL << 7)

static ring_buffer_t rx_buf;
static ring_buffer_t tx_buf;

static void ring_buffer_init(ring_buffer_t *rb) {
    rb->head = 0;
    rb->tail = 0;
}

static bool ring_buffer_put(ring_buffer_t *rb, uint8_t byte) {
    uint16_t next_head = (rb->head + 1U) & CDC_UART_BUF_MASK;
    if (next_head == rb->tail) {
        return false; /* Буфер переповнений */
    }
    rb->data[rb->head] = byte;
    rb->head = next_head;
    return true;
}

static bool ring_buffer_get(ring_buffer_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; /* Буфер порожній */
    }
    *byte = rb->data[rb->tail];
    rb->tail = (rb->tail + 1U) & CDC_UART_BUF_MASK;
    return true;
}

void cdc_uart_init(uint32_t baud_rate) {
    ring_buffer_init(&rx_buf);
    ring_buffer_init(&tx_buf);

    /* Обчислення BRR для частоти APB2 = 72 МГц */
    uint32_t pclk = 72000000UL;
    uint32_t brr = (pclk + (baud_rate / 2U)) / baud_rate;
    USART1_BRR = brr;

    /* Вмикаємо USART1, передавач, приймач та переривання RXNE */
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE | USART_CR1_RXNEIE;
}

bool cdc_uart_write_byte(uint8_t byte) {
    bool result = ring_buffer_put(&tx_buf, byte);
    if (result) {
        /* Активація переривання порожнього регістру передачі (TXEIE) */
        USART1_CR1 |= USART_CR1_TXEIE;
    }
    return result;
}

bool cdc_uart_read_byte(uint8_t *byte) {
    return ring_buffer_get(&rx_buf, byte);
}

uint16_t cdc_uart_rx_available(void) {
    return (rx_buf.head - rx_buf.tail) & CDC_UART_BUF_MASK;
}

void cdc_uart_flush(void) {
    rx_buf.head = rx_buf.tail;
    tx_buf.head = tx_buf.tail;
}

void cdc_uart_irq_handler(void) {
    uint32_t sr = USART1_SR;

    /* Обробка прийому байта (RXNE) */
    if (sr & USART_SR_RXNE) {
        uint8_t received = (uint8_t)(USART1_DR & 0xFFUL);
        ring_buffer_put(&rx_buf, received);
    }

    /* Обробка передачі байта (TXE) */
    if ((sr & USART_SR_TXE) && (USART1_CR1 & USART_CR1_TXEIE)) {
        uint8_t byte_to_send;
        if (ring_buffer_get(&tx_buf, &byte_to_send)) {
            USART1_DR = byte_to_send;
        } else {
            /* Вимикаємо переривання TXE, коли буфер спорожнів */
            USART1_CR1 &= ~USART_CR1_TXEIE;
        }
    }
}

/* Стандартне ім'я обробника у векторній таблиці STM32 */
void USART1_IRQHandler(void) {
    cdc_uart_irq_handler();
}
