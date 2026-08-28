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

/* Допоміжні функції читання big-endian цілих чисел */
static inline uint32_t read_u32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8)  | ((uint32_t)p[3]);
}

static inline uint64_t read_u64(const uint8_t *p) {
    return ((uint64_t)read_u32(p) << 32) | (uint64_t)read_u32(p + 4);
}

static inline int32_t read_i32(const uint8_t *p) {
    return (int32_t)read_u32(p);
}

/* Структура стандартного заголовка бокса */
typedef struct {
    uint32_t type;         /* 4-байтовий FourCC (наприклад 'moof') */
    uint64_t total_size;   /* Загальний розмір бокса в байтах */
    uint32_t header_size;  /* Розмір заголовка (8 або 16 байтів) */
} BoxHeader;

/* Структура метаданих вилученого чанка CMAF */
typedef struct {
    uint32_t seq_num;
    uint32_t track_id;
    uint64_t base_decode_time;
    uint32_t sample_count;
    uint64_t total_duration;
    bool has_sync_frame;
    bool default_base_is_moof;
} CmafChunkMetadata;

/* Розбір базового заголовка бокса */
bool parse_box_header(const uint8_t *buf, size_t len, BoxHeader *out) {
    if (len < 8) return false;

    uint32_t size32 = read_u32(buf);
    out->type = read_u32(buf + 4);
    out->header_size = 8;

    if (size32 == 1) {
        /* 64-бітний розширений розмір largesize */
        if (len < 16) return false;
        out->total_size = read_u64(buf + 8);
        out->header_size = 16;
    } else if (size32 == 0) {
        /* Бокс до кінця потоку */
        out->total_size = len;
    } else {
        out->total_size = size32;
    }

    return (out->total_size >= out->header_size && out->total_size <= len);
}

/* Розбір бокса tfdt: витягування базового часу декодування */
bool parse_tfdt(const uint8_t *payload, size_t len, uint64_t *dts_out) {
    if (len < 4) return false;
    uint8_t version = payload[0];

    if (version == 1) {
        if (len < 12) return false;
        *dts_out = read_u64(payload + 4);
        return true;
    } else if (version == 0) {
        if (len < 8) return false;
        *dts_out = (uint64_t)read_u32(payload + 4);
        return true;
    }
    return false;
}

/* Розбір бокса tfhd: перевірка налаштувань треку та прапорців */
bool parse_tfhd(const uint8_t *payload, size_t len, uint32_t *track_id, bool *base_is_moof) {
    if (len < 8) return false;
    uint32_t flags = read_u32(payload) & 0x00FFFFFF;
    *track_id = read_u32(payload + 4);
    *base_is_moof = (flags & 0x020000) != 0;
    return true;
}

/* Розбір бокса trun: обчислення тривалості та перевірка ключового кадру */
bool parse_trun(const uint8_t *payload, size_t len, uint32_t *sample_count,
                uint64_t *total_duration, bool *has_sync) {
    if (len < 8) return false;

    uint8_t version = payload[0];
    uint32_t flags = read_u32(payload) & 0x00FFFFFF;
    uint32_t count = read_u32(payload + 4);
    *sample_count = count;
    *total_duration = 0;
    *has_sync = false;

    const uint8_t *p = payload + 8;
    const uint8_t *end = payload + len;

    if (flags & 0x000001) p += 4; /* data_offset */
    uint32_t first_flags = 0;
    if (flags & 0x000004) {       /* first_sample_flags */
        if (p + 4 > end) return false;
        first_flags = read_u32(p);
        p += 4;
        /* Перевірка: чи перший семпл є синхронним (ключовим) */
        if ((first_flags & 0x00010000) == 0) {
            *has_sync = true;
        }
    }

    bool has_dur = (flags & 0x000100) != 0;
    bool has_size = (flags & 0x000200) != 0;
    bool has_flags = (flags & 0x000400) != 0;
    bool has_cto = (flags & 0x000800) != 0;

    for (uint32_t i = 0; i < count; i++) {
        uint32_t dur = 1;
        if (has_dur) {
            if (p + 4 > end) return false;
            dur = read_u32(p);
            p += 4;
        }
        *total_duration += dur;

        if (has_size) {
            if (p + 4 > end) return false;
            p += 4;
        }
        if (has_flags) {
            if (p + 4 > end) return false;
            uint32_t sflags = read_u32(p);
            p += 4;
            /* Біт 16 (0x00010000): sample_is_non_sync_sample == 0 -> SAP/Sync */
            if ((sflags & 0x00010000) == 0) {
                *has_sync = true;
            }
        }
        if (has_cto) {
            if (p + 4 > end) return false;
            p += 4;
        }
    }

    return true;
}

/* Розбір контейнера traf */
bool parse_traf(const uint8_t *traf_data, size_t traf_len, CmafChunkMetadata *meta) {
    size_t offset = 0;
    while (offset + 8 <= traf_len) {
        BoxHeader h;
        if (!parse_box_header(traf_data + offset, traf_len - offset, &h)) break;

        const uint8_t *body = traf_data + offset + h.header_size;
        size_t body_len = h.total_size - h.header_size;

        if (h.type == 0x74666474) { /* 'tfdt' */
            parse_tfdt(body, body_len, &meta->base_decode_time);
        } else if (h.type == 0x74666864) { /* 'tfhd' */
            parse_tfhd(body, body_len, &meta->track_id, &meta->default_base_is_moof);
        } else if (h.type == 0x7472756E) { /* 'trun' */
            parse_trun(body, body_len, &meta->sample_count, &meta->total_duration, &meta->has_sync_frame);
        }

        offset += h.total_size;
    }
    return true;
}

/* Головна функція інспекції CMAF-сегмента/чанка */
bool inspect_cmaf_chunk(const uint8_t *data, size_t len, CmafChunkMetadata *meta) {
    memset(meta, 0, sizeof(*meta));
    size_t offset = 0;

    while (offset + 8 <= len) {
        BoxHeader h;
        if (!parse_box_header(data + offset, len - offset, &h)) return false;

        const uint8_t *body = data + offset + h.header_size;
        size_t body_len = h.total_size - h.header_size;

        if (h.type == 0x6D6F6F66) { /* 'moof' */
            size_t inner_off = 0;
            while (inner_off + 8 <= body_len) {
                BoxHeader inh;
                if (!parse_box_header(body + inner_off, body_len - inner_off, &inh)) break;
                const uint8_t *in_body = body + inner_off + inh.header_size;
                size_t in_body_len = inh.total_size - inh.header_size;

                if (inh.type == 0x6D666864 && in_body_len >= 8) { /* 'mfhd' */
                    meta->seq_num = read_u32(in_body + 4);
                } else if (inh.type == 0x74726166) { /* 'traf' */
                    parse_traf(in_body, in_body_len, meta);
                }
                inner_off += inh.total_size;
            }
        }

        offset += h.total_size;
    }
    return true;
}
