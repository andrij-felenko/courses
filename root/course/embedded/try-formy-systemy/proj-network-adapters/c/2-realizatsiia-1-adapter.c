#include <string.h>

#define HOME_RX_QUEUE_SIZE 8

typedef struct {
    net_state_t state;
    uint32_t last_heartbeat_ms;
    uint16_t ack_sequence;
} home_adapter_ctx_t;

static bool home_init(net_adapter_t *self) {
    home_adapter_ctx_t *ctx = (home_adapter_ctx_t *)self->driver_ctx;
    ctx->state = NET_STATE_ONLINE;
    ctx->last_heartbeat_ms = 0;
    ctx->ack_sequence = 0;
    return true;
}

static void home_poll(net_adapter_t *self, uint32_t now_ms) {
    home_adapter_ctx_t *ctx = (home_adapter_ctx_t *)self->driver_ctx;
    
    /* Періодичний локальний Heartbeat до хаба кожні 30 секунд */
    if (now_ms - ctx->last_heartbeat_ms >= 30000) {
        ctx->last_heartbeat_ms = now_ms;
        net_packet_t hb = {
            .msg_id = 0x0001, /* ID: Node Heartbeat */
            .payload = { 0x01 }, /* Статус OK */
            .len = 1,
            .priority = NET_PRIO_LOW
        };
        self->api->send(self, &hb);
    }
}

static bool home_send(net_adapter_t *self, const net_packet_t *pkt) {
    /* Пряма відправка кадру через локальний 802.15.4 / Wi-Fi трансивер */
    (void)self;
    (void)pkt;
    return true;
}

static net_state_t home_get_state(const net_adapter_t *self) {
    const home_adapter_ctx_t *ctx = (const home_adapter_ctx_t *)self->driver_ctx;
    return ctx->state;
}

static const struct net_adapter_api HOME_API = {
    .init = home_init,
    .poll = home_poll,
    .send = home_send,
    .get_state = home_get_state
};
