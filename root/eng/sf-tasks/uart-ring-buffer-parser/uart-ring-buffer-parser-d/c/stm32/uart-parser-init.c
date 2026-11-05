#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Константи протоколу кадрів
#define FRAME_PREAMBLE_1   0xAA
#define FRAME_PREAMBLE_2   0x55
#define MAX_PAYLOAD_SIZE   64

// Перелік станів скінченного автомата (FSM)
typedef enum {
    STATE_PREAMBLE_1,
    STATE_PREAMBLE_2,
    STATE_READ_LEN,
    STATE_READ_PAYLOAD,
    STATE_READ_CRC
} fsm_state_t;

// Структура прийнятого кадру
typedef struct {
    uint8_t payload[MAX_PAYLOAD_SIZE];
    uint8_t length;
    uint8_t crc;
} frame_t;

// Контекст потокового парсера
typedef struct {
    fsm_state_t state;
    frame_t current_frame;
    uint8_t payload_idx;
    uint8_t calculated_crc;
} uart_parser_t;

// Ініціалізація парсера
void uart_parser_init(uart_parser_t *parser) {
    parser->state = STATE_PREAMBLE_1;
    parser->payload_idx = 0;
    parser->calculated_crc = 0;
}

// Інкрементальне оновлення контрольної суми (XOR)
static inline uint8_t update_crc(uint8_t current_crc, uint8_t byte) {
    return current_crc ^ byte;
}

// Покрокова обробка одного байта з потоку
bool uart_parser_feed_byte(uart_parser_t *parser, uint8_t byte, frame_t *out_frame) {
    switch (parser->state) {
        case STATE_PREAMBLE_1:
            if (byte == FRAME_PREAMBLE_1) {
                parser->state = STATE_PREAMBLE_2;
            }
            break;

        case STATE_PREAMBLE_2:
            if (byte == FRAME_PREAMBLE_2) {
                parser->state = STATE_READ_LEN;
            } else if (byte != FRAME_PREAMBLE_1) {
                parser->state = STATE_PREAMBLE_1;
            }
            break;

        case STATE_READ_LEN:
            if (byte > 0 && byte <= MAX_PAYLOAD_SIZE) {
                parser->current_frame.length = byte;
                parser->payload_idx = 0;
                parser->calculated_crc = update_crc(0, byte);
                parser->state = STATE_READ_PAYLOAD;
            } else {
                parser->state = STATE_PREAMBLE_1;
            }
            break;

        case STATE_READ_PAYLOAD:
            parser->current_frame.payload[parser->payload_idx++] = byte;
            parser->calculated_crc = update_crc(parser->calculated_crc, byte);
            if (parser->payload_idx >= parser->current_frame.length) {
                parser->state = STATE_READ_CRC;
            }
            break;

        case STATE_READ_CRC:
            parser->current_frame.crc = byte;
            if (byte == parser->calculated_crc) {
                *out_frame = parser->current_frame;
                parser->state = STATE_PREAMBLE_1;
                return true; // Кадр успішно прийнято та верифіковано
            }
            parser->state = STATE_PREAMBLE_1;
            break;
    }
    return false;
}
