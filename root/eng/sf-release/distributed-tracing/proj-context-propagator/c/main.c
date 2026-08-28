#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TRACEPARENT_LEN 55
#define TRACE_ID_BYTES 16
#define SPAN_ID_BYTES 8

#define FLAG_RECORDED 0x01

typedef struct {
    uint8_t version;
    uint8_t trace_id[TRACE_ID_BYTES];
    uint8_t span_id[SPAN_ID_BYTES];
    uint8_t flags;
} trace_context_t;

/* Таблиця для швидкого декодування hex символів у 4-бітне значення */
static const int8_t hex_table[256] = {
    ['0'] = 0, ['1'] = 1, ['2'] = 2, ['3'] = 3, ['4'] = 4,
    ['5'] = 5, ['6'] = 6, ['7'] = 7, ['8'] = 8, ['9'] = 9,
    ['a'] = 10, ['b'] = 11, ['c'] = 12, ['d'] = 13, ['e'] = 14, ['f'] = 15,
    ['A'] = 10, ['B'] = 11, ['C'] = 12, ['D'] = 13, ['E'] = 14, ['F'] = 15,
    [0 ... '0' - 1] = -1,
    ['9' + 1 ... 'A' - 1] = -1,
    ['F' + 1 ... 'a' - 1] = -1,
    ['f' + 1 ... 255] = -1
};

static bool decode_hex_bytes(const char *src, size_t hex_len, uint8_t *dst) {
    for (size_t i = 0; i < hex_len; i += 2) {
        int8_t hi = hex_table[(uint8_t)src[i]];
        int8_t lo = hex_table[(uint8_t)src[i + 1]];
        if (hi < 0 || lo < 0) {
            return false;
        }
        dst[i / 2] = (uint8_t)((hi << 4) | lo);
    }
    return true;
}

static bool is_all_zeros(const uint8_t *data, size_t len) {
    uint8_t acc = 0;
    for (size_t i = 0; i < len; ++i) {
        acc |= data[i];
    }
    return acc == 0;
}

bool parse_traceparent(const char *header_val, size_t len, trace_context_t *out_ctx) {
    if (!header_val || len < TRACEPARENT_LEN) {
        return false;
    }

    /* Перевірка дефісів-розділювачів */
    if (header_val[2] != '-' || header_val[35] != '-' || header_val[52] != '-') {
        return false;
    }

    /* 1. Декодування версії */
    int8_t v_hi = hex_table[(uint8_t)header_val[0]];
    int8_t v_lo = hex_table[(uint8_t)header_val[1]];
    if (v_hi < 0 || v_lo < 0) return false;
    uint8_t ver = (uint8_t)((v_hi << 4) | v_lo);

    if (ver == 0xFF) {
        return false; /* Версія ff заборонена стандартом */
    }

    /* Для версії 00 довжина повинна бути строго 55 символів */
    if (ver == 0x00 && len != TRACEPARENT_LEN) {
        return false;
    }

    /* 2. Декодування Trace ID (32 hex -> 16 байтів) */
    uint8_t trace_id[TRACE_ID_BYTES];
    if (!decode_hex_bytes(header_val + 3, 32, trace_id)) {
        return false;
    }
    if (is_all_zeros(trace_id, TRACE_ID_BYTES)) {
        return false;
    }

    /* 3. Декодування Parent/Span ID (16 hex -> 8 байтів) */
    uint8_t span_id[SPAN_ID_BYTES];
    if (!decode_hex_bytes(header_val + 36, 16, span_id)) {
        return false;
    }
    if (is_all_zeros(span_id, SPAN_ID_BYTES)) {
        return false;
    }

    /* 4. Декодування прапорців (2 hex -> 1 байт) */
    int8_t f_hi = hex_table[(uint8_t)header_val[53]];
    int8_t f_lo = hex_table[(uint8_t)header_val[54]];
    if (f_hi < 0 || f_lo < 0) return false;
    uint8_t flags = (uint8_t)((f_hi << 4) | f_lo);

    out_ctx->version = ver;
    memcpy(out_ctx->trace_id, trace_id, TRACE_ID_BYTES);
    memcpy(out_ctx->span_id, span_id, SPAN_ID_BYTES);
    out_ctx->flags = flags;
    return true;
}

bool format_traceparent(const trace_context_t *ctx, char *out_buf, size_t buf_size) {
    if (!ctx || !out_buf || buf_size < (TRACEPARENT_LEN + 1)) {
        return false;
    }

    static const char hex_digits[] = "0123456789abcdef";
    char *p = out_buf;

    /* Версія */
    *p++ = hex_digits[(ctx->version >> 4) & 0x0F];
    *p++ = hex_digits[ctx->version & 0x0F];
    *p++ = '-';

    /* Trace ID */
    for (size_t i = 0; i < TRACE_ID_BYTES; ++i) {
        *p++ = hex_digits[(ctx->trace_id[i] >> 4) & 0x0F];
        *p++ = hex_digits[ctx->trace_id[i] & 0x0F];
    }
    *p++ = '-';

    /* Span ID */
    for (size_t i = 0; i < SPAN_ID_BYTES; ++i) {
        *p++ = hex_digits[(ctx->span_id[i] >> 4) & 0x0F];
        *p++ = hex_digits[ctx->span_id[i] & 0x0F];
    }
    *p++ = '-';

    /* Flags */
    *p++ = hex_digits[(ctx->flags >> 4) & 0x0F];
    *p++ = hex_digits[ctx->flags & 0x0F];
    *p = '\0';

    return true;
}
