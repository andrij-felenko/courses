#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

static inline bool is_unreserved(unsigned char c) {
    return (c >= 'A' && c <= 'Z') ||
           (c >= 'a' && c <= 'z') ||
           (c >= '0' && c <= '9') ||
           c == '-' || c == '.' || c == '_' || c == '~';
}

/* Відсоткове кодування рядка за RFC 3986 у вихідний буфер */
size_t url_encode(const char *src, size_t src_len, char *dst, size_t dst_len) {
    static const char hex[] = "0123456789ABCDEF";
    size_t written = 0;

    for (size_t i = 0; i < src_len; i++) {
        unsigned char c = (unsigned char)src[i];
        if (is_unreserved(c)) {
            if (written + 1 >= dst_len) return 0;
            dst[written++] = c;
        } else {
            if (written + 3 >= dst_len) return 0;
            dst[written++] = '%';
            dst[written++] = hex[c >> 4];
            dst[written++] = hex[c & 0x0F];
        }
    }
    if (written < dst_len) dst[written] = '\0';
    return written;
}

static inline int hex_val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

/* Розкодування відсоткових послідовностей %HH */
size_t url_decode(const char *src, size_t src_len, char *dst, size_t dst_len) {
    size_t written = 0;
    for (size_t i = 0; i < src_len; i++) {
        if (src[i] == '%' && i + 2 < src_len) {
            int h1 = hex_val(src[i + 1]);
            int h2 = hex_val(src[i + 2]);
            if (h1 != -1 && h2 != -1) {
                if (written + 1 >= dst_len) return 0;
                dst[written++] = (char)((h1 << 4) | h2);
                i += 2;
                continue;
            }
        }
        if (written + 1 >= dst_len) return 0;
        dst[written++] = src[i];
    }
    if (written < dst_len) dst[written] = '\0';
    return written;
}
