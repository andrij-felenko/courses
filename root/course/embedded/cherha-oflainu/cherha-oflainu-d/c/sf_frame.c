#include "sf_frame.h"

#include <string.h>

/* CRC-32 IEEE 802.3, віддзеркалений поліном 0xEDB88320.
 * Побітово: таблиця на 256 входів з'їла б кілобайт флеші, а сканер
 * відновлення працює лічені десятки мілісекунд один раз за старт. */
uint32_t sf_crc32(const uint8_t *data, size_t len)
{
    uint32_t crc = 0xFFFFFFFFu;

    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; bit++) {
            uint32_t mask = (uint32_t)0 - (crc & 1u);
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }

    return ~crc;
}

size_t sf_frame_size(uint16_t payload_len)
{
    return SF_HDR_SIZE + (size_t)payload_len + SF_CRC_SIZE;
}

static void put_u16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)(v >> 8);
}

static void put_u32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)((v >> 8) & 0xFFu);
    p[2] = (uint8_t)((v >> 16) & 0xFFu);
    p[3] = (uint8_t)((v >> 24) & 0xFFu);
}

static void put_u64(uint8_t *p, uint64_t v)
{
    for (int i = 0; i < 8; i++) {
        p[i] = (uint8_t)((v >> (8 * i)) & 0xFFu);
    }
}

static uint16_t get_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t get_u32(const uint8_t *p)
{
    return (uint32_t)p[0]
         | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16)
         | ((uint32_t)p[3] << 24);
}

static uint64_t get_u64(const uint8_t *p)
{
    uint64_t v = 0;
    for (int i = 7; i >= 0; i--) {
        v = (v << 8) | p[i];
    }
    return v;
}

size_t sf_encode(uint8_t *dst, size_t dst_cap,
                 const sf_hdr_t *hdr, const uint8_t *payload)
{
    if (dst == NULL || hdr == NULL) {
        return 0;
    }
    if (hdr->len > SF_MAX_PAYLOAD) {
        return 0;
    }
    if (hdr->len > 0 && payload == NULL) {
        return 0;
    }

    const size_t total = sf_frame_size(hdr->len);
    if (dst_cap < total) {
        return 0;
    }

    put_u16(dst + 0, (uint16_t)SF_MAGIC);
    put_u32(dst + 2, hdr->seq);
    put_u64(dst + 6, hdr->ts_ms);
    put_u16(dst + 14, hdr->len);
    dst[16] = hdr->type;

    if (hdr->len > 0) {
        memcpy(dst + SF_HDR_SIZE, payload, hdr->len);
    }

    /* CRC накриває заголовок разом із навантаженням: інакше збита
     * довжина пройшла б перевірку й повела сканер у нікуди. */
    put_u32(dst + SF_HDR_SIZE + hdr->len,
            sf_crc32(dst, SF_HDR_SIZE + (size_t)hdr->len));

    return total;
}

sf_status_t sf_parse(const uint8_t *buf, size_t avail,
                     sf_hdr_t *out, size_t *out_total)
{
    if (buf == NULL || avail < 2) {
        return SF_ERR_TRUNCATED;
    }

    /* Стерта комірка NOR читається як 0xFF. Дві такі поспіль на місці
     * преамбули означають кінець записаного, а не пошкодження. */
    if (buf[0] == 0xFFu && buf[1] == 0xFFu) {
        return SF_ERR_ERASED;
    }

    if (get_u16(buf) != (uint16_t)SF_MAGIC) {
        return SF_ERR_MAGIC;
    }
    if (avail < SF_HDR_SIZE) {
        return SF_ERR_TRUNCATED;
    }

    const uint16_t len = get_u16(buf + 14);
    if (len > SF_MAX_PAYLOAD) {
        return SF_ERR_LENGTH;
    }

    const size_t total = sf_frame_size(len);
    if (avail < total) {
        /* Заголовок обіцяє більше байтів, ніж лишилось у секторі:
         * живлення зникло між записом заголовка й навантаження. */
        return SF_ERR_TRUNCATED;
    }

    const uint32_t stored = get_u32(buf + SF_HDR_SIZE + len);
    if (sf_crc32(buf, SF_HDR_SIZE + (size_t)len) != stored) {
        return SF_ERR_CRC;
    }

    if (out != NULL) {
        out->seq   = get_u32(buf + 2);
        out->ts_ms = get_u64(buf + 6);
        out->len   = len;
        out->type  = buf[16];
    }
    if (out_total != NULL) {
        *out_total = total;
    }

    return SF_OK;
}

bool sf_seq_after(uint32_t a, uint32_t b)
{
    return (int32_t)(a - b) > 0;
}
