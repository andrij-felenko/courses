#include "link_tx.h"

#include <string.h>

static void tx_on_ack_frame(uint8_t seq, const uint8_t *payload, size_t len, void *ctx) {
    (void)payload;
    link_tx_t *tx = (link_tx_t *)ctx;

    if (len != 0U) {
        return;   // у зворотному напрямку ходять лише порожні кадри-квитанції
    }

    for (size_t i = 0; i < LINK_WINDOW; ++i) {
        link_tx_slot_t *slot = &tx->slots[i];
        if (slot->used && slot->seq == seq) {
            slot->used = false;
            tx->in_flight--;
            tx->stats.acked++;
            return;
        }
    }

    // Квитанція на кадр, який ми вже зняли з обліку: приймач відповів на дублікат.
    tx->stats.stray_ack++;
}

void link_tx_init(link_tx_t *tx, link_write_fn write, void *write_ctx) {
    memset(tx, 0, sizeof(*tx));
    tx->write = write;
    tx->write_ctx = write_ctx;
    framing_reader_init(&tx->ack_reader, tx_on_ack_frame, tx);
}

link_status_t link_tx_submit(link_tx_t *tx, const uint8_t *payload, size_t len, uint32_t now_ms) {
    if (len > LINK_MAX_PAYLOAD) {
        return LINK_ERR_TOO_LONG;
    }
    if (tx->in_flight >= LINK_WINDOW) {
        return LINK_ERR_WINDOW_FULL;
    }

    link_tx_slot_t *slot = NULL;
    for (size_t i = 0; i < LINK_WINDOW; ++i) {
        if (!tx->slots[i].used) {
            slot = &tx->slots[i];
            break;
        }
    }
    if (slot == NULL) {
        return LINK_ERR_WINDOW_FULL;
    }

    size_t wire_len = 0U;
    const link_status_t st = framing_build(tx->next_seq, payload, len,
                                           slot->wire, sizeof(slot->wire), &wire_len);
    if (st != LINK_OK) {
        return st;
    }

    slot->used = true;
    slot->seq = tx->next_seq;
    slot->len = wire_len;
    slot->tries = 1U;
    slot->deadline_ms = now_ms + LINK_TX_TIMEOUT_MS;

    tx->next_seq = (uint8_t)(tx->next_seq + 1U);
    tx->in_flight++;
    tx->stats.sent++;

    tx->write(slot->wire, slot->len, tx->write_ctx);
    return LINK_OK;
}

void link_tx_feed_acks(link_tx_t *tx, const uint8_t *bytes, size_t len) {
    framing_reader_feed(&tx->ack_reader, bytes, len);
}

link_status_t link_tx_tick(link_tx_t *tx, uint32_t now_ms) {
    link_status_t result = LINK_OK;

    for (size_t i = 0; i < LINK_WINDOW; ++i) {
        link_tx_slot_t *slot = &tx->slots[i];
        if (!slot->used) {
            continue;
        }
        // Порівняння через різницю зі знаком переживає обертання лічильника часу.
        if ((int32_t)(now_ms - slot->deadline_ms) < 0) {
            continue;
        }

        if (slot->tries >= LINK_TX_MAX_TRIES) {
            slot->used = false;
            tx->in_flight--;
            tx->stats.lost++;
            result = LINK_ERR_LINK_DOWN;   // далі повторювати немає сенсу: лінія мертва
            continue;
        }

        slot->tries++;
        slot->deadline_ms = now_ms + LINK_TX_TIMEOUT_MS;
        tx->stats.retrans++;
        tx->write(slot->wire, slot->len, tx->write_ctx);
    }

    return result;
}

bool link_tx_idle(const link_tx_t *tx) {
    return tx->in_flight == 0U;
}
