#include <stdint.h>
#include <stdbool.h>

#define RX_BUF_SIZE 512
#define T_CHAR_TIMEOUT_MS 10
#define T_COMMAND_TIMEOUT_MS 1000

typedef enum {
    FSM_IDLE,
    FSM_RECEIVE_STREAM,
    FSM_PARSE_FRAME,
    FSM_READY,
    FSM_TIMEOUT_ERROR
} fsm_state_t;

typedef struct {
    uint8_t buffer[RX_BUF_SIZE];
    uint16_t head;
    uint16_t tail;
    uint32_t last_byte_time_ms;
    uint32_t cmd_start_time_ms;
    fsm_state_t state;
} at_parser_t;

void at_parser_process_rx(at_parser_t *parser, uint8_t byte, uint32_t current_time_ms) {
    uint16_t next_head = (parser->head + 1) % RX_BUF_SIZE;
    if (next_head != parser->tail) {
        parser->buffer[parser->head] = byte;
        parser->head = next_head;
        parser->last_byte_time_ms = current_time_ms;
        if (parser->state == FSM_IDLE) {
            parser->state = FSM_RECEIVE_STREAM;
        }
    }
}

void at_parser_update_fsm(at_parser_t *parser, uint32_t current_time_ms) {
    if (parser->state == FSM_RECEIVE_STREAM) {
        if ((current_time_ms - parser->last_byte_time_ms) >= T_CHAR_TIMEOUT_MS) {
            parser->state = FSM_PARSE_FRAME;
        } else if ((current_time_ms - parser->cmd_start_time_ms) >= T_COMMAND_TIMEOUT_MS) {
            parser->state = FSM_TIMEOUT_ERROR;
        }
    }
}
