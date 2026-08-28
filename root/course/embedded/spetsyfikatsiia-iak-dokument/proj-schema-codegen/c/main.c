#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PROTO_SOF 0xAA
#define PROTO_EOF 0x55
#define PROTO_HEADER_LEN 6
#define PROTO_FOOTER_LEN 3
#define PROTO_MIN_FRAME_LEN (PROTO_HEADER_LEN + PROTO_FOOTER_LEN)

typedef enum {
    STATUS_OK = 0x00,
    ERR_INVALID_SOF = 0x01,
    ERR_INVALID_EOF = 0x02,
    ERR_INVALID_CRC = 0x03,
    ERR_INVALID_LEN = 0x04,
    ERR_UNKNOWN_MSG = 0x05
} proto_status_t;

typedef enum {
    MSG_CMD_PING = 0x01,
    MSG_CMD_SET_CONFIG = 0x02,
    MSG_TELEMETRY_REPORT = 0x20,
    MSG_CMD_RESPONSE = 0x80
} proto_msg_id_t;

typedef struct {
    int16_t temp_raw;
    uint16_t pressure_raw;
    uint16_t voltage_mv;
    uint8_t flags;
    uint8_t reserved;
} __attribute__((packed)) proto_telemetry_t;

static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

proto_status_t parse_telemetry_frame(const uint8_t *buf, size_t buf_len, proto_telemetry_t *out_data) {
    if (buf_len < PROTO_MIN_FRAME_LEN + sizeof(proto_telemetry_t)) {
        return ERR_INVALID_LEN;
    }
    if (buf[0] != PROTO_SOF) {
        return ERR_INVALID_SOF;
    }
    if (buf[buf_len - 1] != PROTO_EOF) {
        return ERR_INVALID_EOF;
    }

    uint8_t msg_id = buf[2];
    if (msg_id != MSG_TELEMETRY_REPORT) {
        return ERR_UNKNOWN_MSG;
    }

    uint16_t payload_len = (uint16_t)buf[4] | ((uint16_t)buf[5] << 8);
    if (payload_len != sizeof(proto_telemetry_t) || buf_len != PROTO_HEADER_LEN + payload_len + PROTO_FOOTER_LEN) {
        return ERR_INVALID_LEN;
    }

    // Перевірка CRC над заголовком і payload
    uint16_t expected_crc = (uint16_t)buf[buf_len - 3] | ((uint16_t)buf[buf_len - 2] << 8);
    uint16_t calculated_crc = crc16_ccitt(&buf[1], PROTO_HEADER_LEN - 1 + payload_len);
    if (calculated_crc != expected_crc) {
        return ERR_INVALID_CRC;
    }

    // Побайтове копіювання з явним порядком Little-Endian
    const uint8_t *p = &buf[PROTO_HEADER_LEN];
    out_data->temp_raw = (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
    out_data->pressure_raw = (uint16_t)p[2] | ((uint16_t)p[3] << 8);
    out_data->voltage_mv = (uint16_t)p[4] | ((uint16_t)p[5] << 8);
    out_data->flags = p[6];
    out_data->reserved = p[7];

    return STATUS_OK;
}
