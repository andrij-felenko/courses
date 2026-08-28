#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    MP_STATE_START,
    MP_STATE_START_BOUNDARY,
    MP_STATE_HEADER_FIELD,
    MP_STATE_HEADER_VALUE,
    MP_STATE_HEADERS_ALMOST_DONE,
    MP_STATE_PART_DATA,
    MP_STATE_BOUNDARY_MATCH,
    MP_STATE_END
} mp_state_t;

typedef struct {
    void (*on_part_begin)(void *user_data);
    void (*on_header)(const char *name, size_t nlen, const char *val, size_t vlen, void *user_data);
    void (*on_part_data)(const unsigned char *data, size_t len, void *user_data);
    void (*on_part_end)(void *user_data);
} mp_callbacks_t;

typedef struct {
    mp_state_t state;
    char boundary[128];
    size_t boundary_len;
    size_t match_idx;
    char header_name[256];
    size_t header_name_len;
    char header_val[1024];
    size_t header_val_len;
    mp_callbacks_t cb;
    void *user_data;
} mp_parser_t;

void mp_parser_init(mp_parser_t *p, const char *boundary, mp_callbacks_t cb, void *user_data) {
    memset(p, 0, sizeof(*p));
    p->state = MP_STATE_START;
    p->boundary[0] = '-';
    p->boundary[1] = '-';
    strncpy(p->boundary + 2, boundary, sizeof(p->boundary) - 3);
    p->boundary_len = strlen(p->boundary);
    p->cb = cb;
    p->user_data = user_data;
}

size_t mp_parser_execute(mp_parser_t *p, const unsigned char *buf, size_t len) {
    size_t i = 0;
    size_t mark = 0;

    for (i = 0; i < len; ++i) {
        unsigned char c = buf[i];

        switch (p->state) {
        case MP_STATE_START:
        case MP_STATE_START_BOUNDARY:
            if (c == (unsigned char)p->boundary[p->match_idx]) {
                p->match_idx++;
                if (p->match_idx == p->boundary_len) {
                    p->match_idx = 0;
                    p->state = MP_STATE_HEADERS_ALMOST_DONE;
                    if (p->cb.on_part_begin) p->cb.on_part_begin(p->user_data);
                }
            } else {
                p->match_idx = 0;
            }
            break;

        case MP_STATE_HEADERS_ALMOST_DONE:
            if (c == '\n') {
                p->state = MP_STATE_HEADER_FIELD;
                p->header_name_len = 0;
                p->header_val_len = 0;
            }
            break;

        case MP_STATE_HEADER_FIELD:
            if (c == '\r') {
                /* Порожній рядок перед тілом даних */
            } else if (c == '\n') {
                p->state = MP_STATE_PART_DATA;
                mark = i + 1;
            } else if (c == ':') {
                p->state = MP_STATE_HEADER_VALUE;
            } else if (p->header_name_len + 1 < sizeof(p->header_name)) {
                p->header_name[p->header_name_len++] = (char)c;
            }
            break;

        case MP_STATE_HEADER_VALUE:
            if (c == '\r') {
                /* Очікування LF */
            } else if (c == '\n') {
                if (p->cb.on_header) {
                    p->cb.on_header(p->header_name, p->header_name_len,
                                    p->header_val, p->header_val_len, p->user_data);
                }
                p->header_name_len = 0;
                p->header_val_len = 0;
                p->state = MP_STATE_HEADER_FIELD;
            } else if (c != ' ' || p->header_val_len > 0) {
                if (p->header_val_len + 1 < sizeof(p->header_val)) {
                    p->header_val[p->header_val_len++] = (char)c;
                }
            }
            break;

        case MP_STATE_PART_DATA:
            if (c == '\r') {
                if (i > mark && p->cb.on_part_data) {
                    p->cb.on_part_data(buf + mark, i - mark, p->user_data);
                }
                p->state = MP_STATE_BOUNDARY_MATCH;
                p->match_idx = 0;
            }
            break;

        case MP_STATE_BOUNDARY_MATCH:
            if (p->match_idx == 0 && c == '\n') {
                p->match_idx = 1;
            } else if (p->match_idx >= 1 && (p->match_idx - 1) < p->boundary_len &&
                       c == (unsigned char)p->boundary[p->match_idx - 1]) {
                p->match_idx++;
                if ((p->match_idx - 1) == p->boundary_len) {
                    if (p->cb.on_part_end) p->cb.on_part_end(p->user_data);
                    p->state = MP_STATE_HEADERS_ALMOST_DONE;
                    p->match_idx = 0;
                }
            } else {
                /* Несправжня межа: скидаємо накопичені байти назад у тіло частини */
                if (p->cb.on_part_data) {
                    p->cb.on_part_data((const unsigned char *)"\r", 1, p->user_data);
                    if (p->match_idx > 1) {
                        p->cb.on_part_data((const unsigned char *)"\n", 1, p->user_data);
                        p->cb.on_part_data((const unsigned char *)p->boundary, p->match_idx - 2, p->user_data);
                    }
                }
                p->state = MP_STATE_PART_DATA;
                mark = i;
                i--; /* повторна обробка поточного байта */
            }
            break;

        case MP_STATE_END:
            return i;
        }
    }

    if (p->state == MP_STATE_PART_DATA && i > mark) {
        if (p->cb.on_part_data) {
            p->cb.on_part_data(buf + mark, i - mark, p->user_data);
        }
    }

    return len;
}
