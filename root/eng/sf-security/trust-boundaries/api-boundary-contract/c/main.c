#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define BOUNDARY_MAGIC      0x5345
#define BOUNDARY_VERSION    1
#define MAX_PAYLOAD_SIZE    4096

typedef enum {
    GATEWAY_OK = 0,
    ERR_BAD_MAGIC = 1,
    ERR_UNSUPPORTED_VERSION = 2,
    ERR_PAYLOAD_TOO_LARGE = 3,
    ERR_CHECKSUM_MISMATCH = 4,
    ERR_SCHEMA_VIOLATION = 5,
    ERR_CANONICALIZATION_FAIL = 6,
    ERR_ACCESS_DENIED = 7
} GatewayErrorCode;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint16_t version;
    uint16_t opcode;
    uint16_t flags;
    uint32_t sequence_id;
    uint32_t payload_len;
} BoundaryFrameHeader;
#pragma pack(pop)

typedef struct {
    BoundaryFrameHeader header;
    uint8_t payload[MAX_PAYLOAD_SIZE];
    uint32_t checksum;
} ParsedBoundaryMessage;

/* Простий генератор CRC32 для ілюстрації верифікації */
static uint32_t compute_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

/* Інтерфейсний контракт валідації вхідного бінарного кадру */
GatewayErrorCode validate_boundary_frame(
    const uint8_t *raw_stream,
    size_t stream_len,
    ParsedBoundaryMessage *out_msg
) {
    if (raw_stream == NULL || out_msg == NULL) {
        return ERR_SCHEMA_VIOLATION;
    }

    /* 1. Перевірка мінімального розміру для розміщення заголовка та CRC */
    if (stream_len < sizeof(BoundaryFrameHeader) + sizeof(uint32_t)) {
        return ERR_SCHEMA_VIOLATION;
    }

    /* 2. Копіювання заголовка у локальну пам'ять (Single Copy) */
    BoundaryFrameHeader local_hdr;
    memcpy(&local_hdr, raw_stream, sizeof(BoundaryFrameHeader));

    /* 3. Валідація магічного числа та версії */
    if (local_hdr.magic != BOUNDARY_MAGIC) {
        return ERR_BAD_MAGIC;
    }
    if (local_hdr.version != BOUNDARY_VERSION) {
        return ERR_UNSUPPORTED_VERSION;
    }

    /* 4. Контроль довжини корисного навантаження */
    if (local_hdr.payload_len > MAX_PAYLOAD_SIZE) {
        return ERR_PAYLOAD_TOO_LARGE;
    }

    size_t expected_total_size = sizeof(BoundaryFrameHeader) + local_hdr.payload_len + sizeof(uint32_t);
    if (stream_len < expected_total_size) {
        return ERR_SCHEMA_VIOLATION;
    }

    /* 5. Перевірка контрольної суми */
    uint32_t expected_crc = compute_crc32(raw_stream, sizeof(BoundaryFrameHeader) + local_hdr.payload_len);
    uint32_t packet_crc;
    memcpy(&packet_crc, raw_stream + sizeof(BoundaryFrameHeader) + local_hdr.payload_len, sizeof(uint32_t));

    if (expected_crc != packet_crc) {
        return ERR_CHECKSUM_MISMATCH;
    }

    /* 6. Заповнення безпечного типізованого об'єкта */
    out_msg->header = local_hdr;
    memcpy(out_msg->payload, raw_stream + sizeof(BoundaryFrameHeader), local_hdr.payload_len);
    out_msg->checksum = packet_crc;

    return GATEWAY_OK;
}
