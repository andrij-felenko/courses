#include <stdint.h>
#include <stdbool.h>

#define GATEWAY_SOF_BYTE 0x00

typedef enum {
    OP_DISCOVERY          = 0x01,
    OP_DISCOVERY_RESP     = 0x81,
    OP_AUTH_CHALLENGE     = 0x02,
    OP_AUTH_RESP          = 0x82,
    OP_MANIFEST_NEGOTIATE = 0x03,
    OP_MANIFEST_ACK       = 0x83,
    OP_PUSH_CHUNK         = 0x04,
    OP_CHUNK_ACK          = 0x84,
    OP_COMMIT_AND_TEST    = 0x05,
    OP_COMMIT_RESP        = 0x85
} gateway_opcode_t;

typedef struct __attribute__((packed)) {
    uint8_t  seq_id;
    uint8_t  opcode;
    uint16_t payload_len;
} gateway_frame_hdr_t;

typedef struct __attribute__((packed)) {
    uint32_t target_version;
    uint32_t total_payload_size;
    uint16_t chunk_size;
    uint8_t  full_sha256[32];
    uint8_t  signature_ed25519[64];
} manifest_payload_t;

typedef struct __attribute__((packed)) {
    uint16_t chunk_index;
    uint16_t chunk_crc16;
    uint8_t  data[256];
} chunk_payload_t;

/* Обробка отриманого розпакованого кадру */
void handle_gateway_packet(const gateway_frame_hdr_t *hdr,
                           const uint8_t *payload,
                           uint32_t calculated_crc,
                           uint32_t expected_crc) {
    if (calculated_crc != expected_crc) {
        /* Кадр пошкоджено — скидаємо лічильник і не відповідаємо */
        return;
    }

    switch (hdr->opcode) {
        case OP_MANIFEST_NEGOTIATE: {
            const manifest_payload_t *manifest = (const manifest_payload_t *)payload;
            /* Перевірка апаратних обмежень та валідація версії */
            (void)manifest;
            break;
        }
        case OP_PUSH_CHUNK: {
            const chunk_payload_t *chunk = (const chunk_payload_t *)payload;
            /* Запис сектору у Flash B */
            (void)chunk;
            break;
        }
        default:
            break;
    }
}
