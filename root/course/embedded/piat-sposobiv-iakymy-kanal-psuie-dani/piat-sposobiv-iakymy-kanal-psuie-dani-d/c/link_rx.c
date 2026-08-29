#include "link_rx.h"

#include <string.h>

static void rx_send_ack(link_rx_t *rx, uint8_t seq) {
    if (rx->write == NULL) {
        return;
    }
    uint8_t wire[LINK_MAX_WIRE];
    size_t wire_len = 0U;
    // Квитанція — кадр із порожнім навантаженням, номер несе поле seq.
    if (framing_build(seq, NULL, 0U, wire, sizeof(wire), &wire_len) == LINK_OK) {
        rx->write(wire, wire_len, rx->write_ctx);
    }
}

static void rx_deliver(link_rx_t *rx, uint8_t seq, const uint8_t *payload, size_t len) {
    rx->stats.delivered++;
    if (rx->on_payload != NULL) {
        rx->on_payload(seq, payload, len, rx->app_ctx);
    }
}

// Щойно дірка в послідовності закрилася, віддаємо застосунку всю накопичену
// неперервну пачку — строго в порядку зростання номерів.
static void rx_flush(link_rx_t *rx) {
    for (;;) {
        link_rx_slot_t *slot = &rx->slots[rx->expected % LINK_WINDOW];
        if (!slot->used || slot->seq != rx->expected) {
            return;
        }
        rx_deliver(rx, slot->seq, slot->data, slot->len);
        slot->used = false;
        rx->expected = (uint8_t)(rx->expected + 1U);
    }
}

static void rx_on_frame(uint8_t seq, const uint8_t *payload, size_t len, void *ctx) {
    link_rx_t *rx = (link_rx_t *)ctx;

    // ІНВАРІАНТ КВИТУВАННЯ: ACK шлемо на КОЖЕН цілий кадр, зокрема й на дублікат.
    // Інакше передавач довіку повторюватиме те, що ми давно виконали.
    rx_send_ack(rx, seq);

    const uint8_t diff = link_seq_diff(seq, rx->expected);

    if (diff == 0U) {
        rx_deliver(rx, seq, payload, len);
        rx->expected = (uint8_t)(rx->expected + 1U);
        rx_flush(rx);
        return;
    }

    if (diff < LINK_WINDOW) {
        // Кадр випереджає очікуваний: тримаємо його, доки не прийде попередник.
        link_rx_slot_t *slot = &rx->slots[seq % LINK_WINDOW];
        if (slot->used && slot->seq == seq) {
            rx->stats.duplicates++;   // той самий кадр удруге, дані вже лежать у слоті
            return;
        }
        slot->used = true;
        slot->seq = seq;
        slot->len = len;
        if (len > 0U) {
            memcpy(slot->data, payload, len);
        }
        rx->stats.buffered++;
        return;
    }

    if (diff >= 128U) {
        // Номер позаду очікуваного — це повтор уже виконаної команди.
        // Дані відкидаємо, ACK уже надіслано вище.
        rx->stats.duplicates++;
        return;
    }

    // Кадр далеко попереду вікна: у слоті для нього немає місця без ризику
    // переплутати його зі старим номером після обертання лічильника.
    rx->stats.out_of_window++;
}

void link_rx_init(link_rx_t *rx,
                  link_app_fn on_payload, void *app_ctx,
                  link_write_fn write, void *write_ctx) {
    memset(rx, 0, sizeof(*rx));
    rx->on_payload = on_payload;
    rx->app_ctx = app_ctx;
    rx->write = write;
    rx->write_ctx = write_ctx;
    framing_reader_init(&rx->reader, rx_on_frame, rx);
}

void link_rx_feed(link_rx_t *rx, const uint8_t *bytes, size_t len) {
    framing_reader_feed(&rx->reader, bytes, len);
}
