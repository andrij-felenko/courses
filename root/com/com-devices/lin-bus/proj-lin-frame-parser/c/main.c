#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define LIN_MAX_DATA_BYTES 8

typedef enum {
    LIN_CHECKSUM_CLASSIC,
    LIN_CHECKSUM_ENHANCED
} lin_checksum_type_t;

typedef enum {
    LIN_STATE_WAIT_BREAK,
    LIN_STATE_WAIT_SYNC,
    LIN_STATE_WAIT_PID,
    LIN_STATE_WAIT_DATA,
    LIN_STATE_WAIT_CHECKSUM
} lin_parser_state_t;

typedef struct {
    uint8_t id;
    uint8_t pid;
    uint8_t data[LIN_MAX_DATA_BYTES];
    uint8_t data_len;
    uint8_t checksum;
    bool valid;
} lin_frame_t;

typedef struct {
    lin_parser_state_t state;
    lin_frame_t current_frame;
    uint8_t data_index;
    lin_checksum_type_t checksum_type;
} lin_parser_t;

// Обчислення бітів паритету P0 та P1 для ID (0x00..0x3F)
static inline uint8_t lin_calc_pid(uint8_t id) {
    uint8_t id_clean = id & 0x3F;
    uint8_t p0 = ((id_clean >> 0) ^ (id_clean >> 1) ^ (id_clean >> 2) ^ (id_clean >> 4)) & 0x01;
    uint8_t p1 = ~((id_clean >> 1) ^ (id_clean >> 3) ^ (id_clean >> 4) ^ (id_clean >> 5)) & 0x01;
    return id_clean | (p0 << 6) | (p1 << 7);
}

// Перевірка коректності байта PID
static inline bool lin_verify_pid(uint8_t pid) {
    uint8_t id = pid & 0x3F;
    return lin_calc_pid(id) == pid;
}

// Обчислення контрольної суми LIN (Classic або Enhanced)
static uint8_t lin_calc_checksum(uint8_t pid, const uint8_t *data, uint8_t len, lin_checksum_type_t type) {
    uint16_t sum = 0;
    
    if (type == LIN_CHECKSUM_ENHANCED) {
        sum += pid;
    }
    
    for (uint8_t i = 0; i < len; ++i) {
        sum += data[i];
        if (sum > 0xFF) {
            sum = (sum & 0xFF) + 1;
        }
    }
    
    return (uint8_t)(~sum & 0xFF);
}

// Ініціалізація парсера
void lin_parser_init(lin_parser_t *parser, lin_checksum_type_t type) {
    if (!parser) return;
    parser->state = LIN_STATE_WAIT_BREAK;
    parser->checksum_type = type;
    parser->data_index = 0;
    parser->current_frame.valid = false;
}

// Повідомлення парсера про фіксацію сигналу Break
void lin_parser_on_break(lin_parser_t *parser) {
    if (!parser) return;
    parser->state = LIN_STATE_WAIT_SYNC;
    parser->data_index = 0;
    parser->current_frame.valid = false;
}

// Обробка одного байта, отриманого з UART
bool lin_parser_process_byte(lin_parser_t *parser, uint8_t byte, uint8_t expected_data_len) {
    if (!parser) return false;

    switch (parser->state) {
        case LIN_STATE_WAIT_BREAK:
            // Очікування Break триває; звичайні байти ігноруються
            break;

        case LIN_STATE_WAIT_SYNC:
            if (byte == 0x55) {
                parser->state = LIN_STATE_WAIT_PID;
            } else {
                parser->state = LIN_STATE_WAIT_BREAK;
            }
            break;

        case LIN_STATE_WAIT_PID:
            if (lin_verify_pid(byte)) {
                parser->current_frame.pid = byte;
                parser->current_frame.id = byte & 0x3F;
                parser->current_frame.data_len = (expected_data_len > LIN_MAX_DATA_BYTES) ? 
                                                  LIN_MAX_DATA_BYTES : expected_data_len;
                parser->data_index = 0;
                parser->state = LIN_STATE_WAIT_DATA;
            } else {
                parser->state = LIN_STATE_WAIT_BREAK;
            }
            break;

        case LIN_STATE_WAIT_DATA:
            parser->current_frame.data[parser->data_index++] = byte;
            if (parser->data_index >= parser->current_frame.data_len) {
                parser->state = LIN_STATE_WAIT_CHECKSUM;
            }
            break;

        case LIN_STATE_WAIT_CHECKSUM:
            parser->current_frame.checksum = byte;
            // Для діагностичних кадрів 0x3C та 0x3D завжди Classic Checksum
            lin_checksum_type_t active_type = parser->checksum_type;
            if (parser->current_frame.id == 0x3C || parser->current_frame.id == 0x3D) {
                active_type = LIN_CHECKSUM_CLASSIC;
            }

            uint8_t calculated = lin_calc_checksum(parser->current_frame.pid,
                                                   parser->current_frame.data,
                                                   parser->current_frame.data_len,
                                                   active_type);
            
            parser->current_frame.valid = (calculated == byte);
            parser->state = LIN_STATE_WAIT_BREAK;
            return parser->current_frame.valid;
    }

    return false;
}
