#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    SEND_STATE_IDLE,
    SEND_STATE_WAIT_PROMPT,
    SEND_STATE_TRANSMITTING,
    SEND_STATE_WAIT_ACK,
    SEND_STATE_SUCCESS,
    SEND_STATE_FAILED
} send_fsm_state_t;

typedef struct {
    send_fsm_state_t state;
    uint32_t timer_ms;
    uint8_t link_id;
    const uint8_t *tx_data;
    uint16_t tx_len;
    uint16_t sent_bytes;
} send_fsm_t;

void send_fsm_start(send_fsm_t *fsm, uint8_t link_id, const uint8_t *data, uint16_t len, uint32_t current_ms) {
    fsm->state = SEND_STATE_WAIT_PROMPT;
    fsm->link_id = link_id;
    fsm->tx_data = data;
    fsm->tx_len = len;
    fsm->sent_bytes = 0;
    fsm->timer_ms = current_ms;
}

void send_fsm_poll(send_fsm_t *fsm, uint32_t current_ms, void (*uart_send_bytes)(const void*, uint16_t)) {
    if (fsm->state == SEND_STATE_WAIT_PROMPT) {
        if (current_ms - fsm->timer_ms > 2000) {
            fsm->state = SEND_STATE_FAILED;
        }
    } else if (fsm->state == SEND_STATE_WAIT_ACK) {
        if (current_ms - fsm->timer_ms > 5000) {
            fsm->state = SEND_STATE_FAILED;
        }
    }
}

void send_fsm_on_rx_char(send_fsm_t *fsm, char c, uint32_t current_ms, void (*uart_send_bytes)(const void*, uint16_t)) {
    if (fsm->state == SEND_STATE_WAIT_PROMPT && c == '>') {
        fsm->state = SEND_STATE_TRANSMITTING;
        uart_send_bytes(fsm->tx_data, fsm->tx_len);
        fsm->state = SEND_STATE_WAIT_ACK;
        fsm->timer_ms = current_ms;
    }
}

void send_fsm_on_line_response(send_fsm_t *fsm, const char *line) {
    if (fsm->state == SEND_STATE_WAIT_ACK) {
        if (strstr(line, "SEND OK") != NULL) {
            fsm->state = SEND_STATE_SUCCESS;
        } else if (strstr(line, "SEND FAIL") != NULL || strstr(line, "ERROR") != NULL) {
            fsm->state = SEND_STATE_FAILED;
        }
    }
}
