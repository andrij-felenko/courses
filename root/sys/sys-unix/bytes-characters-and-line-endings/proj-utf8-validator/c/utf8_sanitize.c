/* utf8_sanitize.c — Валідатор UTF-8 та нормалізатор кінців рядків.
 * Збірка: cc -std=c99 -Wall -Wextra -O2 utf8_sanitize.c -o utf8_sanitize
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    UTF8_OK = 0,
    UTF8_ERR_INVALID_BYTE,
    UTF8_ERR_OVERLONG,
    UTF8_ERR_SURROGATE,
    UTF8_ERR_OUT_OF_RANGE,
    UTF8_ERR_TRUNCATED
} utf8_error_t;

/* Декодує одну кодову точку. Повертає кількість спожитих байтів (1..4) або 0 при помилці. */
static size_t utf8_decode_codepoint(const uint8_t *buf, size_t len, uint32_t *out_cp, utf8_error_t *err) {
    if (len == 0) {
        *err = UTF8_ERR_TRUNCATED;
        return 0;
    }

    uint8_t b0 = buf[0];
    if (b0 < 0x80) {
        *out_cp = b0;
        *err = UTF8_OK;
        return 1;
    }

    if ((b0 & 0xE0) == 0xC0) {
        if (len < 2) { *err = UTF8_ERR_TRUNCATED; return 0; }
        uint8_t b1 = buf[1];
        if ((b1 & 0xC0) != 0x80) { *err = UTF8_ERR_INVALID_BYTE; return 0; }
        
        uint32_t cp = ((b0 & 0x1F) << 6) | (b1 & 0x3F);
        if (cp < 0x80) { *err = UTF8_ERR_OVERLONG; return 0; }
        
        *out_cp = cp;
        *err = UTF8_OK;
        return 2;
    }

    if ((b0 & 0xF0) == 0xE0) {
        if (len < 3) { *err = UTF8_ERR_TRUNCATED; return 0; }
        uint8_t b1 = buf[1];
        uint8_t b2 = buf[2];
        if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80) { *err = UTF8_ERR_INVALID_BYTE; return 0; }

        uint32_t cp = ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F);
        if (cp < 0x0800) { *err = UTF8_ERR_OVERLONG; return 0; }
        if (cp >= 0xD800 && cp <= 0xDFFF) { *err = UTF8_ERR_SURROGATE; return 0; }

        *out_cp = cp;
        *err = UTF8_OK;
        return 3;
    }

    if ((b0 & 0xF8) == 0xF0) {
        if (len < 4) { *err = UTF8_ERR_TRUNCATED; return 0; }
        uint8_t b1 = buf[1];
        uint8_t b2 = buf[2];
        uint8_t b3 = buf[3];
        if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80 || (b3 & 0xC0) != 0x80) {
            *err = UTF8_ERR_INVALID_BYTE;
            return 0;
        }

        uint32_t cp = ((b0 & 0x07) << 18) | ((b1 & 0x3F) << 12) | ((b2 & 0x3F) << 6) | (b3 & 0x3F);
        if (cp < 0x10000) { *err = UTF8_ERR_OVERLONG; return 0; }
        if (cp > 0x10FFFF) { *err = UTF8_ERR_OUT_OF_RANGE; return 0; }

        *out_cp = cp;
        *err = UTF8_OK;
        return 4;
    }

    *err = UTF8_ERR_INVALID_BYTE;
    return 0;
}

/* Нормалізує кінці рядків та відкидає BOM */
void process_stream(FILE *in, FILE *out) {
    uint8_t in_buf[4096];
    size_t in_len = fread(in_buf, 1, sizeof(in_buf), in);
    size_t pos = 0;

    /* Перевірка та пропуск UTF-8 BOM (0xEF 0xBB 0xBF) на початку */
    if (in_len >= 3 && in_buf[0] == 0xEF && in_buf[1] == 0xBB && in_buf[2] == 0xBF) {
        pos = 3;
    }

    bool prev_cr = false;
    while (pos < in_len) {
        uint32_t cp = 0;
        utf8_error_t err = UTF8_OK;
        size_t consumed = utf8_decode_codepoint(in_buf + pos, in_len - pos, &cp, &err);

        if (consumed == 0) {
            fprintf(stderr, "Помилка UTF-8 на зміщенні %zu (код %d)\n", pos, err);
            break;
        }

        if (cp == '\r') {
            fputc('\n', out);
            prev_cr = true;
        } else if (cp == '\n') {
            if (!prev_cr) {
                fputc('\n', out);
            }
            prev_cr = false;
        } else {
            prev_cr = false;
            fwrite(in_buf + pos, 1, consumed, out);
        }
        pos += consumed;
    }
}

int main(void) {
    process_stream(stdin, stdout);
    return 0;
}
