#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PAYLOAD_SIZE        128U
#define PROTOCOL_MAGIC_BYTE     0x5AU
#define ERROR_INVALID_FRAME     0xE1U
#define ERROR_BUFFER_OVERFLOW   0xE2U
#define ERROR_AUTH_FAILED       0xE3U

typedef struct {
    uint8_t  magic;
    uint8_t  seq_num;
    uint16_t length;
    uint8_t  payload[MAX_PAYLOAD_SIZE];
    uint32_t checksum_crc32;
} __attribute__((packed)) secure_frame_t;

/* Простий апаратний або програмний розрахунок CRC-32 */
uint32_t calculate_crc32(const uint8_t *data, size_t len);

/* Безпечний розбір вхідного кадру від невідомого співпроцесора */
int32_t parse_untrusted_frame(const uint8_t *raw_buf, size_t raw_len, uint8_t *out_payload, size_t *out_len) {
    if (raw_buf == NULL || out_payload == NULL || out_len == NULL) {
        return -ERROR_INVALID_FRAME;
    }

    /* 1. Перевірка мінімальної довжини заголовка */
    if (raw_len < (sizeof(secure_frame_t) - MAX_PAYLOAD_SIZE)) {
        return -ERROR_INVALID_FRAME;
    }

    const secure_frame_t *frame = (const secure_frame_t *)raw_buf;

    /* 2. Перевірка магічного байта протоколу */
    if (frame->magic != PROTOCOL_MAGIC_BYTE) {
        return -ERROR_INVALID_FRAME;
    }

    /* 3. Жорсткий контроль меж розміру корисного навантаження */
    if (frame->length > MAX_PAYLOAD_SIZE || frame->length > (raw_len - 8U)) {
        return -ERROR_BUFFER_OVERFLOW;
    }

    /* 4. Перевірка контрольної суми кадру */
    uint32_t expected_crc = calculate_crc32(raw_buf, sizeof(secure_frame_t) - sizeof(uint32_t));
    if (frame->checksum_crc32 != expected_crc) {
        return -ERROR_AUTH_FAILED;
    }

    /* 5. Безпечне копіювання з контрольованим розміром */
    memcpy(out_payload, frame->payload, frame->length);
    *out_len = frame->length;

    return 0; /* Успішно розібрано */
}
