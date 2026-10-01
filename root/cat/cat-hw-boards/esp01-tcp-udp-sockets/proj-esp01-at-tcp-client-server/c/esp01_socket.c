#include "esp01_socket.h"
#include <string.h>
#include <stdio.h>

// Низькорівнева відправка байтів у UART (апаратно-залежна функція)
extern void uart_send_bytes(const uint8_t *data, uint16_t len);

static void ringbuf_push(esp01_ringbuf_t *rb, uint8_t byte) {
    uint16_t next = (rb->head + 1) % ESP01_RING_BUF_SIZE;
    if (next != rb->tail) {
        rb->buffer[rb->head] = byte;
        rb->head = next;
    }
}

static bool ringbuf_pop(esp01_ringbuf_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false;
    }
    *byte = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % ESP01_RING_BUF_SIZE;
    return true;
}

void esp01_socket_init(esp01_socket_t *sock) {
    memset(sock, 0, sizeof(esp01_socket_t));
    sock->state = ESP01_STATE_IDLE;
    sock->ipd_parser.state = IPD_STATE_IDLE;
}

void esp01_uart_rx_isr_handler(esp01_socket_t *sock, uint8_t byte) {
    ringbuf_push(&sock->rx_ring, byte);
}

// Потоковий парсер кадрів +IPD (формат: +IPD,link_id,len:payload)
static void process_ipd_stream(esp01_socket_t *sock, uint8_t byte) {
    ipd_parser_t *parser = &sock->ipd_parser;

    switch (parser->state) {
        case IPD_STATE_IDLE: {
            static const char prefix[] = "+IPD,";
            static uint8_t prefix_idx = 0;
            if (byte == prefix[prefix_idx]) {
                prefix_idx++;
                if (prefix[prefix_idx] == '\0') {
                    prefix_idx = 0;
                    parser->state = IPD_STATE_LINK_ID;
                    parser->link_id = 0;
                    parser->data_len = 0;
                    parser->rx_bytes = 0;
                }
            } else {
                prefix_idx = (byte == prefix[0]) ? 1 : 0;
            }
            break;
        }

        case IPD_STATE_LINK_ID:
            if (byte >= '0' && byte <= '9') {
                parser->link_id = parser->link_id * 10 + (byte - '0');
            } else if (byte == ',') {
                parser->state = IPD_STATE_LEN;
            } else {
                parser->state = IPD_STATE_IDLE;
            }
            break;

        case IPD_STATE_LEN:
            if (byte >= '0' && byte <= '9') {
                parser->data_len = parser->data_len * 10 + (byte - '0');
            } else if (byte == ':') {
                if (parser->data_len > 0 && parser->data_len <= ESP01_MAX_PAYLOAD) {
                    parser->state = IPD_STATE_DATA;
                } else {
                    parser->state = IPD_STATE_IDLE;
                }
            } else {
                parser->state = IPD_STATE_IDLE;
            }
            break;

        case IPD_STATE_DATA:
            if (parser->rx_bytes < parser->data_len) {
                parser->payload[parser->rx_bytes++] = byte;
            }
            if (parser->rx_bytes >= parser->data_len) {
                // Пакет повністю прочитано — викликаємо callback
                esp01_on_data_received(parser->link_id, parser->payload, parser->data_len);
                parser->state = IPD_STATE_IDLE;
            }
            break;
    }
}

bool esp01_send_async(esp01_socket_t *sock, uint8_t link_id, const uint8_t *data, uint16_t len) {
    if (sock->state != ESP01_STATE_IDLE) {
        return false; // Автомат зайнятий
    }
    sock->active_link_id = link_id;
    sock->tx_data = data;
    sock->tx_len = len;
    sock->prompt_received = false;
    sock->send_success = false;
    sock->state = ESP01_STATE_SEND_INIT;
    return true;
}

void esp01_socket_poll(esp01_socket_t *sock, uint32_t current_time_ms) {
    uint8_t byte;

    // 1. Витягування даних з кільцевого буфера UART
    while (ringbuf_pop(&sock->rx_ring, &byte)) {
        if (sock->state == ESP01_STATE_WAIT_PROMPT && byte == '>') {
            sock->prompt_received = true;
        }
        process_ipd_stream(sock, byte);
    }

    // 2. Обробка станів неблокувального автомата
    switch (sock->state) {
        case ESP01_STATE_IDLE:
            break;

        case ESP01_STATE_SEND_INIT: {
            char cmd[32];
            snprintf(cmd, sizeof(cmd), "AT+CIPSEND=%d,%d\r\n", sock->active_link_id, sock->tx_len);
            uart_send_bytes((const uint8_t *)cmd, (uint16_t)strlen(cmd));
            sock->timeout_timer = current_time_ms;
            sock->state = ESP01_STATE_WAIT_PROMPT;
            break;
        }

        case ESP01_STATE_WAIT_PROMPT:
            if (sock->prompt_received) {
                uart_send_bytes(sock->tx_data, sock->tx_len);
                sock->timeout_timer = current_time_ms;
                sock->state = ESP01_STATE_WAIT_SEND_OK;
            } else if (current_time_ms - sock->timeout_timer > 2000) {
                sock->state = ESP01_STATE_ERROR;
            }
            break;

        case ESP01_STATE_WAIT_SEND_OK:
            if (current_time_ms - sock->timeout_timer > 1000) {
                sock->send_success = true;
                sock->state = ESP01_STATE_IDLE;
            }
            break;

        case ESP01_STATE_ERROR:
            sock->state = ESP01_STATE_IDLE;
            break;
    }
}
