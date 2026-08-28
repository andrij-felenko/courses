#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SLIP_END     0xC0
#define SLIP_ESC     0xDB
#define SLIP_ESC_END 0xDC
#define SLIP_ESC_ESC 0xDD

typedef enum {
    SLIP_ST_NORMAL = 0,
    SLIP_ST_ESCAPED
} slip_fsm_state_t;

typedef struct {
    uint8_t         *rx_buf;
    size_t           max_len;
    size_t           rx_len;
    slip_fsm_state_t state;
    bool             overflow;
    void           (*packet_cb)(const uint8_t *pkt, size_t len, void *ctx);
    void            *user_ctx;
} slip_fsm_t;

void slip_fsm_init(slip_fsm_t *fsm, uint8_t *buf, size_t max_len,
                   void (*cb)(const uint8_t *, size_t, void *), void *ctx) {
    fsm->rx_buf = buf;
    fsm->max_len = max_len;
    fsm->rx_len = 0;
    fsm->state = SLIP_ST_NORMAL;
    fsm->overflow = false;
    fsm->packet_cb = cb;
    fsm->user_ctx = ctx;
}

void slip_fsm_parse_byte(slip_fsm_t *fsm, uint8_t byte) {
    if (fsm->state == SLIP_ST_NORMAL) {
        if (byte == SLIP_END) {
            if (fsm->rx_len > 0) {
                if (!fsm->overflow && fsm->packet_cb) {
                    fsm->packet_cb(fsm->rx_buf, fsm->rx_len, fsm->user_ctx);
                }
                fsm->rx_len = 0;
                fsm->overflow = false;
            }
        } else if (byte == SLIP_ESC) {
            fsm->state = SLIP_ST_ESCAPED;
        } else {
            if (fsm->rx_len < fsm->max_len) {
                fsm->rx_buf[fsm->rx_len++] = byte;
            } else {
                fsm->overflow = true;
            }
        }
    } else { /* SLIP_ST_ESCAPED */
        if (byte == SLIP_ESC_END) {
            if (fsm->rx_len < fsm->max_len) fsm->rx_buf[fsm->rx_len++] = SLIP_END;
            else fsm->overflow = true;
        } else if (byte == SLIP_ESC_ESC) {
            if (fsm->rx_len < fsm->max_len) fsm->rx_buf[fsm->rx_len++] = SLIP_ESC;
            else fsm->overflow = true;
        } else {
            /* Порушення стандарту завадою: записуємо байт як є */
            if (fsm->rx_len < fsm->max_len) fsm->rx_buf[fsm->rx_len++] = byte;
            else fsm->overflow = true;
        }
        fsm->state = SLIP_ST_NORMAL;
    }
}

size_t slip_encode(const uint8_t *src, size_t src_len, uint8_t *dst, size_t dst_max) {
    size_t pos = 0;
    if (pos >= dst_max) return 0;
    dst[pos++] = SLIP_END;

    for (size_t i = 0; i < src_len; ++i) {
        uint8_t b = src[i];
        if (b == SLIP_END) {
            if (pos + 2 > dst_max) return 0;
            dst[pos++] = SLIP_ESC;
            dst[pos++] = SLIP_ESC_END;
        } else if (b == SLIP_ESC) {
            if (pos + 2 > dst_max) return 0;
            dst[pos++] = SLIP_ESC;
            dst[pos++] = SLIP_ESC_ESC;
        } else {
            if (pos + 1 > dst_max) return 0;
            dst[pos++] = b;
        }
    }

    if (pos >= dst_max) return 0;
    dst[pos++] = SLIP_END;
    return pos;
}
