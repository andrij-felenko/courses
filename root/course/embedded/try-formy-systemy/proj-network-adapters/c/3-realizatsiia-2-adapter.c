#define TRACKER_FLASH_BUFFER_SIZE 32

typedef struct {
    uint32_t timestamp;
    int32_t  lat_e7;
    int32_t  lon_e7;
    uint8_t  battery_pct;
} tracker_record_t;

typedef enum {
    TRACKER_ST_SLEEPING,
    TRACKER_ST_MODEM_POWERUP,
    TRACKER_ST_REGISTERING,
    TRACKER_ST_TRANSMITTING_BATCH,
    TRACKER_ST_MODEM_SHUTDOWN
} tracker_fsm_state_t;

typedef struct {
    net_state_t state;
    tracker_fsm_state_t fsm;
    tracker_record_t flash_ring[TRACKER_FLASH_BUFFER_SIZE];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
    uint32_t session_timer_ms;
} tracker_adapter_ctx_t;

static bool tracker_init(net_adapter_t *self) {
    tracker_adapter_ctx_t *ctx = (tracker_adapter_ctx_t *)self->driver_ctx;
    ctx->state = NET_STATE_SLEEPING;
    ctx->fsm = TRACKER_ST_SLEEPING;
    ctx->head = 0;
    ctx->tail = 0;
    ctx->count = 0;
    ctx->session_timer_ms = 0;
    return true;
}

static bool tracker_buffer_point(tracker_adapter_ctx_t *ctx, const tracker_record_t *rec) {
    if (ctx->count >= TRACKER_FLASH_BUFFER_SIZE) {
        /* Перезапис найстарішої точки, якщо буфер переповнений */
        ctx->tail = (ctx->tail + 1) % TRACKER_FLASH_BUFFER_SIZE;
        ctx->count--;
    }
    ctx->flash_ring[ctx->head] = *rec;
    ctx->head = (ctx->head + 1) % TRACKER_FLASH_BUFFER_SIZE;
    ctx->count++;
    return true;
}

static void tracker_poll(net_adapter_t *self, uint32_t now_ms) {
    tracker_adapter_ctx_t *ctx = (tracker_adapter_ctx_t *)self->driver_ctx;

    switch (ctx->fsm) {
    case TRACKER_ST_SLEEPING:
        /* Прокидаємося, якщо накопичилося >5 точок або минула година */
        if (ctx->count >= 5 || (now_ms - ctx->session_timer_ms >= 3600000 && ctx->count > 0)) {
            ctx->fsm = TRACKER_ST_MODEM_POWERUP;
            ctx->session_timer_ms = now_ms;
            ctx->state = NET_STATE_CONNECTING;
        }
        break;

    case TRACKER_ST_MODEM_POWERUP:
        /* Симуляція подачі живлення на модем (PWRKEY затримка 500 мс) */
        if (now_ms - ctx->session_timer_ms >= 500) {
            ctx->fsm = TRACKER_ST_REGISTERING;
            ctx->session_timer_ms = now_ms;
        }
        break;

    case TRACKER_ST_REGISTERING:
        /* Симуляція реєстрації в мережі NB-IoT (до 4 секунд) */
        if (now_ms - ctx->session_timer_ms >= 4000) {
            ctx->fsm = TRACKER_ST_TRANSMITTING_BATCH;
            ctx->state = NET_STATE_ONLINE;
        }
        break;

    case TRACKER_ST_TRANSMITTING_BATCH:
        /* Вивантажуємо всі накопичені пакети одним з'єднанням */
        while (ctx->count > 0) {
            /* Передача точки ctx->flash_ring[ctx->tail] */
            ctx->tail = (ctx->tail + 1) % TRACKER_FLASH_BUFFER_SIZE;
            ctx->count--;
        }
        ctx->fsm = TRACKER_ST_MODEM_SHUTDOWN;
        ctx->session_timer_ms = now_ms;
        break;

    case TRACKER_ST_MODEM_SHUTDOWN:
        /* Вимикаємо живлення модема для нульового витоку струму */
        ctx->state = NET_STATE_SLEEPING;
        ctx->fsm = TRACKER_ST_SLEEPING;
        break;
    }
}

static bool tracker_send(net_adapter_t *self, const net_packet_t *pkt) {
    tracker_adapter_ctx_t *ctx = (tracker_adapter_ctx_t *)self->driver_ctx;
    if (pkt->len >= sizeof(tracker_record_t)) {
        tracker_record_t rec;
        memcpy(&rec, pkt->payload, sizeof(tracker_record_t));
        return tracker_buffer_point(ctx, &rec);
    }
    return false;
}

static net_state_t tracker_get_state(const net_adapter_t *self) {
    const tracker_adapter_ctx_t *ctx = (const tracker_adapter_ctx_t *)self->driver_ctx;
    return ctx->state;
}
