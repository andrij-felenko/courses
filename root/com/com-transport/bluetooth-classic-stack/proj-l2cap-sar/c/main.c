#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define L2CAP_MAX_MTU           1024
#define L2CAP_MAX_CONNECTIONS   4

#define L2CAP_CID_SDP           0x0001
#define L2CAP_CID_SIGNALING     0x0002
#define L2CAP_CID_DYNAMIC_START 0x0040

typedef enum {
    L2CAP_SAR_IDLE,
    L2CAP_SAR_ACCUMULATING,
    L2CAP_SAR_COMPLETE,
    L2CAP_SAR_ERROR_OVERFLOW,
    L2CAP_SAR_ERROR_CORRUPT
} l2cap_sar_state_t;

typedef struct {
    uint16_t length;
    uint16_t cid;
} __attribute__((packed)) l2cap_hdr_t;

typedef struct {
    uint16_t handle;
    l2cap_sar_state_t state;
    uint16_t expected_len;
    uint16_t received_len;
    uint16_t cid;
    uint8_t buffer[L2CAP_MAX_MTU];
} l2cap_channel_ctx_t;

typedef struct {
    l2cap_channel_ctx_t channels[L2CAP_MAX_CONNECTIONS];
} l2cap_engine_t;

void l2cap_engine_init(l2cap_engine_t *engine) {
    memset(engine, 0, sizeof(l2cap_engine_t));
}

static l2cap_channel_ctx_t* l2cap_find_or_alloc_channel(l2cap_engine_t *engine, uint16_t handle) {
    for (int i = 0; i < L2CAP_MAX_CONNECTIONS; i++) {
        if (engine->channels[i].handle == handle && engine->channels[i].state != L2CAP_SAR_IDLE) {
            return &engine->channels[i];
        }
    }
    for (int i = 0; i < L2CAP_MAX_CONNECTIONS; i++) {
        if (engine->channels[i].state == L2CAP_SAR_IDLE) {
            engine->channels[i].handle = handle;
            return &engine->channels[i];
        }
    }
    return NULL;
}

static void l2cap_dispatch_packet(uint16_t handle, uint16_t cid, const uint8_t *payload, uint16_t len) {
    if (cid == L2CAP_CID_SDP) {
        /* Передача у підсистему Service Discovery Protocol */
    } else if (cid == L2CAP_CID_SIGNALING) {
        /* Передача у внутрішній диспетчер команд L2CAP Signaling */
    } else if (cid >= L2CAP_CID_DYNAMIC_START) {
        /* Передача у підсистему емуляції послідовного порту RFCOMM */
    }
}

bool l2cap_process_acl_fragment(l2cap_engine_t *engine,
                                uint16_t handle,
                                uint8_t pb_flag,
                                const uint8_t *data,
                                uint16_t data_len) {
    if (!engine || !data || data_len == 0) {
        return false;
    }

    l2cap_channel_ctx_t *ctx = l2cap_find_or_alloc_channel(engine, handle);
    if (!ctx) {
        return false;
    }

    if (pb_flag == 0x02 || pb_flag == 0x00) {
        /* Перший фрагмент L2CAP кадру (Start Fragment) */
        if (data_len < sizeof(l2cap_hdr_t)) {
            ctx->state = L2CAP_SAR_ERROR_CORRUPT;
            return false;
        }

        const l2cap_hdr_t *hdr = (const l2cap_hdr_t*)data;
        ctx->expected_len = hdr->length;
        ctx->cid = hdr->cid;
        ctx->received_len = 0;

        if (ctx->expected_len > L2CAP_MAX_MTU) {
            ctx->state = L2CAP_SAR_ERROR_OVERFLOW;
            return false;
        }

        uint16_t payload_len = data_len - sizeof(l2cap_hdr_t);
        if (payload_len > ctx->expected_len) {
            ctx->state = L2CAP_SAR_ERROR_CORRUPT;
            return false;
        }

        if (payload_len > 0) {
            memcpy(ctx->buffer, data + sizeof(l2cap_hdr_t), payload_len);
            ctx->received_len = payload_len;
        }

        if (ctx->received_len == ctx->expected_len) {
            ctx->state = L2CAP_SAR_COMPLETE;
            l2cap_dispatch_packet(handle, ctx->cid, ctx->buffer, ctx->received_len);
            ctx->state = L2CAP_SAR_IDLE;
            return true;
        }

        ctx->state = L2CAP_SAR_ACCUMULATING;
        return true;

    } else if (pb_flag == 0x01) {
        /* Продовження кадру L2CAP (Continuation Fragment) */
        if (ctx->state != L2CAP_SAR_ACCUMULATING) {
            ctx->state = L2CAP_SAR_ERROR_CORRUPT;
            return false;
        }

        if (ctx->received_len + data_len > ctx->expected_len) {
            ctx->state = L2CAP_SAR_ERROR_OVERFLOW;
            return false;
        }

        memcpy(ctx->buffer + ctx->received_len, data, data_len);
        ctx->received_len += data_len;

        if (ctx->received_len == ctx->expected_len) {
            ctx->state = L2CAP_SAR_COMPLETE;
            l2cap_dispatch_packet(handle, ctx->cid, ctx->buffer, ctx->received_len);
            ctx->state = L2CAP_SAR_IDLE;
            return true;
        }

        return true;
    }

    return false;
}
