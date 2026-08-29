#ifndef LINK_TX_H
#define LINK_TX_H

#include "framing.h"

// Передавач із вікном неквитованих кадрів і повторами за таймаутом (Selective Repeat).
#define LINK_TX_TIMEOUT_MS 40U
#define LINK_TX_MAX_TRIES  12U

typedef struct {
    bool     used;
    uint8_t  seq;
    uint8_t  tries;
    uint32_t deadline_ms;
    size_t   len;
    uint8_t  wire[LINK_MAX_WIRE];   // готові байти — повтор не перекодовує кадр
} link_tx_slot_t;

typedef struct {
    link_tx_slot_t slots[LINK_WINDOW];
    uint8_t        next_seq;
    uint8_t        in_flight;

    link_write_fn    write;
    void            *write_ctx;
    framing_reader_t ack_reader;    // зворотний потік — такі самі кадри

    struct {
        uint32_t sent;       // нових кадрів
        uint32_t retrans;    // повторів за таймаутом
        uint32_t acked;      // квитанцій, що закрили слот
        uint32_t stray_ack;  // квитанція на вже закритий кадр
        uint32_t lost;       // кадрів, на які вичерпано ліміт спроб
    } stats;
} link_tx_t;

void link_tx_init(link_tx_t *tx, link_write_fn write, void *write_ctx);

link_status_t link_tx_submit(link_tx_t *tx, const uint8_t *payload, size_t len, uint32_t now_ms);
void          link_tx_feed_acks(link_tx_t *tx, const uint8_t *bytes, size_t len);
link_status_t link_tx_tick(link_tx_t *tx, uint32_t now_ms);
bool          link_tx_idle(const link_tx_t *tx);

#endif // LINK_TX_H
