#include <string.h>

#include "auth_frame.h"

/* Little-Endian на дроті — не покладаємося на порядок байтів хоста. */
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

static uint16_t get_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t get_u32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

uint16_t auth_crc16_ccitt(const uint8_t *data, size_t len, uint16_t seed)
{
    uint16_t crc = seed;

    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int bit = 0; bit < 8; ++bit) {
            if ((crc & 0x8000u) != 0u) {
                crc = (uint16_t)((uint16_t)(crc << 1) ^ 0x1021u);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

int auth_frame_encode(uint8_t *out, size_t cap,
                      const auth_header_t *hdr,
                      const void *payload, size_t payload_len)
{
    if (out == NULL || hdr == NULL) {
        return -1;
    }
    if (payload_len > AUTH_MAX_PAYLOAD || (payload_len > 0u && payload == NULL)) {
        return -1;
    }

    const size_t total = AUTH_HEADER_SIZE + payload_len;
    if (cap < total) {
        return -1;
    }

    out[0] = AUTH_MAGIC_BYTE;
    out[1] = AUTH_PROTO_VERSION;
    put_u16(&out[2], hdr->msg_id);
    out[4] = hdr->source_id;
    out[5] = hdr->target_id;
    put_u16(&out[6], hdr->seq_num);
    put_u32(&out[8], hdr->timestamp_ms);
    put_u32(&out[12], hdr->token_nonce);
    put_u16(&out[16], (uint16_t)payload_len);

    if (payload_len > 0u) {
        memcpy(&out[AUTH_HEADER_SIZE], payload, payload_len);
    }

    /* CRC накриває вісімнадцять байтів заголовка (усе, крім самого поля
       CRC) і все корисне навантаження. */
    uint16_t crc = auth_crc16_ccitt(out, 18u, 0xFFFFu);
    crc = auth_crc16_ccitt(&out[AUTH_HEADER_SIZE], payload_len, crc);
    put_u16(&out[18], crc);

    return (int)total;
}

auth_status_code_t auth_frame_decode(const uint8_t *frame, size_t len,
                                     auth_header_t *out, const uint8_t **payload)
{
    if (frame == NULL || out == NULL || len < AUTH_HEADER_SIZE) {
        return AUTH_ERR_BAD_LENGTH;
    }
    if (frame[0] != AUTH_MAGIC_BYTE) {
        return AUTH_ERR_BAD_MAGIC;
    }
    if (frame[1] != AUTH_PROTO_VERSION) {
        return AUTH_ERR_BAD_VERSION;
    }

    const uint16_t plen = get_u16(&frame[16]);
    if (plen > AUTH_MAX_PAYLOAD || (size_t)plen + AUTH_HEADER_SIZE > len) {
        return AUTH_ERR_BAD_LENGTH;
    }

    uint16_t crc = auth_crc16_ccitt(frame, 18u, 0xFFFFu);
    crc = auth_crc16_ccitt(&frame[AUTH_HEADER_SIZE], plen, crc);
    if (crc != get_u16(&frame[18])) {
        return AUTH_ERR_CRC_MISMATCH;
    }

    out->magic        = frame[0];
    out->version      = frame[1];
    out->msg_id       = get_u16(&frame[2]);
    out->source_id    = frame[4];
    out->target_id    = frame[5];
    out->seq_num      = get_u16(&frame[6]);
    out->timestamp_ms = get_u32(&frame[8]);
    out->token_nonce  = get_u32(&frame[12]);
    out->payload_len  = plen;
    out->crc16        = get_u16(&frame[18]);

    if (payload != NULL) {
        *payload = &frame[AUTH_HEADER_SIZE];
    }
    return AUTH_STATUS_OK;
}

long auth_frame_sync(const uint8_t *buf, size_t len)
{
    if (buf == NULL) {
        return -1;
    }
    for (size_t i = 0; i < len; ++i) {
        if (buf[i] != AUTH_MAGIC_BYTE) {
            continue;
        }
        /* Другий байт уже видно — відкидаємо випадкове 0xAA всередині даних. */
        if (i + 1u < len && buf[i + 1u] != AUTH_PROTO_VERSION) {
            continue;
        }
        return (long)i;
    }
    return -1;
}

uint32_t auth_sign_override(uint32_t key, uint8_t src, uint16_t seq, uint32_t ts)
{
    uint8_t buf[11];

    put_u32(&buf[0], key);
    buf[4] = src;
    put_u16(&buf[5], seq);
    put_u32(&buf[7], ts);

    /* FNV-1a: дешево й детерміновано з обох боків каналу. */
    uint32_t hash = 2166136261u;
    for (size_t i = 0; i < sizeof buf; ++i) {
        hash ^= (uint32_t)buf[i];
        hash *= 16777619u;
    }
    return hash;
}
