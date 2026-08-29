#include "log_format.h"

#include <string.h>

void log_put_u16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)((v >> 8) & 0xFFu);
}

void log_put_u32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)((v >> 8) & 0xFFu);
    p[2] = (uint8_t)((v >> 16) & 0xFFu);
    p[3] = (uint8_t)((v >> 24) & 0xFFu);
}

uint16_t log_get_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

uint32_t log_get_u32(const uint8_t *p)
{
    return (uint32_t)p[0]
         | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16)
         | ((uint32_t)p[3] << 24);
}

uint16_t log_crc16_ccitt(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu;

    /* Побітовий варіант: 8 ітерацій на байт. Таблиці на 512 байтів тут не
     * тримаємо — кадри короткі (десятки байтів), а ПЗП дорожче за такти. */
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000u) {
                crc = (uint16_t)((uint16_t)(crc << 1) ^ 0x1021u);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

void log_encode_sector_header(const sector_header_t *hdr, uint8_t out[SECTOR_HEADER_SIZE])
{
    log_put_u16(out + 0, hdr->magic);
    log_put_u16(out + 2, hdr->version);
    log_put_u32(out + 4, hdr->seq_num);
    log_put_u32(out + 8, hdr->erase_count);
    log_put_u32(out + SECTOR_STATE_OFFSET, hdr->state);
}

void log_decode_sector_header(const uint8_t in[SECTOR_HEADER_SIZE], sector_header_t *hdr)
{
    hdr->magic       = log_get_u16(in + 0);
    hdr->version     = log_get_u16(in + 2);
    hdr->seq_num     = log_get_u32(in + 4);
    hdr->erase_count = log_get_u32(in + 8);
    hdr->state       = log_get_u32(in + SECTOR_STATE_OFFSET);
}

size_t log_encode_record(const record_header_t *hdr, const uint8_t *payload,
                         uint8_t payload_len, uint8_t *out, size_t out_cap)
{
    if (payload_len > RECORD_MAX_PAYLOAD) {
        return 0;
    }
    if (payload_len > 0 && payload == NULL) {
        return 0;
    }

    const size_t total = RECORD_HEADER_SIZE + (size_t)payload_len + RECORD_CRC_SIZE;
    if (total > out_cap) {
        return 0;
    }

    log_put_u16(out + 0, LOG_RECORD_MAGIC);
    out[2] = (uint8_t)total;
    out[3] = hdr->level;
    out[4] = hdr->module_id;
    log_put_u32(out + 5, hdr->timestamp_ms);
    log_put_u32(out + 9, hdr->token_id);

    if (payload_len > 0) {
        memcpy(out + RECORD_HEADER_SIZE, payload, payload_len);
    }

    /* CRC покриває байти від поля довжини до останнього байта навантаження:
     * магічне число в неї не входить — воно й так перевіряється окремо. */
    const uint16_t crc = log_crc16_ccitt(out + 2, total - 4);
    log_put_u16(out + total - RECORD_CRC_SIZE, crc);

    return total;
}

bool log_decode_record(const uint8_t *raw, size_t avail, record_header_t *hdr,
                       const uint8_t **payload, uint8_t *payload_len)
{
    if (avail < RECORD_HEADER_SIZE + RECORD_CRC_SIZE) {
        return false;
    }
    if (log_get_u16(raw) != LOG_RECORD_MAGIC) {
        return false;
    }

    const uint8_t total = raw[2];
    if (total < RECORD_HEADER_SIZE + RECORD_CRC_SIZE || (size_t)total > avail) {
        return false;
    }

    const uint16_t stored = log_get_u16(raw + total - RECORD_CRC_SIZE);
    if (stored != log_crc16_ccitt(raw + 2, (size_t)total - 4)) {
        return false;
    }

    hdr->length       = total;
    hdr->level        = raw[3];
    hdr->module_id    = raw[4];
    hdr->timestamp_ms = log_get_u32(raw + 5);
    hdr->token_id     = log_get_u32(raw + 9);

    if (payload != NULL) {
        *payload = raw + RECORD_HEADER_SIZE;
    }
    if (payload_len != NULL) {
        *payload_len = (uint8_t)(total - RECORD_HEADER_SIZE - RECORD_CRC_SIZE);
    }
    return true;
}
