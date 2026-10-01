#ifndef ESP01_SOCKET_H
#define ESP01_SOCKET_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ESP01_RING_BUF_SIZE 256
#define ESP01_MAX_PAYLOAD 512

// Типи мережевих протоколів для ESP-01
typedef enum {
    ESP01_PROTO_TCP,
    ESP01_PROTO_UDP
} esp01_proto_t;

// Стан асинхронного кінцевого автомата сокета
typedef enum {
    ESP01_STATE_IDLE,
    ESP01_STATE_SEND_INIT,
    ESP01_STATE_WAIT_PROMPT,
    ESP01_STATE_SEND_DATA,
    ESP01_STATE_WAIT_SEND_OK,
    ESP01_STATE_ERROR
} esp01_state_t;

// Стан потокового розбору кадрів +IPD
typedef enum {
    IPD_STATE_IDLE,
    IPD_STATE_LINK_ID,
    IPD_STATE_LEN,
    IPD_STATE_DATA
} ipd_state_t;

// Кільцевий буфер для UART
typedef struct {
    uint8_t buffer[ESP01_RING_BUF_SIZE];
    uint16_t head;
    uint16_t tail;
} esp01_ringbuf_t;

// Структура потокового парсера кадрів +IPD
typedef struct {
    ipd_state_t state;
    uint8_t link_id;
    uint16_t data_len;
    uint16_t rx_bytes;
    uint8_t payload[ESP01_MAX_PAYLOAD];
} ipd_parser_t;

// Контекст сокета ESP-01
typedef struct {
    esp01_state_t state;
    esp01_ringbuf_t rx_ring;
    ipd_parser_t ipd_parser;
    uint8_t active_link_id;
    const uint8_t *tx_data;
    uint16_t tx_len;
    uint32_t timeout_timer;
    bool prompt_received;
    bool send_success;
} esp01_socket_t;

// Публічний інтерфейс
void esp01_socket_init(esp01_socket_t *sock);
bool esp01_send_async(esp01_socket_t *sock, uint8_t link_id, const uint8_t *data, uint16_t len);
void esp01_socket_poll(esp01_socket_t *sock, uint32_t current_time_ms);
void esp01_uart_rx_isr_handler(esp01_socket_t *sock, uint8_t byte);

// Callback-функція при отриманні пакету +IPD
void esp01_on_data_received(uint8_t link_id, const uint8_t *data, uint16_t len);

#endif // ESP01_SOCKET_H
