#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    FSM_STATE_IDLE,
    FSM_STATE_SEND_CMD,
    FSM_STATE_WAIT_PROMPT,
    FSM_STATE_PUMP_PAYLOAD,
    FSM_STATE_WAIT_RESULT,
    FSM_STATE_ERROR_RECOVERY
} FsmState;

typedef struct {
    FsmState state;
    uint8_t link_id;
    const uint8_t* payload;
    uint16_t payload_len;
    uint16_t bytes_sent;
    uint32_t timer_start_ms;
    uint8_t prev_rx_byte;
} CipsendFsmDriver;

void fsm_driver_init(CipsendFsmDriver* driver) {
    driver->state = FSM_STATE_IDLE;
    driver->payload = NULL;
    driver->payload_len = 0;
    driver->bytes_sent = 0;
    driver->timer_start_ms = 0;
    driver->prev_rx_byte = 0;
}

bool fsm_driver_start_send(CipsendFsmDriver* driver, uint8_t link_id, const uint8_t* data, uint16_t len, uint32_t current_ms) {
    if (driver->state != FSM_STATE_IDLE || !data || len == 0) return false;

    driver->link_id = link_id;
    driver->payload = data;
    driver->payload_len = len;
    driver->bytes_sent = 0;
    driver->timer_start_ms = current_ms;
    driver->state = FSM_STATE_SEND_CMD;
    return true;
}

void fsm_driver_tick(CipsendFsmDriver* driver, uint32_t current_ms, uint8_t* rx_byte, bool has_rx) {
    switch (driver->state) {
        case FSM_STATE_IDLE:
            break;

        case FSM_STATE_SEND_CMD:
            // В реальній системі тут виконується запис "AT+CIPSEND=<id>,<len>\r\n" у UART TX
            driver->timer_start_ms = current_ms;
            driver->prev_rx_byte = 0;
            driver->state = FSM_STATE_WAIT_PROMPT;
            break;

        case FSM_STATE_WAIT_PROMPT:
            if (has_rx && rx_byte) {
                if (driver->prev_rx_byte == '>' && *rx_byte == ' ') {
                    driver->state = FSM_STATE_PUMP_PAYLOAD;
                    break;
                }
                driver->prev_rx_byte = *rx_byte;
            }
            if (current_ms - driver->timer_start_ms > 1000) { // 1000 мс таймаут промпту
                driver->state = FSM_STATE_ERROR_RECOVERY;
            }
            break;

        case FSM_STATE_PUMP_PAYLOAD:
            // Вивантаження payload у UART TX
            driver->bytes_sent = driver->payload_len;
            driver->timer_start_ms = current_ms;
            driver->state = FSM_STATE_WAIT_RESULT;
            break;

        case FSM_STATE_WAIT_RESULT:
            // Аналіз відповідей SEND OK / SEND FAIL / ERROR
            if (current_ms - driver->timer_start_ms > 5000) { // 5000 мс мережевий таймаут
                driver->state = FSM_STATE_ERROR_RECOVERY;
            }
            break;

        case FSM_STATE_ERROR_RECOVERY:
            // Відновлення стану
            driver->state = FSM_STATE_IDLE;
            break;
    }
}
