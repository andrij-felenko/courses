#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TIMEOUT_AT_MS         2000
#define TIMEOUT_CONNECT_MS    10000
#define TIMEOUT_PROMPT_MS     2000
#define TIMEOUT_SEND_OK_MS    5000
#define MAX_RETRIES           3

typedef enum {
    SOCKET_STATE_INIT_AT,
    SOCKET_STATE_SET_CWMODE,
    SOCKET_STATE_SET_CIPMUX,
    SOCKET_STATE_CONNECT,
    SOCKET_STATE_CONNECTED,
    SOCKET_STATE_SEND_CMD,
    SOCKET_STATE_WAIT_PROMPT,
    SOCKET_STATE_SEND_PAYLOAD,
    SOCKET_STATE_WAIT_SEND_OK,
    SOCKET_STATE_RECOVERY
} SocketFsmState;

typedef struct {
    SocketFsmState state;
    uint32_t state_timer;
    uint8_t retry_count;
    uint8_t link_id;
    const uint8_t *tx_data;
    uint16_t tx_len;
} EspSocketDriver;

extern uint32_t get_tick_ms(void);
extern void uart_send_string(const char *str);
extern void uart_send_bytes(const uint8_t *buf, uint16_t len);
extern void gpio_hardware_reset_esp01(void);

void esp_driver_init(EspSocketDriver *drv) {
    drv->state = SOCKET_STATE_INIT_AT;
    drv->state_timer = get_tick_ms();
    drv->retry_count = 0;
    drv->link_id = 0;
    drv->tx_data = NULL;
    drv->tx_len = 0;
    uart_send_string("AT\r\n");
}

void esp_driver_on_parser_event(EspSocketDriver *drv, int event_type) {
    // 1: OK, 2: ERROR, 3: SEND OK, 4: PROMPT (>), 5: CLOSED
    switch (drv->state) {
        case SOCKET_STATE_INIT_AT:
            if (event_type == 1) {
                drv->state = SOCKET_STATE_SET_CWMODE;
                drv->state_timer = get_tick_ms();
                drv->retry_count = 0;
                uart_send_string("AT+CWMODE=1\r\n");
            }
            break;

        case SOCKET_STATE_SET_CWMODE:
            if (event_type == 1) {
                drv->state = SOCKET_STATE_SET_CIPMUX;
                drv->state_timer = get_tick_ms();
                drv->retry_count = 0;
                uart_send_string("AT+CIPMUX=1\r\n");
            }
            break;

        case SOCKET_STATE_SET_CIPMUX:
            if (event_type == 1) {
                drv->state = SOCKET_STATE_CONNECT;
                drv->state_timer = get_tick_ms();
                drv->retry_count = 0;
                uart_send_string("AT+CIPSTART=0,\"TCP\",\"192.168.1.100\",8080\r\n");
            }
            break;

        case SOCKET_STATE_CONNECT:
            if (event_type == 1) {
                drv->state = SOCKET_STATE_CONNECTED;
                drv->state_timer = get_tick_ms();
                drv->retry_count = 0;
            } else if (event_type == 2) {
                drv->state = SOCKET_STATE_INIT_AT;
                drv->state_timer = get_tick_ms();
                uart_send_string("AT\r\n");
            }
            break;

        case SOCKET_STATE_WAIT_PROMPT:
            if (event_type == 4) { // Надійшов символ '>'
                drv->state = SOCKET_STATE_SEND_PAYLOAD;
                uart_send_bytes(drv->tx_data, drv->tx_len);
                drv->state = SOCKET_STATE_WAIT_SEND_OK;
                drv->state_timer = get_tick_ms();
            }
            break;

        case SOCKET_STATE_WAIT_SEND_OK:
            if (event_type == 3) { // SEND OK
                drv->state = SOCKET_STATE_CONNECTED;
                drv->state_timer = get_tick_ms();
            } else if (event_type == 2) { // ERROR
                drv->state = SOCKET_STATE_CONNECTED;
            }
            break;

        case SOCKET_STATE_CONNECTED:
            if (event_type == 5) { // CLOSED
                drv->state = SOCKET_STATE_CONNECT;
                drv->state_timer = get_tick_ms();
                uart_send_string("AT+CIPSTART=0,\"TCP\",\"192.168.1.100\",8080\r\n");
            }
            break;

        default:
            break;
    }
}

void esp_driver_process(EspSocketDriver *drv) {
    uint32_t now = get_tick_ms();
    uint32_t elapsed = now - drv->state_timer;

    switch (drv->state) {
        case SOCKET_STATE_INIT_AT:
        case SOCKET_STATE_SET_CWMODE:
        case SOCKET_STATE_SET_CIPMUX:
            if (elapsed > TIMEOUT_AT_MS) {
                if (++drv->retry_count >= MAX_RETRIES) {
                    drv->state = SOCKET_STATE_RECOVERY;
                    drv->state_timer = now;
                } else {
                    drv->state_timer = now;
                    uart_send_string("AT\r\n");
                }
            }
            break;

        case SOCKET_STATE_CONNECT:
            if (elapsed > TIMEOUT_CONNECT_MS) {
                drv->state = SOCKET_STATE_INIT_AT;
                drv->state_timer = now;
                uart_send_string("AT\r\n");
            }
            break;

        case SOCKET_STATE_WAIT_PROMPT:
            if (elapsed > TIMEOUT_PROMPT_MS) {
                drv->state = SOCKET_STATE_CONNECTED;
            }
            break;

        case SOCKET_STATE_WAIT_SEND_OK:
            if (elapsed > TIMEOUT_SEND_OK_MS) {
                drv->state = SOCKET_STATE_CONNECTED;
            }
            break;

        case SOCKET_STATE_RECOVERY:
            gpio_hardware_reset_esp01();
            drv->retry_count = 0;
            drv->state = SOCKET_STATE_INIT_AT;
            drv->state_timer = now;
            uart_send_string("AT\r\n");
            break;

        default:
            break;
    }
}
