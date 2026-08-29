/* arq_tx.c — скінченний автомат передавача Stop-and-Wait.
 *
 * IDLE ──send──▶ WAIT_ACK ──ACK──▶ IDLE
 *                    │  ▲
 *          RTO/NACK  │  │ повтор
 *                    ▼  │
 *              (retries < MAX) ──ні──▶ FAILED → доповідь додатку → IDLE
 */
#include "arq.h"

#include <string.h>

static void tx_emit(arq_tx *tx, uint32_t now_ms)
{
    tx->sent_at_ms = now_ms;
    tx->write(tx->write_ctx, tx->wire, tx->wire_len);
}

void arq_tx_init(arq_tx *tx, arq_write_fn write, void *write_ctx,
                 arq_result_fn on_result, void *result_ctx)
{
    memset(tx, 0, sizeof(*tx));
    tx->state      = ARQ_TX_IDLE;
    tx->write      = write;
    tx->write_ctx  = write_ctx;
    tx->on_result  = on_result;
    tx->result_ctx = result_ctx;
    arq_rto_init(&tx->rto);
}

bool arq_tx_send(arq_tx *tx, const uint8_t *data, uint8_t len, uint32_t now_ms)
{
    if (tx->state != ARQ_TX_IDLE) {
        return false; /* Stop-and-Wait: у польоті рівно один кадр */
    }
    if (len > ARQ_MAX_PAYLOAD) {
        return false;
    }

    arq_frame frame;
    frame.type = ARQ_DATA;
    frame.seq  = tx->seq;
    frame.len  = len;
    if (len > 0) {
        memcpy(frame.payload, data, len);
    }

    /* Пакуємо один раз: повтор шле байт-у-байт ту саму копію. */
    tx->wire_len = arq_encode(&frame, tx->wire, sizeof tx->wire);
    if (tx->wire_len == 0) {
        return false;
    }

    tx->retries       = 0;
    tx->retransmitted = false;
    tx->state         = ARQ_TX_WAIT_ACK;
    tx->stats.sent++;
    tx_emit(tx, now_ms);
    return true;
}

/* Повтор кадру. backoff=true — реакція на таймаут (правило Карна №2). */
static void tx_retry(arq_tx *tx, uint32_t now_ms, bool backoff)
{
    if (tx->retries >= ARQ_MAX_RETRIES) {
        tx->state = ARQ_TX_FAILED;
        tx->stats.failed++;
        if (tx->on_result != NULL) {
            tx->on_result(tx->result_ctx, false, tx->seq);
        }
        /* Номер НЕ чергуємо: якщо приймач насправді отримав дані, а до нас
           не дійшла жодна квитанція, зміна номера змусила б його прийняти
           наступний кадр за дублікат. Перевстановити сесію — справа
           прикладного рівня, протокол лише чесно доповів про відмову. */
        tx->state = ARQ_TX_IDLE;
        return;
    }

    tx->retries++;
    tx->retransmitted = true; /* правило Карна №1: вимір RTT уже негодящий */
    tx->stats.retransmitted++;
    if (backoff) {
        arq_rto_backoff(&tx->rto);
    }
    tx_emit(tx, now_ms);
}

void arq_tx_poll(arq_tx *tx, uint32_t now_ms)
{
    if (tx->state != ARQ_TX_WAIT_ACK) {
        return;
    }
    /* Різниця беззнакова — переповнення лічильника мілісекунд не ламає порівняння. */
    if ((uint32_t)(now_ms - tx->sent_at_ms) < arq_rto_get(&tx->rto)) {
        return;
    }
    tx_retry(tx, now_ms, true);
}

void arq_tx_on_wire(arq_tx *tx, const uint8_t *wire, size_t len, uint32_t now_ms)
{
    arq_frame frame;
    if (arq_decode(wire, len, &frame) != ARQ_DEC_OK) {
        tx->stats.stray++; /* биту квитанцію лікує таймаут, ніякої особливої логіки */
        return;
    }
    if (tx->state != ARQ_TX_WAIT_ACK || frame.seq != tx->seq) {
        tx->stats.stray++; /* квитанція з попереднього кола або взагалі не на часі */
        return;
    }

    if (frame.type == ARQ_ACK) {
        if (!tx->retransmitted) {
            /* Карн №1: міряємо тільки кадри, доставлені з першої спроби. */
            arq_rto_update(&tx->rto, (uint32_t)(now_ms - tx->sent_at_ms));
        }
        tx->seq ^= 1u; /* чергування біта: 0,1,0,1,… */
        tx->state = ARQ_TX_IDLE;
        tx->stats.acked++;
        if (tx->on_result != NULL) {
            tx->on_result(tx->result_ctx, true, frame.seq);
        }
    } else if (frame.type == ARQ_NACK) {
        /* Приймач явно сказав «кадр побитий» — повторюємо негайно, не чекаючи RTO.
           Таймаут при цьому НЕ подвоюємо: канал живий, це завада, а не перевантаження. */
        tx_retry(tx, now_ms, false);
    } else {
        tx->stats.stray++;
    }
}
