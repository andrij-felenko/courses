/* sbo_target_engine.c — автомат Select-Before-Operate на борту. */
#include "sbo_target_engine.h"

#include <string.h>

#define SBO_DIAG_EXEC_PULSE_US 10u
#define SBO_DIAG_DROP_PULSE_US 50u

/* Лінійний конгруентний генератор: без купи й без залежності від libc.
 * Час підмішуємо, щоб після перезапуску серія токенів не повторилася. */
static uint32_t sbo_next_token(sbo_target_context_t *ctx, uint32_t now_ms) {
    ctx->prng_seed = ctx->prng_seed * 1664525u + 1013904223u + (now_ms << 3);
    uint32_t token = ctx->prng_seed >> 1;   /* молодші біти LCG надто регулярні */
    if (token == 0u) {
        token = 0xA5A55A5Au;                /* нуль зарезервовано під «токена немає» */
    }
    return token;
}

static void sbo_disarm(sbo_target_context_t *ctx) {
    if (ctx->state == SBO_STATE_ARMED) {
        sbo_diag_set(SBO_DIAG_ARMED, false);
    }
    ctx->state = SBO_STATE_IDLE;
    ctx->active_token = 0u;
    ctx->locked_cmd_code = 0u;
    ctx->locked_source_id = 0u;
    ctx->arm_expiry_timestamp_ms = 0u;
}

static void sbo_fill_response(const sbo_target_context_t *ctx, const sbo_packet_t *rx,
                              sbo_packet_t *tx, uint8_t msg_type) {
    memset(tx, 0, sizeof(*tx));
    tx->magic       = SBO_MAGIC_BYTE;
    tx->seq         = rx->seq;
    tx->msg_type    = msg_type;
    tx->source_id   = ctx->my_system_id;
    tx->target_id   = rx->source_id;
    tx->target_comp = rx->target_comp;
    tx->cmd_code    = rx->cmd_code;
    tx->sbo_state   = ctx->state;
}

static sbo_error_t sbo_nack(sbo_target_context_t *ctx, const sbo_packet_t *rx,
                            sbo_packet_t *tx, uint8_t msg_type, sbo_error_t err) {
    sbo_fill_response(ctx, rx, tx, msg_type);
    tx->payload[0]  = (uint8_t)err;   /* причину відмови оператор бачить у пульті */
    tx->payload_len = 1u;
    ctx->reject_count++;
    return err;
}

void sbo_target_init(sbo_target_context_t *ctx, uint8_t system_id, uint32_t initial_seed) {
    if (ctx == NULL) {
        return;
    }
    memset(ctx, 0, sizeof(*ctx));
    ctx->my_system_id = system_id;
    ctx->state = SBO_STATE_IDLE;
    ctx->prng_seed = initial_seed ^ 0xDEADBEEFu;
    sbo_diag_set(SBO_DIAG_ARMED, false);
}

bool sbo_target_tick(sbo_target_context_t *ctx, uint32_t now_ms) {
    if (ctx == NULL || ctx->state != SBO_STATE_ARMED) {
        return false;
    }
    /* Порівнюємо РІЗНИЦЮ зі знаком: лічильник мілісекунд обертається кожні ~49 діб,
     * пряме now >= expiry зняло б замок на самому переповненні. */
    if ((int32_t)(now_ms - ctx->arm_expiry_timestamp_ms) >= 0) {
        sbo_disarm(ctx);
        ctx->timeout_count++;
        return true;
    }
    return false;
}

sbo_error_t sbo_target_process_packet(sbo_target_context_t *ctx,
                                      const sbo_packet_t *rx,
                                      sbo_packet_t *tx,
                                      bool *has_response,
                                      uint32_t now_ms) {
    if (ctx == NULL || rx == NULL || tx == NULL || has_response == NULL) {
        return SBO_ERR_INTERNAL_FAULT;
    }
    *has_response = false;

    /* Строгий unicast: критична дія широкомовним кадром не проходить ніколи. */
    if (rx->target_id == SBO_BROADCAST_ID) {
        sbo_diag_pulse(SBO_DIAG_SECURITY_DROP, SBO_DIAG_DROP_PULSE_US);
        ctx->reject_count++;
        return SBO_ERR_BROADCAST_FORBIDDEN;
    }
    if (rx->target_id != ctx->my_system_id) {
        return SBO_ERR_FOREIGN_TARGET;   /* сусідній апарат — мовчимо, ефір не засмічуємо */
    }

    const bool expired = sbo_target_tick(ctx, now_ms);
    *has_response = true;

    switch (rx->msg_type) {
    case SBO_MSG_SELECT_REQ: {
        /* Поки триває дія або поки замок тримає інший пульт — тільки відмова. */
        if (ctx->state == SBO_STATE_EXECUTING ||
            (ctx->state == SBO_STATE_ARMED && ctx->locked_source_id != rx->source_id)) {
            return sbo_nack(ctx, rx, tx, SBO_MSG_SELECT_NACK, SBO_ERR_BUSY);
        }

        uint16_t window = (rx->timeout_ms > 0u) ? rx->timeout_ms : (uint16_t)SBO_DEFAULT_TIMEOUT_MS;
        if (window > SBO_MAX_TIMEOUT_MS) {
            window = (uint16_t)SBO_MAX_TIMEOUT_MS;
        }

        ctx->state = SBO_STATE_ARMED;
        ctx->locked_source_id = rx->source_id;
        ctx->locked_cmd_code = rx->cmd_code;
        ctx->active_token = sbo_next_token(ctx, now_ms);
        ctx->arm_expiry_timestamp_ms = now_ms + window;
        ctx->select_count++;
        sbo_diag_set(SBO_DIAG_ARMED, true);

        sbo_fill_response(ctx, rx, tx, SBO_MSG_SELECT_ACK);
        tx->sbo_token  = ctx->active_token;
        tx->timeout_ms = window;
        return SBO_ERR_NONE;
    }

    case SBO_MSG_OPERATE_REQ: {
        if (ctx->state != SBO_STATE_ARMED) {
            sbo_error_t why = SBO_ERR_NOT_ARMED;
            if (expired) {
                why = SBO_ERR_TIMEOUT_EXPIRED;      /* замок зняв саме таймер, і це видно оператору */
            } else if (ctx->state == SBO_STATE_EXECUTING) {
                why = SBO_ERR_BUSY;
            }
            return sbo_nack(ctx, rx, tx, SBO_MSG_OPERATE_NACK, why);
        }
        if (rx->source_id != ctx->locked_source_id) {
            sbo_diag_pulse(SBO_DIAG_SECURITY_DROP, SBO_DIAG_DROP_PULSE_US);
            sbo_disarm(ctx);
            return sbo_nack(ctx, rx, tx, SBO_MSG_OPERATE_NACK, SBO_ERR_SOURCE_MISMATCH);
        }
        if (rx->sbo_token != ctx->active_token) {
            /* Підставлений або запізнілий токен: знешкоджуємо негайно, нової селекції
             * доведеться просити заново. */
            sbo_diag_pulse(SBO_DIAG_SECURITY_DROP, SBO_DIAG_DROP_PULSE_US);
            sbo_disarm(ctx);
            return sbo_nack(ctx, rx, tx, SBO_MSG_OPERATE_NACK, SBO_ERR_INVALID_TOKEN);
        }
        if (rx->cmd_code != ctx->locked_cmd_code) {
            sbo_diag_pulse(SBO_DIAG_SECURITY_DROP, SBO_DIAG_DROP_PULSE_US);
            sbo_disarm(ctx);
            return sbo_nack(ctx, rx, tx, SBO_MSG_OPERATE_NACK, SBO_ERR_CMD_MISMATCH);
        }

        /* Токен анулюємо ДО звертання до приводу: повтор кадру не пройде навіть тоді,
         * коли привід відпрацьовує довго, а радіо встигло принести дубль. */
        const uint16_t cmd = ctx->locked_cmd_code;
        ctx->active_token = 0u;
        ctx->state = SBO_STATE_EXECUTING;
        sbo_diag_set(SBO_DIAG_ARMED, false);

        const bool ok = sbo_actuator_execute(cmd, rx->payload, rx->payload_len);

        ctx->state = SBO_STATE_IDLE;
        ctx->locked_cmd_code = 0u;
        ctx->locked_source_id = 0u;
        ctx->arm_expiry_timestamp_ms = 0u;

        if (!ok) {
            return sbo_nack(ctx, rx, tx, SBO_MSG_OPERATE_NACK, SBO_ERR_INTERNAL_FAULT);
        }
        sbo_diag_pulse(SBO_DIAG_OP_EXEC, SBO_DIAG_EXEC_PULSE_US);
        ctx->exec_count++;
        sbo_fill_response(ctx, rx, tx, SBO_MSG_OPERATE_ACK);
        return SBO_ERR_NONE;
    }

    case SBO_MSG_CANCEL_REQ: {
        if (ctx->state == SBO_STATE_EXECUTING) {
            return sbo_nack(ctx, rx, tx, SBO_MSG_CANCEL_NACK, SBO_ERR_BUSY);
        }
        if (ctx->state == SBO_STATE_ARMED && ctx->locked_source_id != rx->source_id) {
            return sbo_nack(ctx, rx, tx, SBO_MSG_CANCEL_NACK, SBO_ERR_BUSY);
        }
        sbo_disarm(ctx);
        sbo_fill_response(ctx, rx, tx, SBO_MSG_CANCEL_ACK);
        return SBO_ERR_NONE;
    }

    default:
        /* Квитанції (ACK/NACK) на борту не мають сенсу: приймає їх пульт. */
        *has_response = false;
        return SBO_ERR_UNKNOWN_TYPE;
    }
}

sbo_error_t sbo_target_handle_frame(sbo_target_context_t *ctx,
                                    const uint8_t *in, size_t in_len,
                                    uint8_t *out, size_t out_cap, size_t *out_len,
                                    uint32_t now_ms) {
    if (out_len == NULL) {
        return SBO_ERR_INTERNAL_FAULT;
    }
    *out_len = 0u;

    sbo_packet_t rx;
    sbo_error_t err = sbo_frame_decode(in, in_len, &rx);
    if (err != SBO_ERR_NONE) {
        return err;                       /* побитий ефіром кадр далі валідатора не йде */
    }

    sbo_packet_t tx;
    bool has_response = false;
    err = sbo_target_process_packet(ctx, &rx, &tx, &has_response, now_ms);
    if (!has_response) {
        return err;
    }

    const sbo_error_t enc = sbo_frame_encode(&tx, out, out_cap, out_len);
    return (enc != SBO_ERR_NONE) ? enc : err;
}
