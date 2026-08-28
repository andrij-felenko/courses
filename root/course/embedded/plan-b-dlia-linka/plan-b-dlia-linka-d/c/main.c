#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BEARER_COUNT 2
#define DWELL_TIME_MS 4000
#define FAILOVER_PER 25
#define RECOVERY_PER 5

typedef enum {
    LINK_PRIO_CMD = 0,
    LINK_PRIO_TELEM,
    LINK_PRIO_BULK
} link_prio_t;

typedef struct {
    int16_t  rssi_dbm;
    uint32_t last_rx_ms;
    uint32_t rx_mask;
    uint8_t  per;
    bool     alive;
} channel_state_t;

typedef struct {
    uint8_t         active_idx;
    uint8_t         state;
    uint32_t        eval_start_ms;
    channel_state_t ch[BEARER_COUNT];
} arbiter_ctx_t;

void arbiter_rx_update(arbiter_ctx_t *ctx, uint8_t ch_idx, int16_t rssi, uint32_t now) {
    channel_state_t *c = &ctx->ch[ch_idx];
    c->last_rx_ms = now;
    c->rssi_dbm = (int16_t)((c->rssi_dbm * 3 + rssi) >> 2);
    c->rx_mask = (c->rx_mask << 1) | 1U;
    
    uint8_t rec = 0;
    uint32_t m = c->rx_mask;
    for (int i = 0; i < 32; i++) {
        if (m & 1U) rec++;
        m >>= 1;
    }
    c->per = (uint8_t)(((32 - rec) * 100) / 32);
}

void arbiter_poll(arbiter_ctx_t *ctx, uint32_t now) {
    channel_state_t *prim = &ctx->ch[0];
    channel_state_t *fall = &ctx->ch[1];
    
    bool prim_bad = (now - prim->last_rx_ms > 1200) || (prim->per >= FAILOVER_PER);
    
    if (ctx->active_idx == 0 && prim_bad) {
        ctx->active_idx = 1; /* Перемикання на Sub-GHz */
        ctx->eval_start_ms = 0;
    } else if (ctx->active_idx == 1 && !prim_bad && prim->per <= RECOVERY_PER) {
        if (ctx->eval_start_ms == 0) {
            ctx->eval_start_ms = now; /* Старт таймера гістерезису */
        } else if (now - ctx->eval_start_ms >= DWELL_TIME_MS) {
            ctx->active_idx = 0; /* Повернення на Primary */
            ctx->eval_start_ms = 0;
        }
    } else {
        ctx->eval_start_ms = 0;
    }
}

int arbiter_dispatch(arbiter_ctx_t *ctx, link_prio_t prio, const uint8_t *data, uint16_t len) {
    if (prio == LINK_PRIO_BULK && ctx->active_idx == 1) {
        return 0; /* Скидання відеопотоку на резервному каналі */
    }
    /* Передача кадру у вихідний драйвер активного каналу */
    return len;
}
