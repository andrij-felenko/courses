#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

size_t ndef_build_uri_record(uint8_t prefix_code, const char *url_body, bool is_first, bool is_last, uint8_t *out_buf, size_t max_buf) {
    size_t body_len = strlen(url_body);
    size_t payload_len = 1 + body_len;
    bool is_short = (payload_len <= 255);

    size_t header_size = 1 + 1 + (is_short ? 1 : 4) + 1; // Flags + TypeLen + PayloadLen + Type('U')
    size_t total_size = header_size + payload_len;

    if (total_size > max_buf) return 0;

    uint8_t flags = 0x01; // TNF = Well-Known (0x01)
    if (is_first) flags |= 0x80;
    if (is_last)  flags |= 0x40;
    if (is_short) flags |= 0x10;

    size_t offset = 0;
    out_buf[offset++] = flags;
    out_buf[offset++] = 1; // Type Length = 1 ('U')

    if (is_short) {
        out_buf[offset++] = (uint8_t)payload_len;
    } else {
        out_buf[offset++] = (uint8_t)(payload_len >> 24);
        out_buf[offset++] = (uint8_t)(payload_len >> 16);
        out_buf[offset++] = (uint8_t)(payload_len >> 8);
        out_buf[offset++] = (uint8_t)(payload_len & 0xFF);
    }

    out_buf[offset++] = 'U'; // Record Type
    out_buf[offset++] = prefix_code; // URI Prefix Code

    memcpy(&out_buf[offset], url_body, body_len);
    offset += body_len;

    return offset;
}
