#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RS485_BUFFER_SIZE 256

typedef enum {
    RS485_STATE_IDLE = 0,
    RS485_STATE_TRANSMITTING,
    RS485_STATE_RECEIVING,
    RS485_STATE_ERROR
} rs485_state_t;

typedef struct {
    uint8_t tx_buf[RS485_BUFFER_SIZE];
    volatile size_t tx_head;
    volatile size_t tx_len;
    uint8_t rx_buf[RS485_BUFFER_SIZE];
    volatile size_t rx_len;
    volatile rs485_state_t state;
    bool local_echo_enabled;
    volatile size_t echo_skip_count;
} rs485_driver_t;

static rs485_driver_t g_rs485;

// Керування піном DE через атомарний регістр BSRR (порт GPIOA, пін PA4)
static inline void de_pin_set_high(void) {
    GPIOA->BSRR = (1 << 4);
}

static inline void de_pin_set_low(void) {
    GPIOA->BSRR = (1 << (4 + 16));
}

void rs485_init(bool enable_local_echo) {
    g_rs485.tx_head = 0;
    g_rs485.tx_len = 0;
    g_rs485.rx_len = 0;
    g_rs485.state = RS485_STATE_IDLE;
    g_rs485.local_echo_enabled = enable_local_echo;
    g_rs485.echo_skip_count = 0;
    de_pin_set_low();
}

bool rs485_send_packet(const uint8_t *data, size_t len) {
    if (len == 0 || len > RS485_BUFFER_SIZE || g_rs485.state == RS485_STATE_TRANSMITTING) {
        return false;
    }

    for (size_t i = 0; i < len; ++i) {
        g_rs485.tx_buf[i] = data[i];
    }
    g_rs485.tx_head = 0;
    g_rs485.tx_len = len;
    g_rs485.echo_skip_count = g_rs485.local_echo_enabled ? 0 : len;
    g_rs485.state = RS485_STATE_TRANSMITTING;

    // Піднімаємо лінію DE перед першим байтом
    de_pin_set_high();

    // Записуємо перший байт і вмикаємо переривання TXE
    USART1->TDR = g_rs485.tx_buf[g_rs485.tx_head++];
    USART1->CR1 |= USART_CR1_TXEIE;

    return true;
}

// Обробник переривання USART (ISR)
void USART1_IRQHandler(void) {
    uint32_t isr = USART1->ISR;
    uint32_t cr1 = USART1->CR1;

    // 1. Очищення апаратних помилок
    usart1_clear_error_flags(isr);

    // 2. Обробка передачі: TDR звільнився (TXE)
    if ((isr & USART_ISR_TXE_TXFNF) && (cr1 & USART_CR1_TXEIE)) {
        if (g_rs485.tx_head < g_rs485.tx_len) {
            USART1->TDR = g_rs485.tx_buf[g_rs485.tx_head++];
        } else {
            // Буфер вичерпано: вимикаємо TXE, вмикаємо очікування завершення стоп-біта (TC)
            USART1->CR1 &= ~USART_CR1_TXEIE;
            USART1->CR1 |= USART_CR1_TCIE;
        }
    }

    // 3. Обробка повного завершення передачі (TC)
    if ((isr & USART_ISR_TC) && (cr1 & USART_CR1_TCIE)) {
        USART1->ICR = USART_ICR_TCCF; // Очищення прапорця TC
        USART1->CR1 &= ~USART_CR1_TCIE;
        de_pin_set_low();             // Опускаємо DE: перехід у прийом
        g_rs485.state = RS485_STATE_IDLE;
    }

    // 4. Обробка прийому даних (RXNE)
    if (isr & USART_ISR_RXNE_RXFNE) {
        uint8_t byte = (uint8_t)USART1->RDR;
        if (g_rs485.echo_skip_count > 0) {
            g_rs485.echo_skip_count--; // Скидання байта власного відлуння
        } else if (g_rs485.rx_len < RS485_BUFFER_SIZE) {
            g_rs485.rx_buf[g_rs485.rx_len++] = byte;
        }
    }
}
