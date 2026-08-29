// Демонстрація: 24 команди на виконавчий вузол крізь канал, який б'є, губить,
// дублює, переставляє й ріже дані. Застосунок мусить побачити рівно 24 команди
// по одному разу й у правильному порядку.
#include <stdio.h>
#include <string.h>

#include "channel.h"
#include "link_rx.h"
#include "link_tx.h"

#define N_COMMANDS    24U
#define TIME_LIMIT_MS 20000U

typedef struct {
    unsigned delivered;
    unsigned expected_index;
    bool     order_broken;
} app_t;

// Виконавчий вузол: кожна команда — крок двигуна. Повторне виконання = аварія.
static void app_execute(uint8_t seq, const uint8_t *payload, size_t len, void *ctx) {
    app_t *app = (app_t *)ctx;
    if (len < 1U) {
        return;
    }

    const unsigned index = payload[0];
    if (index != app->expected_index) {
        app->order_broken = true;
        printf("  АВАРІЯ: застосунок побачив команду #%02u, а чекав #%02u\n",
               index, app->expected_index);
    } else {
        app->expected_index++;
    }

    app->delivered++;
    printf("  виконано seq=%3u  #%02u %.*s\n",
           (unsigned)seq, index, (int)(len - 1U), (const char *)&payload[1]);
}

static void write_to_channel(const uint8_t *bytes, size_t len, void *ctx) {
    channel_send((channel_t *)ctx, bytes, len);
}

static void deliver_to_receiver(const uint8_t *bytes, size_t len, void *ctx) {
    link_rx_feed((link_rx_t *)ctx, bytes, len);
}

static void deliver_to_sender(const uint8_t *bytes, size_t len, void *ctx) {
    link_tx_feed_acks((link_tx_t *)ctx, bytes, len);
}

static void print_channel(const char *name, const channel_t *ch) {
    printf("%s: віддано %u, згинуло %u, побито %u, здубльовано %u, переставлено %u, черга переповнена %u\n",
           name, ch->stats.offered, ch->stats.dropped, ch->stats.corrupted,
           ch->stats.duplicated, ch->stats.reordered, ch->stats.overflow);
}

int main(void) {
    // Шафа автоматики поруч із частотним інвертором: канал поганий в обидва боки.
    const channel_cfg_t forward_cfg = {
        .drop_permille = 150U, .duplicate_permille = 80U,
        .reorder_permille = 120U, .burst_permille = 120U
    };
    const channel_cfg_t back_cfg = {
        .drop_permille = 150U, .duplicate_permille = 0U,
        .reorder_permille = 0U, .burst_permille = 80U
    };

    channel_t forward;
    channel_t backward;
    channel_init(&forward, &forward_cfg, 0x1234ABCDU);
    channel_init(&backward, &back_cfg, 0x0BADC0DEU);

    app_t app = {0};
    link_rx_t rx;
    link_tx_t tx;
    link_rx_init(&rx, app_execute, &app, write_to_channel, &backward);
    link_tx_init(&tx, write_to_channel, &forward);

    unsigned next_cmd = 0U;
    uint32_t now = 0U;
    bool link_down = false;

    while (now < TIME_LIMIT_MS) {
        // Наповнюємо вікно, доки є вільні слоти.
        while (next_cmd < N_COMMANDS) {
            uint8_t cmd[24];
            cmd[0] = (uint8_t)next_cmd;
            const int text_len = snprintf((char *)&cmd[1], sizeof(cmd) - 1U, "STEP +10mm");
            if (text_len < 0) {
                break;
            }
            const link_status_t st = link_tx_submit(&tx, cmd, (size_t)text_len + 1U, now);
            if (st == LINK_ERR_WINDOW_FULL) {
                break;
            }
            if (st != LINK_OK) {
                printf("подача команди не вдалася: %s\n", link_status_str(st));
                break;
            }
            next_cmd++;
        }

        if (link_tx_tick(&tx, now) == LINK_ERR_LINK_DOWN) {
            printf("ліміт повторів вичерпано — вважаємо лінію розірваною\n");
            link_down = true;
            break;
        }

        channel_pump(&forward, deliver_to_receiver, &rx);
        channel_pump(&backward, deliver_to_sender, &tx);

        if (next_cmd == N_COMMANDS && link_tx_idle(&tx) &&
            channel_idle(&forward) && channel_idle(&backward)) {
            break;
        }
        now++;
    }

    printf("\n--- що зробив канал (за %u мс віртуального часу) ---\n", now);
    print_channel("вперед ", &forward);
    print_channel("назад  ", &backward);

    printf("\n--- що побачив приймач ---\n");
    printf("цілих кадрів %u, помилок COBS %u, помилок CRC %u, переповнень %u\n",
           rx.reader.stats.frames, rx.reader.stats.cobs_err,
           rx.reader.stats.crc_err, rx.reader.stats.overflow);
    printf("віддано застосунку %u, дублікатів відкинуто %u, буферизовано %u, поза вікном %u\n",
           rx.stats.delivered, rx.stats.duplicates,
           rx.stats.buffered, rx.stats.out_of_window);

    printf("\n--- що робив передавач ---\n");
    printf("нових кадрів %u, повторів %u, квитанцій %u (з них зайвих %u), втрачено %u\n",
           tx.stats.sent, tx.stats.retrans, tx.stats.acked,
           tx.stats.stray_ack, tx.stats.lost);

    const bool ok = !link_down && !app.order_broken &&
                    app.delivered == N_COMMANDS && app.expected_index == N_COMMANDS;

    printf("\nВЕРДИКТ: %s\n",
           ok ? "усі команди виконано рівно по разу й у правильному порядку"
              : "конвеєр не втримав канал");
    return ok ? 0 : 1;
}
