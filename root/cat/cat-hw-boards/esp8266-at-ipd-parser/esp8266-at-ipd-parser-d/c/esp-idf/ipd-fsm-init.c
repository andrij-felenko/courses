#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define IPD_MAX_PAYLOAD_SIZE 2048

typedef enum {
    IPD_STATE_IDLE,
    IPD_STATE_PREFIX,
    IPD_STATE_LINK_ID,
    IPD_STATE_LEN,
    IPD_STATE_PAYLOAD,
    IPD_STATE_DONE
} ipd_fsm_state_t;

typedef void (*ipd_payload_callback_t)(uint8_t link_id, const uint8_t *buffer, uint16_t len);

typedef struct {
    ipd_fsm_state_t state;
    uint8_t prefix_idx;
    uint8_t link_id;
    uint16_t payload_len;
    uint16_t bytes_read;
    bool is_multilink;
    uint8_t payload_buffer[IPD_MAX_PAYLOAD_SIZE];
    ipd_payload_callback_t callback;
} ipd_fsm_t;

static const char IPD_PREFIX[] = "IPD,";

void ipd_fsm_init(ipd_fsm_t *fsm, bool multilink, ipd_payload_callback_t cb) {
    fsm->state = IPD_STATE_IDLE;
    fsm->prefix_idx = 0;
    fsm->link_id = 0;
    fsm->payload_len = 0;
    fsm->bytes_read = 0;
    fsm->is_multilink = multilink;
    fsm->callback = cb;
}

void ipd_fsm_reset(ipd_fsm_t *fsm) {
    fsm->state = IPD_STATE_IDLE;
    fsm->prefix_idx = 0;
    fsm->link_id = 0;
    fsm->payload_len = 0;
    fsm->bytes_read = 0;
}

void ipd_fsm_feed_byte(ipd_fsm_t *fsm, uint8_t byte) {
    char c = (char)byte;

    switch (fsm->state) {
        case IPD_STATE_IDLE:
            if (c == '+') {
                fsm->state = IPD_STATE_PREFIX;
                fsm->prefix_idx = 0;
            }
            break;

        case IPD_STATE_PREFIX:
            if (c == IPD_PREFIX[fsm->prefix_idx]) {
                fsm->prefix_idx++;
                if (IPD_PREFIX[fsm->prefix_idx] == '\0') {
                    fsm->payload_len = 0;
                    fsm->link_id = 0;
                    fsm->state = fsm->is_multilink ? IPD_STATE_LINK_ID : IPD_STATE_LEN;
                }
            } else {
                ipd_fsm_reset(fsm);
            }
            break;

        case IPD_STATE_LINK_ID:
            if (c >= '0' && c <= '9') {
                fsm->link_id = (uint8_t)(c - '0');
            } else if (c == ',') {
                fsm->state = IPD_STATE_LEN;
                fsm->payload_len = 0;
            } else {
                ipd_fsm_reset(fsm);
            }
            break;

        case IPD_STATE_LEN:
            if (c >= '0' && c <= '9') {
                fsm->payload_len = (uint16_t)(fsm->payload_len * 10 + (c - '0'));
                if (fsm->payload_len > IPD_MAX_PAYLOAD_SIZE) {
                    ipd_fsm_reset(fsm);
                }
            } else if (c == ':') {
                if (fsm->payload_len > 0) {
                    fsm->state = IPD_STATE_PAYLOAD;
                    fsm->bytes_read = 0;
                } else {
                    if (fsm->callback) {
                        fsm->callback(fsm->link_id, fsm->payload_buffer, 0);
                    }
                    ipd_fsm_reset(fsm);
                }
            } else {
                ipd_fsm_reset(fsm);
            }
            break;

        case IPD_STATE_PAYLOAD:
            fsm->payload_buffer[fsm->bytes_read++] = byte;
            if (fsm->bytes_read >= fsm->payload_len) {
                fsm->state = IPD_STATE_DONE;
                if (fsm->callback) {
                    fsm->callback(fsm->link_id, fsm->payload_buffer, fsm->payload_len);
                }
                ipd_fsm_reset(fsm);
            }
            break;

        case IPD_STATE_DONE:
            ipd_fsm_reset(fsm);
            break;
    }
}
