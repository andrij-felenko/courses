/* uart_break_receiver.c - Обробник переривань UART із детекцією Break */
#include <stdint.h>
#include <stdbool.h>

#define RX_BUFFER_SIZE 512

typedef enum {
    DMX_STATE_WAIT_BREAK = 0,
    DMX_STATE_WAIT_START_CODE,
    DMX_STATE_RECEIVE_DATA
} dmx_rx_state_t;

typedef struct {
    volatile dmx_rx_state_t state;
    volatile uint16_t channel_index;
    volatile bool frame_ready;
    uint8_t buffer[RX_BUFFER_SIZE];
} dmx_receiver_t;

static dmx_receiver_t g_dmx_rx;

/* Функція, що викликається з вектора переривання USART_IRQHandler */
void USART_Receive_ISR_Handler(uint32_t status_reg, uint8_t data_reg) {
    bool framing_error = (status_reg & (1u << 1)) != 0; /* Біт FE у USART_SR/ISR */

    if (framing_error) {
        if (data_reg == 0x00) {
            /* Зафіксовано валідний сигнал Break! */
            g_dmx_rx.state = DMX_STATE_WAIT_START_CODE;
            g_dmx_rx.channel_index = 0;
        }
        return;
    }

    switch (g_dmx_rx.state) {
        case DMX_STATE_WAIT_START_CODE:
            if (data_reg == 0x00) {
                /* Валідний стартовий код для каналів діммера */
                g_dmx_rx.state = DMX_STATE_RECEIVE_DATA;
                g_dmx_rx.channel_index = 0;
            } else {
                /* Чужий стартовий код (наприклад RDM або текст) -> ігноруємо */
                g_dmx_rx.state = DMX_STATE_WAIT_BREAK;
            }
            break;

        case DMX_STATE_RECEIVE_DATA:
            if (g_dmx_rx.channel_index < RX_BUFFER_SIZE) {
                g_dmx_rx.buffer[g_dmx_rx.channel_index++] = data_reg;
                if (g_dmx_rx.channel_index == RX_BUFFER_SIZE) {
                    g_dmx_rx.frame_ready = true;
                    g_dmx_rx.state = DMX_STATE_WAIT_BREAK;
                }
            }
            break;

        case DMX_STATE_WAIT_BREAK:
        default:
            /* Очікуємо наступного розриву лінії, ігноруючи решту байтів */
            break;
    }
}
