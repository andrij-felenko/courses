#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RECORD_MAGIC 0xAA55
#define MAX_PAYLOAD_SIZE 512

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint8_t  type;
    uint8_t  flags;
    uint32_t seq;
    uint64_t timestamp_ms;
    uint16_t payload_len;
    uint16_t reserved;
} record_hdr_t;
#pragma pack(pop)

// Обчислення CRC-32 (IEEE 802.3)
uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    while (len--) {
        crc ^= *data++;
        for (int i = 0; i < 8; i++) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1)));
        }
    }
    return ~crc;
}

// Перевірка цілісності запису, зчитаного з Flash
bool validate_flash_record(const uint8_t *raw_buf, size_t buf_len, record_hdr_t *out_hdr) {
    if (buf_len < sizeof(record_hdr_t) + sizeof(uint32_t)) {
        return false;
    }

    const record_hdr_t *hdr = (const record_hdr_t *)raw_buf;
    if (hdr->magic != RECORD_MAGIC) {
        return false; // Немає преамбули або область стерта (0xFF)
    }

    if (hdr->payload_len > MAX_PAYLOAD_SIZE) {
        return false; // Пошкоджена довжина
    }

    size_t total_record_len = sizeof(record_hdr_t) + hdr->payload_len + sizeof(uint32_t);
    if (buf_len < total_record_len) {
        return false;
    }

    // Вичитуємо збережений у кінці кадру CRC
    uint32_t stored_crc;
    memcpy(&stored_crc, raw_buf + total_record_len - sizeof(uint32_t), sizeof(uint32_t));

    // Рахуємо CRC для заголовка та корисного навантаження
    uint32_t calculated_crc = calc_crc32(raw_buf, total_record_len - sizeof(uint32_t));
    if (calculated_crc != stored_crc) {
        return false; // Помилка CRC — запис був перерваний аварійним вимкненням
    }

    if (out_hdr) {
        *out_hdr = *hdr;
    }
    return true;
}
