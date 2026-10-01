typedef enum {
    STATE_IDLE,
    STATE_MATCH_PREFIX,
    STATE_PARSE_MUX_ID,
    STATE_PARSE_LEN,
    STATE_READ_PAYLOAD
} ipd_parser_state_t;

void parse_uart_byte(uint8_t byte) {
    static ipd_parser_state_t state = STATE_IDLE;
    static uint16_t payload_len = 0;
    static uint16_t rx_count = 0;
    static uint8_t socket_id = 0;

    switch (state) {
        case STATE_IDLE:
            if (byte == '+') state = STATE_MATCH_PREFIX;
            break;
        case STATE_MATCH_PREFIX:
            state = STATE_PARSE_LEN;
            payload_len = 0;
            break;
        case STATE_PARSE_LEN:
            if (byte >= '0' && byte <= '9') {
                payload_len = payload_len * 10 + (byte - '0');
            } else if (byte == ':') {
                rx_count = 0;
                state = STATE_READ_PAYLOAD;
            }
            break;
        case STATE_READ_PAYLOAD:
            rx_count++;
            if (rx_count >= payload_len) {
                state = STATE_IDLE;
            }
            break;
    }
}
