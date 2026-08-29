/* arq_rx.c — скінченний автомат приймача Stop-and-Wait.
 *
 * Уся пам'ять приймача — один байт `expected_seq`. Черг, буферів
 * переупорядкування й динамічної алокації тут немає й бути не може.
 */
#include "arq.h"

#include <string.h>

static void rx_control(arq_rx *rx, uint8_t type, uint8_t seq)
{
    arq_frame ctrl;
    ctrl.type = type;
    ctrl.seq  = seq;
    ctrl.len  = 0;

    uint8_t wire[ARQ_HDR_LEN + ARQ_CRC_LEN];
    const size_t n = arq_encode(&ctrl, wire, sizeof wire);
    if (n > 0 && rx->write != NULL) {
        rx->write(rx->write_ctx, wire, n);
    }
}

void arq_rx_init(arq_rx *rx, arq_write_fn write, void *write_ctx,
                 arq_deliver_fn deliver, void *deliver_ctx)
{
    memset(rx, 0, sizeof(*rx));
    rx->expected_seq = 0;
    rx->last_error   = ARQ_DEC_OK;
    rx->write        = write;
    rx->write_ctx    = write_ctx;
    rx->deliver      = deliver;
    rx->deliver_ctx  = deliver_ctx;
}

void arq_rx_on_wire(arq_rx *rx, const uint8_t *wire, size_t len)
{
    arq_frame frame;
    const arq_decode_res res = arq_decode(wire, len, &frame);

    if (res != ARQ_DEC_OK) {
        rx->stats.corrupted++;
        rx->last_error = res;
        /* Номер побитого кадру невідомий (він і сам міг бути спотворений),
           тому просимо повторити той кадр, якого чекаємо. */
        rx_control(rx, ARQ_NACK, rx->expected_seq);
        return;
    }

    if (frame.type != ARQ_DATA) {
        rx->stats.ignored++; /* приймач сам квитанцій не чекає */
        return;
    }

    if (frame.seq == rx->expected_seq) {
        rx->stats.delivered++;
        if (rx->deliver != NULL) {
            rx->deliver(rx->deliver_ctx, frame.payload, frame.len);
        }
        rx->expected_seq ^= 1u;
    } else {
        /* Дублікат: наш ACK загубився на зворотному шляху. Додатку дані
           вдруге НЕ віддаємо — інакше «зупинити привід» виконається двічі. */
        rx->stats.duplicates++;
    }

    /* Квитуємо в обох випадках: і свіжий кадр, і повтор. Мовчання на дублікат
       залишило б передавача заблокованим до вичерпання спроб. */
    rx_control(rx, ARQ_ACK, frame.seq);
}
