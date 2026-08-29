#ifndef LINK_RX_H
#define LINK_RX_H

#include "framing.h"

// Стадії 4–5 конвеєра: дедуплікація за порядковим номером, буфер впорядкування
// та диспетчеризація чистого навантаження застосунку.
typedef void (*link_app_fn)(uint8_t seq, const uint8_t *payload, size_t len, void *ctx);

typedef struct {
    bool    used;
    uint8_t seq;
    size_t  len;
    uint8_t data[LINK_MAX_PAYLOAD];
} link_rx_slot_t;

typedef struct {
    framing_reader_t reader;
    link_rx_slot_t   slots[LINK_WINDOW];   // буфер впорядкування, слот = seq % LINK_WINDOW
    uint8_t          expected;             // номер кадру, якого чекаємо

    link_app_fn   on_payload;
    void         *app_ctx;
    link_write_fn write;                   // зворотний канал для квитанцій
    void         *write_ctx;

    struct {
        uint32_t delivered;      // віддано застосунку
        uint32_t duplicates;     // повтори вже виконаних команд
        uint32_t buffered;       // кадрів, що чекали на попередника
        uint32_t out_of_window;  // номер поза приймальним вікном
    } stats;
} link_rx_t;

void link_rx_init(link_rx_t *rx,
                  link_app_fn on_payload, void *app_ctx,
                  link_write_fn write, void *write_ctx);

// Шматок байтового потоку будь-якого розміру: 1 байт, 3 байти, півтора кадру.
void link_rx_feed(link_rx_t *rx, const uint8_t *bytes, size_t len);

#endif // LINK_RX_H
