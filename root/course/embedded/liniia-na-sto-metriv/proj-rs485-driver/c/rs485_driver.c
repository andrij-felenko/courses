/* rs485_driver.h / rs485_driver.c — Промисловий драйвер RS-485 на C */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RS485_BUF_SIZE 256

typedef enum {
    RS485_STATE_IDLE = 0,
    RS485_STATE_RECEIVING,
    RS485_STATE_TRANSMITTING,
    RS485_STATE_TX_COMPLETE
} rs485_state_t;

typedef struct {
    uint8_t tx_buf[RS485_BUF_SIZE];
    uint8_t rx_buf[RS485_BUF_SIZE];
    volatile size_t tx_head;
    volatile size_t tx_tail;
    volatile size_t rx_count;
    volatile rs485_state_t state;
    volatile bool frame_ready;
    void (*set_de_pin)(bool enable);
    void (*uart_write_byte)(uint8_t data);
    void (*enable_tc_interrupt)(bool enable);
} rs485_port_t;

void rs485_init(rs485_port_t *port,
                void (*set_de)(bool),
                void (*uart_putc)(uint8_t),
                void (*enable_tc_irq)(bool))
{
    port->tx_head = 0;
    port->tx_tail = 0;
    port->rx_count = 0;
    port->state = RS485_STATE_IDLE;
    port->frame_ready = false;
    port->set_de_pin = set_de;
    port->uart_write_byte = uart_putc;
    port->enable_tc_interrupt = enable_tc_irq;

    /* Початковий стан: приймання (DE = 0) */
    port->set_de_pin(false);
}

bool rs485_send_packet(rs485_port_t *port, const uint8_t *data, size_t len)
{
    if (len == 0 || len > RS485_BUF_SIZE || port->state == RS485_STATE_TRANSMITTING) {
        return false;
    }

    for (size_t i = 0; i < len; ++i) {
        port->tx_buf[i] = data[i];
    }
    port->tx_head = len;
    port->tx_tail = 0;
    port->state = RS485_STATE_TRANSMITTING;

    /* 1. Вмикаємо передавач (DE = 1) */
    port->set_de_pin(true);

    /* 2. Відправляємо перший байт у чергу UART */
    uint8_t first_byte = port->tx_buf[port->tx_tail++];
    port->uart_write_byte(first_byte);

    return true;
}

/* Обробник переривання: байт переписано в зсувний регістр (TXE) */
void rs485_isr_txe(rs485_port_t *port)
{
    if (port->state != RS485_STATE_TRANSMITTING) {
        return;
    }

    if (port->tx_tail < port->tx_head) {
        port->uart_write_byte(port->tx_buf[port->tx_tail++]);
    } else {
        /* Усі байти завантажені — вмикаємо очікування повного завершення (TC) */
        port->enable_tc_interrupt(true);
    }
}

/* Обробник переривання: останній біт повністю вийшов у лінію (TC) */
void rs485_isr_tc(rs485_port_t *port)
{
    if (port->state == RS485_STATE_TRANSMITTING) {
        port->enable_tc_interrupt(false);
        /* 3. Безпечно вимикаємо передавач: стоп-біт гарантовано в лінії */
        port->set_de_pin(false);
        port->state = RS485_STATE_IDLE;
    }
}

/* Обробник переривання: отримано байт (RXNE) */
void rs485_isr_rxne(rs485_port_t *port, uint8_t byte)
{
    if (port->state == RS485_STATE_TRANSMITTING) {
        return; /* Ігноруємо відлуння, якщо /RE з'єднано з DE */
    }

    if (port->rx_count < RS485_BUF_SIZE) {
        port->rx_buf[port->rx_count++] = byte;
        port->state = RS485_STATE_RECEIVING;
    }
}

/* Викликається за таймером паузи (3.5 символи для Modbus або міжсимвольний таймаут) */
void rs485_timer_idle_timeout(rs485_port_t *port)
{
    if (port->state == RS485_STATE_RECEIVING && port->rx_count > 0) {
        port->frame_ready = true;
        port->state = RS485_STATE_IDLE;
    }
}
