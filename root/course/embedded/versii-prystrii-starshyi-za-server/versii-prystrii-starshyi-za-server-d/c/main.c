#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define V1_MAGIC_BYTE     0xAA
#define V1_PROTOCOL_VER   0x01
#define V1_FRAME_LEN      16

typedef struct {
    uint32_t device_id;
    uint16_t sequence_id;
    uint32_t pulse_count;
    uint8_t  battery_code;
    bool     tamper_triggered;
    bool     reverse_flow_flag;
} legacy_meter_record_t;

typedef enum {
    DECODE_SUCCESS = 0,
    ERR_FRAME_TOO_SHORT,
    ERR_BAD_MAGIC_PREAMBLE,
    ERR_VERSION_MISMATCH,
    ERR_CRC_CHECKSUM_FAIL
} decode_status_t;

/* Обчислення контрольної суми CRC-16-CCITT (0x1021) */
static uint16_t calculate_crc16(const uint8_t *src, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)src[i] << 8;
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

decode_status_t decode_legacy_v1_frame(const uint8_t *buffer, size_t size, legacy_meter_record_t *out_record) {
    if (size < V1_FRAME_LEN) {
        return ERR_FRAME_TOO_SHORT;
    }

    if (buffer[0] != V1_MAGIC_BYTE) {
        return ERR_BAD_MAGIC_PREAMBLE;
    }

    if (buffer[1] != V1_PROTOCOL_VER) {
        return ERR_VERSION_MISMATCH;
    }

    /* Перевірка контрольної суми (останні 2 байти) */
    uint16_t received_crc = (uint16_t)((buffer[14] << 8) | buffer[15]);
    uint16_t computed_crc = calculate_crc16(buffer, 14);

    if (received_crc != computed_crc) {
        return ERR_CRC_CHECKSUM_FAIL;
    }

    /* Безпечне вилучення полів у форматі Big-Endian */
    out_record->device_id = ((uint32_t)buffer[2] << 24) |
                            ((uint32_t)buffer[3] << 16) |
                            ((uint32_t)buffer[4] << 8)  |
                            ((uint32_t)buffer[5]);

    out_record->sequence_id = (uint16_t)((buffer[6] << 8) | buffer[7]);

    out_record->pulse_count = ((uint32_t)buffer[8] << 24) |
                              ((uint32_t)buffer[9] << 16) |
                              ((uint32_t)buffer[10] << 8) |
                              ((uint32_t)buffer[11]);

    out_record->battery_code = buffer[12];
    
    uint8_t flags = buffer[13];
    out_record->tamper_triggered  = (flags & 0x01) != 0;
    out_record->reverse_flow_flag = (flags & 0x02) != 0;

    return DECODE_SUCCESS;
}
