#include "sf_frame.h"

#include <string.h>

#include "sf_crc32.h"

static void put_le16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)(v >> 8);
}

static void put_le32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)((v >> 8) & 0xFFu);
    p[2] = (uint8_t)((v >> 16) & 0xFFu);
    p[3] = (uint8_t)((v >> 24) & 0xFFu);
}

static void put_le64(uint8_t *p, uint64_t v)
{
    put_le32(p, (uint32_t)(v & 0xFFFFFFFFu));
    put_le32(p + 4, (uint32_t)(v >> 32));
}

static uint16_t get_le16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t get_le32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t get_le64(const uint8_t *p)
{
    return (uint64_t)get_le32(p) | ((uint64_t)get_le32(p + 4) << 32);
}

uint32_t sf_frame_pack(uint8_t *dst, const sf_header_t *hdr, const void *payload)
{
    const uint32_t body = SF_HEADER_SIZE + (uint32_t)hdr->payload_len;
    const uint32_t stride = sf_frame_stride(hdr->payload_len);

    put_le16(dst + 0, SF_MAGIC);
    dst[2] = hdr->type;
    dst[3] = hdr->flags;
    put_le32(dst + 4, hdr->seq);
    put_le64(dst + 8, hdr->timestamp_ms);
    put_le16(dst + 16, hdr->payload_len);
    put_le16(dst + 18, hdr->reserved);

    memcpy(dst + SF_HEADER_SIZE, payload, hdr->payload_len);
    put_le32(dst + body, sf_crc32(dst, body));

    /* Вирівнювання пишемо одиницями: у NOR це «нічого не програмувати»,
     * комірка і так стерта, зайвих циклів запису не витрачаємо. */
    for (uint32_t i = body + SF_CRC_SIZE; i < stride; i++) {
        dst[i] = 0xFFu;
    }
    return stride;
}

bool sf_frame_parse_header(const uint8_t *src, sf_header_t *out)
{
    sf_header_t h;

    h.magic = get_le16(src + 0);
    if (h.magic != SF_MAGIC) {
        return false;
    }

    h.type = src[2];
    h.flags = src[3];
    h.seq = get_le32(src + 4);
    h.timestamp_ms = get_le64(src + 8);
    h.payload_len = get_le16(src + 16);
    h.reserved = get_le16(src + 18);

    /* Нульове навантаження чи довжина понад ліміт означає, що
     * преамбула збіглася випадково або запис обірвано посеред довжини. */
    if (h.payload_len == 0u || h.payload_len > SF_MAX_PAYLOAD) {
        return false;
    }

    *out = h;
    return true;
}

bool sf_frame_check_crc(const uint8_t *record, uint16_t payload_len)
{
    const uint32_t body = SF_HEADER_SIZE + (uint32_t)payload_len;
    return sf_crc32(record, body) == get_le32(record + body);
}

bool sf_frame_is_blank(const void *buf, uint32_t len)
{
    const uint8_t *p = (const uint8_t *)buf;

    for (uint32_t i = 0; i < len; i++) {
        if (p[i] != 0xFFu) {
            return false;
        }
    }
    return true;
}
