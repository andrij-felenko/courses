#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define NDEF_FLAG_MB 0x80
#define NDEF_FLAG_ME 0x40
#define NDEF_FLAG_CF 0x20
#define NDEF_FLAG_SR 0x10
#define NDEF_FLAG_IL 0x08
#define NDEF_TNF_MASK 0x07

typedef enum {
    NDEF_OK = 0,
    NDEF_ERR_BUFFER_TOO_SMALL,
    NDEF_ERR_INVALID_HEADER,
    NDEF_ERR_UNSUPPORTED_TNF
} ndef_error_t;

typedef struct {
    uint8_t tnf;
    bool is_first;
    bool is_last;
    const uint8_t *type;
    uint8_t type_len;
    const uint8_t *id;
    uint8_t id_len;
    const uint8_t *payload;
    uint32_t payload_len;
} ndef_record_t;

static const char *URI_PREFIXES[] = {
    "",
    "http://www.",
    "https://www.",
    "http://",
    "https://",
    "tel:",
    "mailto:",
    "ftp://anonymous:anonymous@",
    "ftp://ftp.",
    "ftps://",
    "sftp://"
};
#define URI_PREFIX_COUNT (sizeof(URI_PREFIXES) / sizeof(URI_PREFIXES[0]))

ndef_error_t ndef_parse_record(const uint8_t *buf, size_t len, ndef_record_t *rec, size_t *parsed_bytes) {
    if (len < 2) return NDEF_ERR_BUFFER_TOO_SMALL;

    uint8_t header = buf[0];
    rec->is_first = (header & NDEF_FLAG_MB) != 0;
    rec->is_last = (header & NDEF_FLAG_ME) != 0;
    rec->tnf = header & NDEF_TNF_MASK;
    bool is_short = (header & NDEF_FLAG_SR) != 0;
    bool has_id = (header & NDEF_FLAG_IL) != 0;

    size_t offset = 1;

    rec->type_len = buf[offset++];
    
    if (is_short) {
        if (offset >= len) return NDEF_ERR_BUFFER_TOO_SMALL;
        rec->payload_len = buf[offset++];
    } else {
        if (offset + 4 > len) return NDEF_ERR_BUFFER_TOO_SMALL;
        rec->payload_len = ((uint32_t)buf[offset] << 24) |
                          ((uint32_t)buf[offset + 1] << 16) |
                          ((uint32_t)buf[offset + 2] << 8) |
                          ((uint32_t)buf[offset + 3]);
        offset += 4;
    }

    if (has_id) {
        if (offset >= len) return NDEF_ERR_BUFFER_TOO_SMALL;
        rec->id_len = buf[offset++];
    } else {
        rec->id_len = 0;
        rec->id = NULL;
    }

    if (offset + rec->type_len + rec->id_len + rec->payload_len > len) {
        return NDEF_ERR_BUFFER_TOO_SMALL;
    }

    rec->type = &buf[offset];
    offset += rec->type_len;

    if (has_id) {
        rec->id = &buf[offset];
        offset += rec->id_len;
    }

    rec->payload = &buf[offset];
    offset += rec->payload_len;

    *parsed_bytes = offset;
    return NDEF_OK;
}

size_t ndef_decode_uri(const ndef_record_t *rec, char *out_str, size_t out_max) {
    if (rec->tnf != 0x01 || rec->type_len != 1 || rec->type[0] != 'U') {
        return 0;
    }
    if (rec->payload_len < 1) return 0;

    uint8_t prefix_idx = rec->payload[0];
    const char *prefix = "";
    if (prefix_idx < URI_PREFIX_COUNT) {
        prefix = URI_PREFIXES[prefix_idx];
    }

    size_t prefix_len = strlen(prefix);
    size_t body_len = rec->payload_len - 1;

    if (prefix_len + body_len + 1 > out_max) return 0;

    memcpy(out_str, prefix, prefix_len);
    memcpy(out_str + prefix_len, &rec->payload[1], body_len);
    out_str[prefix_len + body_len] = '\0';

    return prefix_len + body_len;
}
