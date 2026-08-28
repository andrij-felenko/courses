#define P2P_FAILSAFE_TIMEOUT_MS 1500

typedef struct {
    net_state_t state;
    uint32_t last_rx_timestamp_ms;
    uint16_t tx_sequence;
    uint16_t rx_sequence;
    uint32_t packets_lost;
    bool failsafe_triggered;
} p2p_adapter_ctx_t;

static bool p2p_init(net_adapter_t *self) {
    p2p_adapter_ctx_t *ctx = (p2p_adapter_ctx_t *)self->driver_ctx;
    ctx->state = NET_STATE_CONNECTING;
    ctx->last_rx_timestamp_ms = 0;
    ctx->tx_sequence = 0;
    ctx->rx_sequence = 0;
    ctx->packets_lost = 0;
    ctx->failsafe_triggered = false;
    return true;
}

static void p2p_poll(net_adapter_t *self, uint32_t now_ms) {
    p2p_adapter_ctx_t *ctx = (p2p_adapter_ctx_t *)self->driver_ctx;

    /* Контроль тайм-ауту зв'язку */
    if (ctx->state == NET_STATE_ONLINE) {
        if (now_ms - ctx->last_rx_timestamp_ms >= P2P_FAILSAFE_TIMEOUT_MS) {
            ctx->state = NET_STATE_ERROR;
            ctx->failsafe_triggered = true;
            /* Повідомлення автопілоту: перехід у режим аварійного повернення */
        }
    }
}

static bool p2p_send(net_adapter_t *self, const net_packet_t *pkt) {
    p2p_adapter_ctx_t *ctx = (p2p_adapter_ctx_t *)self->driver_ctx;
    ctx->tx_sequence++;

    /* У P2P критичні пакети (керування) витісняють чергу телеметрії */
    if (pkt->priority == NET_PRIO_CRITICAL) {
        /* Негайна передача в RF-трансивер через SPI/UART без буферизації */
        return true;
    }
    
    /* Звичайна телеметрія відправляється, якщо радіоканал не зайнятий */
    return true;
}

static void p2p_on_frame_rx(net_adapter_t *self, const uint8_t *data, uint8_t len, uint16_t seq, uint32_t now_ms) {
    p2p_adapter_ctx_t *ctx = (p2p_adapter_ctx_t *)self->driver_ctx;
    
    /* Скидання таймера Fail-Safe */
    ctx->last_rx_timestamp_ms = now_ms;
    ctx->state = NET_STATE_ONLINE;
    ctx->failsafe_triggered = false;

    /* Підрахунок втрачених кадрів за послідовністю sequence number */
    if (seq > ctx->rx_sequence + 1) {
        ctx->packets_lost += (seq - ctx->rx_sequence - 1);
    }
    ctx->rx_sequence = seq;

    if (self->rx_cb) {
        net_packet_t pkt;
        pkt.msg_id = (data[0] << 8) | data[1];
        pkt.len = len > 64 ? 64 : len;
        memcpy(pkt.payload, data, pkt.len);
        pkt.priority = NET_PRIO_CRITICAL;
        self->rx_cb(&pkt, self->user_data);
    }
}
