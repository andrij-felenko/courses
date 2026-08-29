#define _POSIX_C_SOURCE 200809L

#include "ble_scan.h"
#include "modbus_rtu.h"
#include "mqtt_client.h"
#include "sf_queue.h"

#include <pthread.h>
#include <signal.h>
#include <stdarg.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/* Шлюз між польовим сегментом (RS-485 + BLE) і хмарним брокером MQTT.
 *
 * Три задачі, жодна не чекає на іншу:
 *   poller  — опитує Modbus, тут-таки виконує правило автономії;
 *   ble     — слухає ефір і розбирає рекламні кадри давачів;
 *   uplink  — тримає з'єднання з брокером і спорожняє буфер.
 * Зв'язок між ними — тільки через буфер Store-and-Forward. */

#define MB_DEVICE              "/dev/ttyUSB0"
#define MB_BAUD                19200
#define MB_RESPONSE_TIMEOUT_MS 500
#define MB_SLAVE               1
#define REG_PRESSURE           0x0001   /* два регістри: float32 тиску в барах */
#define COIL_EMERGENCY_DUMP    0x0010   /* котушка аварійного скидання */
#define ALARM_SET_BAR          10.0f
#define ALARM_CLEAR_BAR        9.5f     /* гістерезис: інакше клапан смикався б */
#define POLL_PERIOD_MS         1000

#define HCI_INDEX              0

#define BROKER_HOST            "broker.plant.local"
#define BROKER_PORT            "1883"
#define CLIENT_ID              "gw-unit1"
#define KEEPALIVE_S            30

#define DRAIN_RATE_PER_S       5.0      /* архівні повідомлення за секунду */
#define DRAIN_BURST            10.0
#define BACKOFF_MIN_MS         1000u
#define BACKOFF_MAX_MS         30000u

/* Буфер живе в статичній пам'яті: розміри задано в sf_queue.h часом компіляції. */
static sf_queue_t g_queue;
static modbus_port_t *g_mb;
static volatile sig_atomic_t g_stop;
static atomic_uint g_seq;
static pthread_mutex_t g_log_lock = PTHREAD_MUTEX_INITIALIZER;

static void on_signal(int sig)
{
    (void)sig;
    g_stop = 1;
}

static void sleep_ms(int64_t ms)
{
    if (ms <= 0)
        return;
    struct timespec ts = { ms / 1000, (long)(ms % 1000) * 1000000L };
    nanosleep(&ts, NULL);
}

static int64_t wall_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

/* Три потоки пишуть у той самий stdout — без замка рядки перепліталися б. */
static void log_line(const char *fmt, ...)
{
    char stamp[16];
    time_t t = time(NULL);
    struct tm tm_buf;
    localtime_r(&t, &tm_buf);
    strftime(stamp, sizeof(stamp), "%H:%M:%S", &tm_buf);

    va_list ap;
    va_start(ap, fmt);
    pthread_mutex_lock(&g_log_lock);
    printf("%s ", stamp);
    vprintf(fmt, ap);
    putchar('\n');
    fflush(stdout);
    pthread_mutex_unlock(&g_log_lock);
    va_end(ap);
}

/* Номер послідовності й мітку часу ставить шлюз, а не давач: за розривом у
 * seq сервер бачить, скільки записів згоріло в переповненому буфері. */
static void publish_json(const char *topic, const char *body_fmt, ...)
{
    telemetry_msg_t msg;
    msg.seq = (uint32_t)atomic_fetch_add(&g_seq, 1u) + 1u;
    msg.ts_ms = wall_ms();
    snprintf(msg.topic, sizeof(msg.topic), "%s", topic);

    char body[SF_PAYLOAD_MAX];
    va_list ap;
    va_start(ap, body_fmt);
    vsnprintf(body, sizeof(body), body_fmt, ap);
    va_end(ap);

    snprintf(msg.payload, sizeof(msg.payload), "{\"seq\":%u,\"ts\":%lld,%s}",
             msg.seq, (long long)msg.ts_ms, body);
    sf_publish(&g_queue, &msg);
}

static void *poller_thread(void *arg)
{
    (void)arg;
    bool alarm_latched = false;
    unsigned errors_in_row = 0;

    while (!g_stop) {
        int64_t cycle_start = sf_now_ms();

        uint16_t regs[2];
        mb_status_t st = mb_read_holding(g_mb, MB_SLAVE, REG_PRESSURE, 2, regs);
        if (st != MB_OK) {
            errors_in_row++;
            if (st == MB_ERR_EXCEPTION)
                log_line("[modbus] вузол %u: виняток 0x%02X", MB_SLAVE, mb_last_exception(g_mb));
            else
                log_line("[modbus] вузол %u: %s (підряд %u)", MB_SLAVE, mb_strerror(st), errors_in_row);
            /* Про смерть шини сервер має дізнатися окремим повідомленням —
             * мовчання телеметрії він міг би списати на обрив WAN. */
            if (errors_in_row == 3)
                publish_json("plant/unit1/status/fieldbus",
                             "\"link\":\"down\",\"slave\":%u,\"why\":\"%s\"",
                             MB_SLAVE, mb_strerror(st));
            sleep_ms(POLL_PERIOD_MS - (sf_now_ms() - cycle_start));
            continue;
        }

        if (errors_in_row >= 3)
            publish_json("plant/unit1/status/fieldbus", "\"link\":\"up\",\"slave\":%u", MB_SLAVE);
        errors_in_row = 0;

        float bar = mb_regs_to_float(regs);

        /* Межа автономії проходить саме тут. Дорога до хмари й назад коштує
         * секунд і може взагалі не відбутися, а клапан треба відкрити зараз. */
        if (!alarm_latched && bar > ALARM_SET_BAR) {
            mb_status_t w = mb_write_coil(g_mb, MB_SLAVE, COIL_EMERGENCY_DUMP, true);
            if (w == MB_OK) {
                alarm_latched = true;
                log_line("[автономія] тиск %.2f бар > %.1f — котушку 0x%04X увімкнено",
                         bar, ALARM_SET_BAR, COIL_EMERGENCY_DUMP);
                publish_json("plant/unit1/event/alarm",
                             "\"rule\":\"pressure_high\",\"p_bar\":%.2f,\"action\":\"dump_on\"", bar);
            } else {
                /* Засувка не спрацювала — засувка й лишається метою: латч не
                 * ставимо, наступний такт спробує знову. */
                log_line("[автономія] СКИДАННЯ НЕ ПРОЙШЛО (%s) — повтор наступним тактом",
                         mb_strerror(w));
                publish_json("plant/unit1/event/alarm",
                             "\"rule\":\"pressure_high\",\"p_bar\":%.2f,\"action\":\"dump_failed\"", bar);
            }
        } else if (alarm_latched && bar < ALARM_CLEAR_BAR) {
            if (mb_write_coil(g_mb, MB_SLAVE, COIL_EMERGENCY_DUMP, false) == MB_OK) {
                alarm_latched = false;
                log_line("[автономія] тиск %.2f бар — аварію знято, котушку вимкнено", bar);
                publish_json("plant/unit1/event/alarm",
                             "\"rule\":\"pressure_high\",\"p_bar\":%.2f,\"action\":\"dump_off\"", bar);
            }
        }

        publish_json("plant/unit1/telemetry/pressure",
                     "\"dev\":\"boiler_1\",\"p_bar\":%.2f,\"alarm\":%s",
                     bar, alarm_latched ? "true" : "false");

        sleep_ms(POLL_PERIOD_MS - (sf_now_ms() - cycle_start));
    }
    return NULL;
}

static void *ble_thread(void *arg)
{
    (void)arg;

    ble_scanner_t *scanner = ble_open(HCI_INDEX);
    if (!scanner) {
        /* Радіо не піднялося — це привід працювати без нього, а не падати:
         * дротова шина й аварійне правило від BLE не залежать. */
        log_line("[ble] сканер hci%d не піднявся — шлюз працює лише по шині", HCI_INDEX);
        return NULL;
    }
    log_line("[ble] пасивне сканування hci%d увімкнено", HCI_INDEX);

    while (!g_stop) {
        ble_sample_t s;
        int r = ble_next_sample(scanner, &s, 500);
        if (r < 0) {
            log_line("[ble] сокет HCI помер — сканування зупинено");
            break;
        }
        if (r == 0)
            continue;

        /* Адреса в HCI лежить молодшим байтом уперед — друкуємо у звичному порядку. */
        publish_json("plant/unit1/telemetry/temperature",
                     "\"dev\":\"%02X:%02X:%02X:%02X:%02X:%02X\",\"t_c\":%.2f,"
                     "\"batt\":%u,\"rssi\":%d",
                     s.addr[5], s.addr[4], s.addr[3], s.addr[2], s.addr[1], s.addr[0],
                     s.temperature_c, s.battery_pct, s.rssi_dbm);
    }

    ble_close(scanner);
    return NULL;
}

static void *uplink_thread(void *arg)
{
    (void)arg;
    unsigned backoff_ms = BACKOFF_MIN_MS;
    unsigned seed = (unsigned)time(NULL);

    while (!g_stop) {
        mqtt_client_t *client = mqtt_connect(BROKER_HOST, BROKER_PORT, CLIENT_ID, KEEPALIVE_S);
        if (!client) {
            size_t fresh = 0, backlog = 0;
            uint32_t dropped = 0;
            sf_stats(&g_queue, &fresh, &backlog, &dropped);

            /* Джитер обов'язковий: після падіння базової станції сотні шлюзів
             * прокидаються разом, і рівний відступ звів би їх в один залп. */
            unsigned wait = backoff_ms / 2 + (unsigned)(rand_r(&seed) % (backoff_ms + 1));
            log_line("[wan] брокер недосяжний; повтор через %u мс; у буфері %zu+%zu, втрачено %u",
                     wait, fresh, backlog, dropped);
            sleep_ms(wait);
            backoff_ms = (backoff_ms * 2 > BACKOFF_MAX_MS) ? BACKOFF_MAX_MS : backoff_ms * 2;
            continue;
        }

        backoff_ms = BACKOFF_MIN_MS;
        log_line("[wan] з'єднання з брокером піднято");

        double tokens = DRAIN_BURST;
        int64_t last_fill = sf_now_ms();

        while (!g_stop) {
            if (mqtt_keepalive(client) < 0) {
                log_line("[wan] брокер не відповів на PINGREQ — канал вважаємо мертвим");
                break;
            }

            int64_t now = sf_now_ms();
            tokens += (double)(now - last_fill) / 1000.0 * DRAIN_RATE_PER_S;
            if (tokens > DRAIN_BURST)
                tokens = DRAIN_BURST;
            last_fill = now;

            telemetry_msg_t msg;
            bool from_backlog = false;
            if (!sf_peek(&g_queue, &msg, &from_backlog, 200))
                continue;

            /* Свіже йде без обмежень, архів — лише за наявності токена: інакше
             * викачування триденної історії з'їло б увесь канал, і щойно зняті
             * показники чекали б за спиною в ста тисяч старих записів. */
            if (from_backlog && tokens < 1.0) {
                sleep_ms(50);
                continue;
            }

            if (mqtt_publish_qos1(client, msg.topic, msg.payload) != 0) {
                /* Не комітимо: повідомлення лишається в черзі й піде після
                 * перепідключення. Брокер може отримати дублікат — це
                 * нормальна ціна доставки «щонайменше раз». */
                log_line("[wan] публікація seq=%u не підтверджена — перепідключення", msg.seq);
                break;
            }
            sf_commit(&g_queue, from_backlog, msg.seq);
            if (from_backlog)
                tokens -= 1.0;
        }

        mqtt_disconnect(client);
    }
    return NULL;
}

int main(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = on_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
    /* Запис у мертвий сокет не повинен убивати шлюз — помилку поверне write(). */
    signal(SIGPIPE, SIG_IGN);

    sf_init(&g_queue);

    g_mb = mb_open(MB_DEVICE, MB_BAUD, MB_RESPONSE_TIMEOUT_MS);
    if (!g_mb) {
        perror("mb_open");
        sf_destroy(&g_queue);
        return 1;
    }

    log_line("=== шлюз піднято: %s @ %d, брокер %s:%s ===",
             MB_DEVICE, MB_BAUD, BROKER_HOST, BROKER_PORT);

    pthread_t poller, ble, uplink;
    pthread_create(&poller, NULL, poller_thread, NULL);
    pthread_create(&ble, NULL, ble_thread, NULL);
    pthread_create(&uplink, NULL, uplink_thread, NULL);

    while (!g_stop) {
        sleep_ms(5000);
        size_t fresh = 0, backlog = 0;
        uint32_t dropped = 0;
        sf_stats(&g_queue, &fresh, &backlog, &dropped);
        log_line("[буфер] свіжих %zu, архівних %zu, втрачено назавжди %u",
                 fresh, backlog, dropped);
    }

    log_line("зупинка за сигналом…");
    pthread_join(poller, NULL);
    pthread_join(ble, NULL);
    pthread_join(uplink, NULL);

    mb_close(g_mb);
    sf_destroy(&g_queue);
    log_line("=== шлюз зупинено ===");
    return 0;
}
