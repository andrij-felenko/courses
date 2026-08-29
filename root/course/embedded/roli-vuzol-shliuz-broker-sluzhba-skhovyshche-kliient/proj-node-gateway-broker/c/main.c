/* main.c — симулятор польового вузла.
 *
 * Роль вузла в системі: міряє, пакує вимір у 16-байтовий кадр, віддає його
 * у канал і виконує команди, що прийшли назад. Ніякої купи: увесь стан —
 * одна структура на стеку, кадри — масиви фіксованої довжини.
 *
 * Запуск:  ./node [node_id] [host] [port]     типово: 42 127.0.0.1 9000
 */
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "frame.h"
#include "link.h"

#define TELEMETRY_PERIOD_MS 2000
#define POLL_SLICE_MS        200
#define RECONNECT_DELAY_MS  1000

typedef struct {
    uint16_t id;
    uint32_t seq;
    bool     relay_on;
    bool     sensor_fault;
    int16_t  temp_c100;     /* сотні градуса */
    uint16_t battery_mv;
} node_state_t;

static volatile sig_atomic_t g_stop = 0;

static void on_sigint(int sig)
{
    (void)sig;
    g_stop = 1;   /* тільки прапорець: у обробнику сигналу друкувати не можна */
}

static void sleep_ms(int ms)
{
    struct timespec ts = { .tv_sec = ms / 1000, .tv_nsec = (long)(ms % 1000) * 1000000L };
    nanosleep(&ts, NULL);
}

static uint64_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000u + (uint64_t)(ts.tv_nsec / 1000000L);
}

/* Замість справжнього АЦП — блукання довкола 22.00 °C і повільний розряд
   батареї. Раз на ~50 вимірів давач «зривається»: саме на це є прапорець збою. */
static void node_sample(node_state_t *st)
{
    st->temp_c100 = (int16_t)(st->temp_c100 + (rand() % 41) - 20);
    if (st->temp_c100 > 3500) st->temp_c100 = 3500;
    if (st->temp_c100 < 1000) st->temp_c100 = 1000;

    if (st->battery_mv > 3000) {
        st->battery_mv = (uint16_t)(st->battery_mv - (rand() % 2));
    }

    st->sensor_fault = (rand() % 50) == 0;
}

static uint8_t node_flags(const node_state_t *st)
{
    uint8_t flags = 0;
    if (st->relay_on)     flags |= FLAG_RELAY_ON;
    if (st->sensor_fault) flags |= FLAG_SENSOR_FAULT;
    return flags;
}

static int node_send_telemetry(node_state_t *st, link_t *lk)
{
    uint8_t frame[FRAME_SIZE];
    st->seq++;
    frame_build_telemetry(frame, st->id, st->seq, st->temp_c100, st->battery_mv, node_flags(st));

    if (link_send_frame(lk, frame) != 0) {
        return -1;
    }
    printf("[node %u] seq=%u  %d.%02d °C  %u мВ  реле=%s\n",
           st->id, st->seq, st->temp_c100 / 100, abs(st->temp_c100 % 100),
           st->battery_mv, st->relay_on ? "увімкнено" : "вимкнено");
    fflush(stdout);
    return 0;
}

/* Прийнятий кадр: чужі й нечитані типи мовчки ігноруємо, на свою команду
   відповідаємо квитанцією — інакше шлюз ніколи не оновить цифрового двійника. */
static int node_handle_frame(node_state_t *st, link_t *lk, const uint8_t frame[FRAME_SIZE])
{
    command_frame_t cmd;
    if (!frame_read_command(frame, &cmd)) {
        return 0;
    }
    if (cmd.head.node_id != st->id) {
        return 0;   /* кадр для сусіда у спільному ефірі */
    }

    uint8_t status = ACK_UNKNOWN_CMD;
    if (cmd.cmd_id == CMD_SET_RELAY) {
        if (cmd.value <= 1) {
            st->relay_on = (cmd.value != 0);
            status = ACK_OK;
            printf("[node %u] команда seq=%u: реле → %s\n",
                   st->id, cmd.head.seq, st->relay_on ? "увімкнено" : "вимкнено");
        } else {
            status = ACK_BAD_VALUE;
            printf("[node %u] команда seq=%u: неприйнятне значення %u\n",
                   st->id, cmd.head.seq, cmd.value);
        }
    } else {
        printf("[node %u] команда seq=%u: невідомий код 0x%02X\n",
               st->id, cmd.head.seq, cmd.cmd_id);
    }
    fflush(stdout);

    uint8_t ack[FRAME_SIZE];
    frame_build_ack(ack, st->id, cmd.head.seq, cmd.cmd_id, status, node_flags(st));
    return link_send_frame(lk, ack);
}

/* Одна сесія зв'язку: живе, поки канал цілий. Повертає -1, коли канал упав. */
static int run_session(node_state_t *st, link_t *lk)
{
    uint64_t next_tx = now_ms();

    while (!g_stop) {
        uint8_t frame[FRAME_SIZE];
        int rc = link_read_frame(lk, frame, POLL_SLICE_MS);
        if (rc < 0) {
            return -1;
        }
        if (rc == 1 && node_handle_frame(st, lk, frame) != 0) {
            return -1;
        }

        if (now_ms() >= next_tx) {
            node_sample(st);
            if (node_send_telemetry(st, lk) != 0) {
                return -1;
            }
            next_tx += TELEMETRY_PERIOD_MS;
        }
    }
    return 0;
}

int main(int argc, char **argv)
{
    node_state_t st = {
        .id = (argc > 1) ? (uint16_t)strtoul(argv[1], NULL, 10) : 42,
        .seq = 0,
        .relay_on = false,
        .sensor_fault = false,
        .temp_c100 = 2200,
        .battery_mv = 3300
    };
    const char *host = (argc > 2) ? argv[2] : "127.0.0.1";
    const char *port = (argc > 3) ? argv[3] : "9000";

    signal(SIGINT, on_sigint);
    srand((unsigned)time(NULL) ^ st.id);

    printf("[node %u] старт, шлюз %s:%s\n", st.id, host, port);

    while (!g_stop) {
        link_t lk;
        if (link_connect(&lk, host, port) != 0) {
            sleep_ms(RECONNECT_DELAY_MS);
            continue;   /* шлюз ще не піднявся — вузол не має права здаватися */
        }
        printf("[node %u] канал відкрито\n", st.id);

        run_session(&st, &lk);

        printf("[node %u] сесію закрито (викинуто байтів на ресинхронізації: %u)\n",
               st.id, lk.resync_drops);
        link_close(&lk);

        if (!g_stop) {
            sleep_ms(RECONNECT_DELAY_MS);
        }
    }

    printf("\n[node %u] зупинка за SIGINT\n", st.id);
    return 0;
}
