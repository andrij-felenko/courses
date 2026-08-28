#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(_WIN32)
  #include <winsock2.h>
#else
  #include <arpa/inet.h>
#endif

/* Двійкова структура розібраного PSSH-боксу */
typedef struct {
    uint8_t  version;
    uint8_t  system_id[16];
    uint32_t kid_count;
    uint8_t (*kids)[16];       /* динамічний масив 16-байтових KID */
    uint32_t data_size;
    uint8_t *data;             /* непрозоре навантаження DRM */
} pssh_box_t;

/* Читання 32-бітного uint у форматі big-endian */
static inline uint32_t read_be32(const uint8_t *buf) {
    return ((uint32_t)buf[0] << 24) |
           ((uint32_t)buf[1] << 16) |
           ((uint32_t)buf[2] <<  8) |
           ((uint32_t)buf[3]);
}

/**
 * Парсер боксу pssh відповідно до стандарту ISO/IEC 23001-7.
 * Повертає true у разі успішного розбору, false при пошкодженні даних.
 */
bool parse_pssh_box(const uint8_t *raw_buf, size_t buf_len, pssh_box_t *out_box) {
    if (!raw_buf || !out_box || buf_len < 32) {
        return false;
    }

    memset(out_box, 0, sizeof(*out_box));

    size_t offset = 0;
    uint32_t box_size = read_be32(raw_buf + offset);
    offset += 4;

    if (box_size > buf_len || box_size < 32) {
        return false;
    }

    /* Перевірка FourCC типу боксу: 'pssh' == 0x70737368 */
    if (memcmp(raw_buf + offset, "pssh", 4) != 0) {
        return false;
    }
    offset += 4;

    out_box->version = raw_buf[offset];
    offset += 1;

    /* 3 байти flags (пропускаємо) */
    offset += 3;

    /* 16 байтів SystemID */
    memcpy(out_box->system_id, raw_buf + offset, 16);
    offset += 16;

    if (out_box->version == 1) {
        if (offset + 4 > box_size) return false;
        out_box->kid_count = read_be32(raw_buf + offset);
        offset += 4;

        if (offset + (out_box->kid_count * 16) > box_size) {
            return false;
        }

        if (out_box->kid_count > 0) {
            out_box->kids = (uint8_t(*)[16])malloc(out_box->kid_count * 16);
            if (!out_box->kids) return false;
            memcpy(out_box->kids, raw_buf + offset, out_box->kid_count * 16);
            offset += out_box->kid_count * 16;
        }
    } else {
        out_box->kid_count = 0;
        out_box->kids = NULL;
    }

    if (offset + 4 > box_size) {
        free(out_box->kids);
        return false;
    }

    out_box->data_size = read_be32(raw_buf + offset);
    offset += 4;

    if (offset + out_box->data_size > box_size) {
        free(out_box->kids);
        return false;
    }

    if (out_box->data_size > 0) {
        out_box->data = (uint8_t *)malloc(out_box->data_size);
        if (!out_box->data) {
            free(out_box->kids);
            return false;
        }
        memcpy(out_box->data, raw_buf + offset, out_box->data_size);
    }

    return true;
}

void free_pssh_box(pssh_box_t *box) {
    if (box) {
        free(box->kids);
        free(box->data);
        memset(box, 0, sizeof(*box));
    }
}
