#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    FSM_SEARCH_PREFIX,
    FSM_PARSE_LEN,
    FSM_READ_PAYLOAD
} ipd_parser_state_t;

typedef struct {
    ipd_parser_state_t state;
    uint8_t link_id;
    uint16_t payload_len;
    uint16_t bytes_read;
    uint8_t buffer[512];
} ipd_parser_t;

// Побайтовий асинхронний розбір потоку UART
void ipd_parser_feed_byte(ipd_parser_t *parser, uint8_t byte) {
    switch (parser->state) {
        case FSM_SEARCH_PREFIX:
            // Детекція префікса "+IPD," та перехід до парсингу довжини
            break;
        case FSM_PARSE_LEN:
            if (byte >= '0' && byte <= '9') {
                parser->payload_len = parser->payload_len * 10 + (byte - '0');
            } else if (byte == ':') {
                parser->bytes_read = 0;
                parser->state = FSM_READ_PAYLOAD;
            }
            break;
        case FSM_READ_PAYLOAD:
            parser->buffer[parser->bytes_read++] = byte;
            if (parser->bytes_read >= parser->payload_len) {
                // Пакет повністю прийнято, обробка додатком
                parser->state = FSM_SEARCH_PREFIX;
            }
            break;
    }
}
