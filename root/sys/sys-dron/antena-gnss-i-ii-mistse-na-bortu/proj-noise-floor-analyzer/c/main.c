#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define UBX_SYNC1 0xB5
#define UBX_SYNC2 0x62
#define UBX_CLASS_MON 0x0A
#define UBX_ID_MON_RF 0x38
#define UBX_MAX_PAYLOAD 256

typedef enum {
    UBX_STATE_SYNC1 = 0,
    UBX_STATE_SYNC2,
    UBX_STATE_CLASS,
    UBX_STATE_ID,
    UBX_STATE_LEN_LSB,
    UBX_STATE_LEN_MSB,
    UBX_STATE_PAYLOAD,
    UBX_STATE_CKA,
    UBX_STATE_CKB
} ubx_state_t;

typedef struct {
    uint8_t block_id;
    uint8_t ant_status;
    uint8_t ant_power;
    uint16_t noise_per_ms;
    uint16_t agc_cnt;
    uint8_t jam_ind;
    uint8_t jamming_state;
} gnss_rf_block_metrics_t;

typedef struct {
    uint8_t version;
    uint8_t num_blocks;
    gnss_rf_block_metrics_t blocks[4];
    bool valid;
} gnss_rf_report_t;

typedef enum {
    RF_STATUS_OK = 0,
    RF_STATUS_WARNING_NOISE,
    RF_STATUS_CRITICAL_JAMMING,
    RF_STATUS_AGC_SATURATED
} rf_health_status_t;

typedef struct {
    ubx_state_t state;
    uint8_t msg_class;
    uint8_t msg_id;
    uint16_t payload_len;
    uint16_t payload_idx;
    uint8_t payload[UBX_MAX_PAYLOAD];
    uint8_t ck_a;
    uint8_t ck_b;
    uint8_t calc_ck_a;
    uint8_t calc_ck_b;
} ubx_parser_ctx_t;

static void ubx_update_checksum(uint8_t byte, uint8_t *ck_a, uint8_t *ck_b) {
    *ck_a = (uint8_t)(*ck_a + byte);
    *ck_b = (uint8_t)(*ck_b + *ck_a);
}

void ubx_parser_init(ubx_parser_ctx_t *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(ubx_parser_ctx_t));
    ctx->state = UBX_STATE_SYNC1;
}

bool ubx_parser_feed_byte(ubx_parser_ctx_t *ctx, uint8_t b, gnss_rf_report_t *report) {
    if (!ctx || !report) return false;

    switch (ctx->state) {
        case UBX_STATE_SYNC1:
            if (b == UBX_SYNC1) {
                ctx->state = UBX_STATE_SYNC2;
            }
            break;

        case UBX_STATE_SYNC2:
            if (b == UBX_SYNC2) {
                ctx->state = UBX_STATE_CLASS;
                ctx->calc_ck_a = 0;
                ctx->calc_ck_b = 0;
            } else {
                ctx->state = UBX_STATE_SYNC1;
            }
            break;

        case UBX_STATE_CLASS:
            ctx->msg_class = b;
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            ctx->state = UBX_STATE_ID;
            break;

        case UBX_STATE_ID:
            ctx->msg_id = b;
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            ctx->state = UBX_STATE_LEN_LSB;
            break;

        case UBX_STATE_LEN_LSB:
            ctx->payload_len = b;
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            ctx->state = UBX_STATE_LEN_MSB;
            break;

        case UBX_STATE_LEN_MSB:
            ctx->payload_len |= (uint16_t)(b << 8);
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            ctx->payload_idx = 0;
            if (ctx->payload_len > UBX_MAX_PAYLOAD) {
                ctx->state = UBX_STATE_SYNC1;
            } else if (ctx->payload_len == 0) {
                ctx->state = UBX_STATE_CKA;
            } else {
                ctx->state = UBX_STATE_PAYLOAD;
            }
            break;

        case UBX_STATE_PAYLOAD:
            ctx->payload[ctx->payload_idx++] = b;
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            if (ctx->payload_idx >= ctx->payload_len) {
                ctx->state = UBX_STATE_CKA;
            }
            break;

        case UBX_STATE_CKA:
            ctx->ck_a = b;
            ctx->state = UBX_STATE_CKB;
            break;

        case UBX_STATE_CKB:
            ctx->ck_b = b;
            ctx->state = UBX_STATE_SYNC1;
            if (ctx->ck_a == ctx->calc_ck_a && ctx->ck_b == ctx->calc_ck_b) {
                if (ctx->msg_class == UBX_CLASS_MON && ctx->msg_id == UBX_ID_MON_RF) {
                    if (ctx->payload_len >= 4) {
                        report->version = ctx->payload[0];
                        report->num_blocks = ctx->payload[1];
                        if (report->num_blocks > 4) report->num_blocks = 4;

                        for (uint8_t i = 0; i < report->num_blocks; ++i) {
                            size_t offset = 4 + (size_t)i * 24;
                            if (offset + 24 <= ctx->payload_len) {
                                gnss_rf_block_metrics_t *blk = &report->blocks[i];
                                blk->block_id = ctx->payload[offset + 0];
                                blk->ant_status = ctx->payload[offset + 2];
                                blk->ant_power = ctx->payload[offset + 3];
                                blk->noise_per_ms = (uint16_t)(ctx->payload[offset + 8] | (ctx->payload[offset + 9] << 8));
                                blk->agc_cnt = (uint16_t)(ctx->payload[offset + 10] | (ctx->payload[offset + 11] << 8));
                                blk->jam_ind = ctx->payload[offset + 12];
                                blk->jamming_state = ctx->payload[offset + 14];
                            }
                        }
                        report->valid = true;
                        return true;
                    }
                }
            }
            break;
    }
    return false;
}

rf_health_status_t gnss_evaluate_rf_health(const gnss_rf_block_metrics_t *metrics, uint16_t baseline_noise) {
    if (!metrics) return RF_STATUS_OK;

    if (metrics->jam_ind > 100 || metrics->jamming_state == 3) {
        return RF_STATUS_CRITICAL_JAMMING;
    }
    if (metrics->agc_cnt < 4000) {
        return RF_STATUS_AGC_SATURATED;
    }
    if (baseline_noise > 0 && metrics->noise_per_ms > (uint16_t)(baseline_noise * 1.3f)) {
        return RF_STATUS_WARNING_NOISE;
    }
    return RF_STATUS_OK;
}
