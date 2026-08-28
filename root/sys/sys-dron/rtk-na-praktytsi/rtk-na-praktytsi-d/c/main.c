#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define RTCM3_PREAMBLE           0xD3
#define RTCM3_MAX_PAYLOAD_SIZE   1023
#define RTCM3_HEADER_SIZE        3
#define RTCM3_CRC_SIZE           3
#define RTCM3_MAX_FRAME_SIZE     (RTCM3_HEADER_SIZE + RTCM3_MAX_PAYLOAD_SIZE + RTCM3_CRC_SIZE)

// Поліном CRC24 Qualcomm: x^24 + x^23 + x^18 + x^17 + x^14 + x^11 + x^10 + x^7 + x^6 + x^5 + x^4 + x^3 + x + 1
#define CRC24_QUALCOMM_POLY      0x01864CFBul

typedef enum {
    RTCM_STATE_WAIT_PREAMBLE,
    RTCM_STATE_GET_HEADER,
    RTCM_STATE_GET_PAYLOAD,
    RTCM_STATE_GET_CRC
} rtcm_parse_state_t;

typedef struct {
    uint16_t station_id;
    uint8_t  itrf_year;
    bool     has_gps;
    bool     has_glonass;
    bool     has_galileo;
    double   ecef_x; // у метрах
    double   ecef_y;
    double   ecef_z;
} rtcm_msg_1005_t;

typedef struct {
    rtcm_parse_state_t state;
    uint16_t payload_len;
    uint16_t bytes_read;
    uint8_t  frame_buf[RTCM3_MAX_FRAME_SIZE];
    uint32_t expected_crc;
} rtcm_parser_t;

// Розрахунок 24-бітного CRC Qualcomm
static uint32_t rtcm_crc24(const uint8_t *data, size_t len) {
    uint32_t crc = 0x00000000ul;
    for (size_t i = 0; i < len; i++) {
        crc ^= ((uint32_t)data[i]) << 16;
        for (int j = 0; j < 8; j++) {
            crc <<= 1;
            if (crc & 0x01000000ul) {
                crc ^= CRC24_QUALCOMM_POLY;
            }
        }
    }
    return crc & 0x00FFFFFFul;
}

// Допоміжне читання довільної кількості бітів з бітового потоку
static uint64_t get_bits(const uint8_t *buffer, size_t *bit_offset, uint8_t num_bits) {
    uint64_t result = 0;
    for (uint8_t i = 0; i < num_bits; i++) {
        size_t byte_idx = (*bit_offset) / 8;
        uint8_t bit_idx = 7 - ((*bit_offset) % 8);
        uint8_t bit_val = (buffer[byte_idx] >> bit_idx) & 1;
        result = (result << 1) | bit_val;
        (*bit_offset)++;
    }
    return result;
}

// Допоміжне читання знакового цілого у форматі доповняльного коду
static int64_t get_bits_signed(const uint8_t *buffer, size_t *bit_offset, uint8_t num_bits) {
    uint64_t val = get_bits(buffer, bit_offset, num_bits);
    if (val & ((uint64_t)1 << (num_bits - 1))) {
        val |= ~(((uint64_t)1 << num_bits) - 1);
    }
    return (int64_t)val;
}

void rtcm_parser_init(rtcm_parser_t *p) {
    p->state = RTCM_STATE_WAIT_PREAMBLE;
    p->payload_len = 0;
    p->bytes_read = 0;
    p->expected_crc = 0;
}

// Побайтовий розбір RTCM3 потоку. Повертає true, якщо прийнято повний валідний кадр
bool rtcm_parser_feed_byte(rtcm_parser_t *p, uint8_t byte) {
    switch (p->state) {
        case RTCM_STATE_WAIT_PREAMBLE:
            if (byte == RTCM3_PREAMBLE) {
                p->frame_buf[0] = byte;
                p->bytes_read = 1;
                p->state = RTCM_STATE_GET_HEADER;
            }
            break;

        case RTCM_STATE_GET_HEADER:
            p->frame_buf[p->bytes_read++] = byte;
            if (p->bytes_read == RTCM3_HEADER_SIZE) {
                // Біти 6..15 містять довжину корисного навантаження (10 біт)
                p->payload_len = ((p->frame_buf[1] & 0x03) << 8) | p->frame_buf[2];
                if (p->payload_len > RTCM3_MAX_PAYLOAD_SIZE) {
                    p->state = RTCM_STATE_WAIT_PREAMBLE; // некоректна довжина
                } else {
                    p->state = RTCM_STATE_GET_PAYLOAD;
                }
            }
            break;

        case RTCM_STATE_GET_PAYLOAD:
            p->frame_buf[p->bytes_read++] = byte;
            if (p->bytes_read == RTCM3_HEADER_SIZE + p->payload_len) {
                p->state = RTCM_STATE_GET_CRC;
            }
            break;

        case RTCM_STATE_GET_CRC:
            p->frame_buf[p->bytes_read++] = byte;
            if (p->bytes_read == RTCM3_HEADER_SIZE + p->payload_len + RTCM3_CRC_SIZE) {
                size_t total_len = p->bytes_read;
                size_t crc_idx = total_len - 3;
                uint32_t received_crc = ((uint32_t)p->frame_buf[crc_idx] << 16) |
                                        ((uint32_t)p->frame_buf[crc_idx + 1] << 8) |
                                        (uint32_t)p->frame_buf[crc_idx + 2];
                
                uint32_t computed_crc = rtcm_crc24(p->frame_buf, RTCM3_HEADER_SIZE + p->payload_len);
                p->state = RTCM_STATE_WAIT_PREAMBLE;

                if (received_crc == computed_crc) {
                    return true; // Кадр валідний
                }
            }
            break;
    }
    return false;
}

// Декодування повідомлення 1005 (Stationary Antenna Reference Point)
bool rtcm_decode_1005(const uint8_t *payload, size_t payload_len, rtcm_msg_1005_t *out_1005) {
    if (payload_len < 19) return false; // 1005 має розмір не менше 152 бітів (19 байтів)
    size_t bit_offset = 0;

    uint16_t msg_type = (uint16_t)get_bits(payload, &bit_offset, 12);
    if (msg_type != 1005) return false;

    out_1005->station_id = (uint16_t)get_bits(payload, &bit_offset, 12);
    out_1005->itrf_year = (uint8_t)get_bits(payload, &bit_offset, 6);
    out_1005->has_gps = (bool)get_bits(payload, &bit_offset, 1);
    out_1005->has_glonass = (bool)get_bits(payload, &bit_offset, 1);
    out_1005->has_galileo = (bool)get_bits(payload, &bit_offset, 1);
    bit_offset += 1; // Резервний біт

    // ECEF координати закодовано з кроком 0.0001 м (0.1 мм) у 38-бітних знакових числах
    int64_t raw_x = get_bits_signed(payload, &bit_offset, 38);
    bit_offset += 2; // Резерв
    int64_t raw_y = get_bits_signed(payload, &bit_offset, 38);
    bit_offset += 2; // Резерв
    int64_t raw_z = get_bits_signed(payload, &bit_offset, 38);

    out_1005->ecef_x = (double)raw_x * 0.0001;
    out_1005->ecef_y = (double)raw_y * 0.0001;
    out_1005->ecef_z = (double)raw_z * 0.0001;

    return true;
}
