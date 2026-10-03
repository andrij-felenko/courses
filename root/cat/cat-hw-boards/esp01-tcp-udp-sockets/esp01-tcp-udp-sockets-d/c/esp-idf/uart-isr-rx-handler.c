#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RING_BUFFER_SIZE 256
#define MAX_AT_RESPONSE_LEN 64

typedef enum {
    FSM_IDLE_SEARCH,
    FSM_PARSE_IPD_HEADER,
    FSM_READ_IPD_PAYLOAD,
    FSM_WAIT_CMD_RESPONSE
} fsm_state_t;

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} ring_buffer_t;

typedef void (*socket_data_cb_t)(uint8_t link_id, const uint8_t *data, uint16_t len);

typedef struct {
    fsm_state_t state;
    ring_buffer_t rx_ring;
    uint8_t current_link_id;
    uint16_t ipd_bytes_remaining;
    char line_buf[MAX_AT_RESPONSE_LEN];
    uint8_t line_pos;
    socket_data_cb_t on_data_received;
} esp01_driver_t;

static esp01_driver_t g_driver;

// Вставка байта у кільцевий буфер з переривання UART ISR
void uart_isr_rx_handler(uint8_t rx_byte) {
    uint16_t next_head = (g_driver.rx_ring.head + 1) % RING_BUFFER_SIZE;
    if (next_head != g_driver.rx_ring.tail) {
        g_driver.rx_ring.buffer[g_driver.rx_ring.head] = rx_byte;
        g_driver.rx_ring.head = next_head;
    }
}

// Вичитання байта з кільцевого буфера
static bool ring_buffer_pop(uint8_t *byte) {
    if (g_driver.rx_ring.head == g_driver.rx_ring.tail) {
        return false;
    }
    *byte = g_driver.rx_ring.buffer[g_driver.rx_ring.tail];
    g_driver.rx_ring.tail = (g_driver.rx_ring.tail + 1) % RING_BUFFER_SIZE;
    return true;
}

// Головний неблокуючий крок FSM-парсера
void esp01_driver_process(void) {
    uint8_t byte;
    while (ring_buffer_pop(&byte)) {
        switch (g_driver.state) {
            case FSM_IDLE_SEARCH:
                if (byte == '+') {
                    g_driver.line_pos = 0;
                    g_driver.line_buf[g_driver.line_pos++] = byte;
                } else if (g_driver.line_pos > 0 && g_driver.line_pos < MAX_AT_RESPONSE_LEN - 1) {
                    g_driver.line_buf[g_driver.line_pos++] = byte;
                    g_driver.line_buf[g_driver.line_pos] = '\0';

                    if (strstr(g_driver.line_buf, "+IPD,")) {
                        g_driver.state = FSM_PARSE_IPD_HEADER;
                        g_driver.line_pos = 0;
                    }
                }
                break;

            case FSM_PARSE_IPD_HEADER:
                // Розбір синтаксису: <link_id>,<len>: або <len>:
                if (byte == ':') {
                    g_driver.line_buf[g_driver.line_pos] = '\0';
                    int link_id = 0, len = 0;
                    if (sscanf(g_driver.line_buf, "%d,%d", &link_id, &len) == 2) {
                        g_driver.current_link_id = (uint8_t)link_id;
                        g_driver.ipd_bytes_remaining = (uint16_t)len;
                    } else if (sscanf(g_driver.line_buf, "%d", &len) == 1) {
                        g_driver.current_link_id = 0;
                        g_driver.ipd_bytes_remaining = (uint16_t)len;
                    }
                    g_driver.state = FSM_READ_IPD_PAYLOAD;
                } else if (g_driver.line_pos < MAX_AT_RESPONSE_LEN - 1) {
                    g_driver.line_buf[g_driver.line_pos++] = byte;
                }
                break;

            case FSM_READ_IPD_PAYLOAD:
                // Пряма вигрузка байтів корисного навантаження у колбек
                if (g_driver.on_data_received) {
                    g_driver.on_data_received(g_driver.current_link_id, &byte, 1);
                }
                g_driver.ipd_bytes_remaining--;
                if (g_driver.ipd_bytes_remaining == 0) {
                    g_driver.line_pos = 0;
                    g_driver.state = FSM_IDLE_SEARCH;
                }
                break;

            default:
                g_driver.state = FSM_IDLE_SEARCH;
                break;
        }
    }
}
