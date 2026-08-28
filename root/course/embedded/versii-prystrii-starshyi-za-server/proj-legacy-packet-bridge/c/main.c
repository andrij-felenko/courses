#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define LEGACY_FRAME_MAGIC    0xAA
#define LEGACY_FRAME_VERSION  0x01
#define LEGACY_FRAME_SIZE     16

#define LEGACY_CMD_MAGIC      0x55
#define LEGACY_CMD_SIZE       6

typedef struct {
    uint32_t device_id;
    uint16_t seq_num;
    uint32_t raw_pulses;
    uint8_t  battery_raw;
    bool     tamper_alarm;
    bool     reverse_flow;
} legacy_telemetry_t;

typedef enum {
    PARSE_OK = 0,
    PARSE_ERR_BUFFER_TOO_SMALL,
    PARSE_ERR_INVALID_MAGIC,
    PARSE_ERR_UNSUPPORTED_VERSION,
    PARSE_ERR_CRC_MISMATCH
} parse_result_t;

/* Обчислення контрольної суми CRC-16-CCITT (Поліном 0x1021, init 0xFFFF) */
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/* Безпечне вилучення 16-бітного цілого в форматі Big-Endian */
static inline uint16_t read_be16(const uint8_t *p) {
    return (uint16_t)((p[0] << 8) | p[1]);
}

/* Безпечне вилучення 32-бітного цілого в форматі Big-Endian */
static inline uint32_t read_be32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) |
           ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8)  |
           ((uint32_t)p[3]);
}

/* Безпечний запис 16-бітного цілого в форматі Big-Endian */
static inline void write_be16(uint8_t *p, uint16_t val) {
    p[0] = (uint8_t)(val >> 8);
    p[1] = (uint8_t)(val & 0xFF);
}

parse_result_t legacy_parse_telemetry(const uint8_t *buf, size_t len, legacy_telemetry_t *out) {
    if (len < LEGACY_FRAME_SIZE) {
        return PARSE_ERR_BUFFER_TOO_SMALL;
    }

    if (buf[0] != LEGACY_FRAME_MAGIC) {
        return PARSE_ERR_INVALID_MAGIC;
    }

    if (buf[1] != LEGACY_FRAME_VERSION) {
        return PARSE_ERR_UNSUPPORTED_VERSION;
    }

    /* Верифікація CRC16 для байтів заголовка та корисного навантаження (0..13) */
    uint16_t expected_crc = read_be16(&buf[14]);
    uint16_t actual_crc = crc16_ccitt(buf, 14);
    if (expected_crc != actual_crc) {
        return PARSE_ERR_CRC_MISMATCH;
    }

    /* Розпакування полів без ризику непарного вирівнювання пам'яті */
    out->device_id   = read_be32(&buf[2]);
    out->seq_num     = read_be16(&buf[6]);
    out->raw_pulses  = read_be32(&buf[8]);
    out->battery_raw = buf[12];
    
    uint8_t flags    = buf[13];
    out->tamper_alarm = (flags & 0x01) != 0;
    out->reverse_flow = (flags & 0x02) != 0;

    return PARSE_OK;
}

bool legacy_build_command(uint8_t cmd_type, uint16_t param, uint8_t *out_buf, size_t out_capacity) {
    if (out_capacity < LEGACY_CMD_SIZE) {
        return false;
    }

    out_buf[0] = LEGACY_CMD_MAGIC;
    out_buf[1] = cmd_type;
    write_be16(&out_buf[2], param);

    uint16_t crc = crc16_ccitt(out_buf, 4);
    write_be16(&out_buf[4], crc);

    return true;
}
