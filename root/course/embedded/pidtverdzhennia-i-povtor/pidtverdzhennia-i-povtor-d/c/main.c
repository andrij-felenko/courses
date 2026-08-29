/* main.c — демонстрація Stop-and-Wait ARQ на віртуальному каналі.
 *
 * Модель: віртуальний годинник із тіком 1 мс, одностороння затримка,
 * втрати й завади з детермінованим генератором (щоб прогін відтворювався).
 * Вузол A шле команди, вузол B їх приймає й квитує.
 */
#include "arq.h"

#include <stdio.h>
#include <string.h>

#define LINK_SLOTS 8

typedef struct {
    uint8_t  bytes[ARQ_MAX_FRAME];
    size_t   len;
    uint32_t due_ms;
    bool     toward_rx;
    bool     busy;
} link_pkt;

typedef struct {
    link_pkt slots[LINK_SLOTS];
    uint32_t now_ms;
    uint32_t delay_ms;
    uint32_t rng;
    unsigned drop_pct;
    unsigned corrupt_pct;
    arq_tx  *tx;
    arq_rx  *rx;
} link_sim;

/* Кінець лінії: кому саме віддавати те, що записав цей вузол. */
typedef struct {
    link_sim *link;
    bool      toward_rx;
} link_port;

static uint32_t xorshift32(uint32_t *s)
{
    uint32_t x = *s;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *s = x;
    return x;
}

static void link_put(link_sim *l, bool toward_rx, const uint8_t *buf, size_t len)
{
    const char *dir  = toward_rx ? "A→B" : "B→A";
    const unsigned dice = xorshift32(&l->rng) % 100u;

    if (dice < l->drop_pct) {
        printf("[%5u мс] %s  кадр загублено в каналі\n", l->now_ms, dir);
        return;
    }

    for (size_t i = 0; i < LINK_SLOTS; ++i) {
        link_pkt *p = &l->slots[i];
        if (p->busy) {
            continue;
        }
        memcpy(p->bytes, buf, len);
        p->len       = len;
        p->due_ms    = l->now_ms + l->delay_ms;
        p->toward_rx = toward_rx;
        p->busy      = true;

        if (dice < l->drop_pct + l->corrupt_pct) {
            /* Псуємо байт даних, а в короткій квитанції — байт номера. */
            const size_t victim = (len > ARQ_HDR_LEN + ARQ_CRC_LEN) ? ARQ_HDR_LEN : 2u;
            p->bytes[victim] ^= 0x20u;
            printf("[%5u мс] %s  завада перевернула біт у байті %zu\n",
                   l->now_ms, dir, victim);
        }
        return;
    }

    printf("[%5u мс] %s  черга каналу переповнена, кадр відкинуто\n", l->now_ms, dir);
}

static void link_pump(link_sim *l)
{
    for (size_t i = 0; i < LINK_SLOTS; ++i) {
        link_pkt *p = &l->slots[i];
        if (!p->busy || p->due_ms > l->now_ms) {
            continue;
        }
        /* Копія і звільнення слота ДО виклику: обробник кадру сам кладе
           в канал відповідь і зайняв би цей самий слот. */
        const link_pkt pkt = *p;
        p->busy = false;

        if (pkt.toward_rx) {
            arq_rx_on_wire(l->rx, pkt.bytes, pkt.len);
        } else {
            arq_tx_on_wire(l->tx, pkt.bytes, pkt.len, l->now_ms);
        }
    }
}

static void port_write(void *ctx, const uint8_t *buf, size_t len)
{
    link_port *port = (link_port *)ctx;
    link_put(port->link, port->toward_rx, buf, len);
}

/* --- Прикладний рівень вузла A --- */

static const char *const g_commands[] = {
    "ARM MOTORS", "SET SPEED 120", "GET STATUS", "STOP", "DISARM"
};
#define COMMAND_COUNT (sizeof g_commands / sizeof g_commands[0])

typedef struct {
    link_sim *link;
    arq_tx   *tx;
    unsigned  next;
    bool      in_flight;
    bool      link_lost;
} app_state;

static void on_result(void *ctx, bool delivered, uint8_t seq)
{
    app_state *app = (app_state *)ctx;
    if (delivered) {
        printf("[%5u мс] A: seq=%u підтверджено (SRTT=%u мс, RTO=%u мс)\n",
               app->link->now_ms, seq,
               arq_rto_srtt(&app->tx->rto), arq_rto_get(&app->tx->rto));
    } else {
        printf("[%5u мс] A: seq=%u не доставлено за %u спроб — зв'язок втрачено\n",
               app->link->now_ms, seq, (unsigned)ARQ_MAX_RETRIES);
        app->link_lost = true;
    }
    app->in_flight = false;
}

static void on_deliver(void *ctx, const uint8_t *data, uint8_t len)
{
    link_sim *l = (link_sim *)ctx;
    printf("[%5u мс] B: додатку віддано «%.*s»\n", l->now_ms, (int)len, (const char *)data);
}

int main(void)
{
    arq_tx tx;
    arq_rx rx;
    link_sim link;

    memset(&link, 0, sizeof link);
    link.delay_ms    = 8;
    link.rng         = 0x20260829u;
    link.drop_pct    = 20;
    link.corrupt_pct = 15;
    link.tx          = &tx;
    link.rx          = &rx;

    link_port a_port = { &link, true };
    link_port b_port = { &link, false };
    app_state app    = { &link, &tx, 0, false, false };

    arq_tx_init(&tx, port_write, &a_port, on_result, &app);
    arq_rx_init(&rx, port_write, &b_port, on_deliver, &link);

    printf("Stop-and-Wait ARQ: втрати %u%%, спотворення %u%%, затримка %u мс в один бік\n\n",
           link.drop_pct, link.corrupt_pct, link.delay_ms);

    for (link.now_ms = 0; link.now_ms < 20000u; ++link.now_ms) {
        link_pump(&link);
        arq_tx_poll(&tx, link.now_ms);

        if (app.link_lost) {
            break;
        }
        if (!app.in_flight) {
            if (app.next >= COMMAND_COUNT) {
                break; /* усі команди підтверджено */
            }
            if (tx.state == ARQ_TX_IDLE) {
                const char *cmd = g_commands[app.next++];
                printf("[%5u мс] A: команда «%s» → кадр seq=%u\n", link.now_ms, cmd, tx.seq);
                if (arq_tx_send(&tx, (const uint8_t *)cmd, (uint8_t)strlen(cmd), link.now_ms)) {
                    app.in_flight = true;
                } else {
                    app.next--; /* не влізло в кадр — спробуємо ще раз наступним тіком */
                }
            }
        }
    }

    printf("\n--- Підсумок (%u мс модельного часу) ---\n", link.now_ms);
    printf("A: нових кадрів %u, повторів %u, підтверджено %u, відмов %u, сміття %u\n",
           tx.stats.sent, tx.stats.retransmitted, tx.stats.acked, tx.stats.failed, tx.stats.stray);
    printf("B: доставлено %u, дублікатів відсіяно %u, побитих кадрів %u",
           rx.stats.delivered, rx.stats.duplicates, rx.stats.corrupted);
    if (rx.stats.corrupted > 0) {
        printf(" (остання причина: %s)", arq_decode_str(rx.last_error));
    }
    printf("\nПідсумковий RTO %u мс при SRTT %u мс\n",
           arq_rto_get(&tx.rto), arq_rto_srtt(&tx.rto));
    return 0;
}
