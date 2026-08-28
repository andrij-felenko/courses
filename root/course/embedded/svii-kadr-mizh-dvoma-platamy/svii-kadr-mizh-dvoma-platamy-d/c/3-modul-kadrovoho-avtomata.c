typedef enum {
    FSM_STATE_IDLE,
    FSM_STATE_RECEIVE,
    FSM_STATE_OVERFLOW
} FsmState_t;

typedef enum {
    FRAME_OK = 0,
    FRAME_ERR_CRC,
    FRAME_ERR_LENGTH,
    FRAME_ERR_COBS
} FrameStatus_t;

// Зворотний виклик при успішному прийомі валідного кадру
typedef void (*FrameCallback_t)(const FrameHeader_t *header, 
                                const uint8_t *payload, 
                                size_t payload_len);

typedef struct {
    FsmState_t       state;
    uint8_t          rx_buf[PROTOCOL_MAX_ENCODED];
    size_t           rx_len;
    FrameCallback_t  on_frame;
    uint32_t         frames_received;
    uint32_t         crc_errors;
    uint32_t         overflow_errors;
} FramingParser_t;

void framing_parser_init(FramingParser_t *parser, FrameCallback_t callback) {
    if (!parser) return;
    parser->state = FSM_STATE_IDLE;
    parser->rx_len = 0;
    parser->on_frame = callback;
    parser->frames_received = 0;
    parser->crc_errors = 0;
    parser->overflow_errors = 0;
}

static void framing_parser_process_packet(FramingParser_t *parser) {
    if (parser->rx_len < 2) return; // Занадто короткий для валідного COBS

    // Розпаковуємо прямо в тому самому буфері (in-place)
    size_t decoded_len = cobs_decode(parser->rx_buf, parser->rx_len, parser->rx_buf);
    if (decoded_len < sizeof(FrameHeader_t) + sizeof(uint16_t)) {
        parser->crc_errors++;
        return;
    }

    // Перевіряємо CRC-16
    uint16_t calculated_crc = crc16_calculate(parser->rx_buf, decoded_len - sizeof(uint16_t));
    uint16_t received_crc = (uint16_t)parser->rx_buf[decoded_len - 2] |
                           ((uint16_t)parser->rx_buf[decoded_len - 1] << 8);

    if (calculated_crc != received_crc) {
        parser->crc_errors++;
        return;
    }

    const FrameHeader_t *hdr = (const FrameHeader_t *)parser->rx_buf;
    const uint8_t *payload = parser->rx_buf + sizeof(FrameHeader_t);
    size_t actual_payload_len = decoded_len - sizeof(FrameHeader_t) - sizeof(uint16_t);

    if (hdr->payload_len != actual_payload_len) {
        parser->crc_errors++;
        return;
    }

    parser->frames_received++;
    if (parser->on_frame) {
        parser->on_frame(hdr, payload, actual_payload_len);
    }
}

// Побайтовий ввід у автомат (викликається в ISR або з черги)
void framing_parser_feed_byte(FramingParser_t *parser, uint8_t byte) {
    if (!parser) return;

    if (byte == 0x00) {
        // Зустріли розділювач кадру
        if (parser->state == FSM_STATE_RECEIVE) {
            framing_parser_process_packet(parser);
        }
        parser->state = FSM_STATE_IDLE;
        parser->rx_len = 0;
        return;
    }

    switch (parser->state) {
        case FSM_STATE_IDLE:
            parser->rx_len = 0;
            parser->rx_buf[parser->rx_len++] = byte;
            parser->state = FSM_STATE_RECEIVE;
            break;

        case FSM_STATE_RECEIVE:
            if (parser->rx_len < PROTOCOL_MAX_ENCODED) {
                parser->rx_buf[parser->rx_len++] = byte;
            } else {
                parser->overflow_errors++;
                parser->state = FSM_STATE_OVERFLOW;
            }
            break;

        case FSM_STATE_OVERFLOW:
            // Чекаємо 0x00, ігноруючи поточні байти
            break;
    }
}
