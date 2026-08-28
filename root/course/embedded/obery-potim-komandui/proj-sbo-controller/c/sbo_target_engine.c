/* sbo_target_engine.h / sbo_target_engine.c — Чистий C для вбудованих систем */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define SBO_MAGIC_BYTE          0x5B
#define SBO_BROADCAST_ID        0xFF
#define SBO_DEFAULT_TIMEOUT_MS  5000
#define SBO_MAX_PAYLOAD_LEN     64

typedef enum {
    SBO_STATE_IDLE = 0,
    SBO_STATE_ARMED,
    SBO_STATE_EXECUTING
} sbo_fsm_state_t;

typedef enum {
    SBO_MSG_SELECT_REQ  = 0x10,
    SBO_MSG_SELECT_ACK  = 0x11,
    SBO_MSG_SELECT_NACK = 0x12,
    SBO_MSG_OPERATE_REQ = 0x20,
    SBO_MSG_OPERATE_ACK = 0x21,
    SBO_MSG_OPERATE_NACK= 0x22,
    SBO_MSG_CANCEL_REQ  = 0x30,
    SBO_MSG_CANCEL_ACK  = 0x31
} sbo_msg_type_t;

typedef enum {
    SBO_ERR_NONE = 0,
    SBO_ERR_BUSY,
    SBO_ERR_INVALID_TOKEN,
    SBO_ERR_TIMEOUT_EXPIRED,
    SBO_ERR_NOT_ARMED,
    SBO_ERR_CMD_MISMATCH,
    SBO_ERR_BROADCAST_FORBIDDEN,
    SBO_ERR_INTERNAL_FAULT
} sbo_error_t;

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;
    uint8_t  payload_len;
    uint8_t  seq;
    uint8_t  msg_type;
    uint8_t  source_id;
    uint8_t  target_id;
    uint8_t  target_comp;
    uint8_t  sbo_state;
    uint32_t sbo_token;
    uint16_t cmd_code;
    uint16_t timeout_ms;
    uint8_t  payload[SBO_MAX_PAYLOAD_LEN];
    uint16_t crc16;
} sbo_packet_t;
#pragma pack(pop)

typedef struct {
    uint8_t         my_system_id;
    sbo_fsm_state_t state;
    uint8_t         locked_source_id;
    uint16_t        locked_cmd_code;
    uint32_t        active_token;
    uint32_t        arm_expiry_timestamp_ms;
    uint32_t        prng_seed;
} sbo_target_context_t;

/* Простий генератор ентропійних токенів */
static uint32_t sbo_generate_token(sbo_target_context_t *ctx, uint32_t current_time_ms) {
    ctx->prng_seed = ctx->prng_seed * 1664525u + 1013904223u + current_time_ms;
    uint32_t token = ctx->prng_seed;
    if (token == 0) token = 0xA5A55A5A; /* Запобігання нульовому токену */
    return token;
}

void sbo_target_init(sbo_target_context_t *ctx, uint8_t system_id, uint32_t initial_seed) {
    memset(ctx, 0, sizeof(sbo_target_context_t));
    ctx->my_system_id = system_id;
    ctx->state = SBO_STATE_IDLE;
    ctx->prng_seed = initial_seed ^ 0xDEADBEEF;
}

/* Періодичне оновлення таймера (виклик кожні 10..50 мс) */
void sbo_target_tick(sbo_target_context_t *ctx, uint32_t current_time_ms) {
    if (ctx->state == SBO_STATE_ARMED) {
        if (current_time_ms >= ctx->arm_expiry_timestamp_ms) {
            /* Спливання вікна дії: автоматичне знешкодження */
            ctx->state = SBO_STATE_IDLE;
            ctx->active_token = 0;
            ctx->locked_cmd_code = 0;
            ctx->locked_source_id = 0;
        }
    }
}

/* Обробка вхідного пакету транзакції */
sbo_error_t sbo_target_process_packet(sbo_target_context_t *ctx,
                                      const sbo_packet_t *rx_pkt,
                                      sbo_packet_t *tx_response,
                                      uint32_t current_time_ms) {
    /* 1. Фільтрація широкомовних пакетів для критичних операцій */
    if (rx_pkt->target_id == SBO_BROADCAST_ID) {
        return SBO_ERR_BROADCAST_FORBIDDEN;
    }

    /* 2. Перевірка приналежності пакету цьому вузлу */
    if (rx_pkt->target_id != ctx->my_system_id) {
        return SBO_ERR_NONE; /* Пакет адресовано іншому вузлу, ігноруємо */
    }

    /* Оновлення статусу тайм-ауту */
    sbo_target_tick(ctx, current_time_ms);

    memset(tx_response, 0, sizeof(sbo_packet_t));
    tx_response->magic = SBO_MAGIC_BYTE;
    tx_response->seq = rx_pkt->seq;
    tx_response->source_id = ctx->my_system_id;
    tx_response->target_id = rx_pkt->source_id;
    tx_response->cmd_code = rx_pkt->cmd_code;

    switch (rx_pkt->msg_type) {
        case SBO_MSG_SELECT_REQ: {
            if (ctx->state == SBO_STATE_ARMED && ctx->locked_source_id != rx_pkt->source_id) {
                tx_response->msg_type = SBO_MSG_SELECT_NACK;
                tx_response->sbo_state = ctx->state;
                tx_response->payload[0] = (uint8_t)SBO_ERR_BUSY;
                tx_response->payload_len = 1;
                return SBO_ERR_BUSY;
            }

            /* Переведення у стан ARMED */
            ctx->state = SBO_STATE_ARMED;
            ctx->locked_source_id = rx_pkt->source_id;
            ctx->locked_cmd_code = rx_pkt->cmd_code;
            ctx->active_token = sbo_generate_token(ctx, current_time_ms);
            
            uint16_t window = (rx_pkt->timeout_ms > 0) ? rx_pkt->timeout_ms : SBO_DEFAULT_TIMEOUT_MS;
            ctx->arm_expiry_timestamp_ms = current_time_ms + window;

            tx_response->msg_type = SBO_MSG_SELECT_ACK;
            tx_response->sbo_state = SBO_STATE_ARMED;
            tx_response->sbo_token = ctx->active_token;
            tx_response->timeout_ms = window;
            return SBO_ERR_NONE;
        }

        case SBO_MSG_OPERATE_REQ: {
            if (ctx->state != SBO_STATE_ARMED) {
                tx_response->msg_type = SBO_MSG_OPERATE_NACK;
                tx_response->sbo_state = ctx->state;
                tx_response->payload[0] = (uint8_t)SBO_ERR_NOT_ARMED;
                tx_response->payload_len = 1;
                return SBO_ERR_NOT_ARMED;
            }

            if (rx_pkt->sbo_token != ctx->active_token) {
                /* Спроба використати недійсний токен: негайне знешкодження */
                ctx->state = SBO_STATE_IDLE;
                ctx->active_token = 0;
                tx_response->msg_type = SBO_MSG_OPERATE_NACK;
                tx_response->sbo_state = SBO_STATE_IDLE;
                tx_response->payload[0] = (uint8_t)SBO_ERR_INVALID_TOKEN;
                tx_response->payload_len = 1;
                return SBO_ERR_INVALID_TOKEN;
            }

            if (rx_pkt->cmd_code != ctx->locked_cmd_code) {
                ctx->state = SBO_STATE_IDLE;
                ctx->active_token = 0;
                tx_response->msg_type = SBO_MSG_OPERATE_NACK;
                tx_response->sbo_state = SBO_STATE_IDLE;
                tx_response->payload[0] = (uint8_t)SBO_ERR_CMD_MISMATCH;
                tx_response->payload_len = 1;
                return SBO_ERR_CMD_MISMATCH;
            }

            /* Успішна валідація: дія дозволена до виконання */
            ctx->state = SBO_STATE_IDLE; /* Одноразовий селектор */
            ctx->active_token = 0;

            tx_response->msg_type = SBO_MSG_OPERATE_ACK;
            tx_response->sbo_state = SBO_STATE_IDLE;
            return SBO_ERR_NONE;
        }

        case SBO_MSG_CANCEL_REQ: {
            ctx->state = SBO_STATE_IDLE;
            ctx->active_token = 0;
            tx_response->msg_type = SBO_MSG_CANCEL_ACK;
            tx_response->sbo_state = SBO_STATE_IDLE;
            return SBO_ERR_NONE;
        }

        default:
            return SBO_ERR_INTERNAL_FAULT;
    }
}
