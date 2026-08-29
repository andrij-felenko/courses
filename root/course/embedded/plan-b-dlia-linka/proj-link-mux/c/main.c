/* Прогін диспетчера на моделі польоту: 20 секунд із заглушенням основного
   каналу, провалом резерву й поверненням. Час іде кроком 10 мс — у прошивці
   на цьому місці таймерне переривання й HAL_GetTick(). */
#include "arbiter.h"
#include "link_stats.h"
#include "qos_queue.h"

#include <stdio.h>
#include <string.h>

#define TICK_MS          10u
#define SIM_END_MS       20000u
#define JAM_START_MS     3000u    /* завада по основному каналу */
#define JAM_END_MS       11000u
#define FALL_JAM_START   5500u    /* заглушили ще й резерв */
#define FALL_JAM_END     9500u

static uint32_t g_now_ms;

/* --- Модель ефіру: кадр летить не миттєво, і саме тому кадри міняються
   місцями. Наземна станція розбирає їх ковзним вікном дедуплікації. --- */
#define AIR_SLOTS 64

typedef struct {
    bool        busy;
    uint16_t    seq;
    uint32_t    arrive_ms;
    const char *via;
} air_frame_t;

static air_frame_t    g_air[AIR_SLOTS];
static dedup_window_t g_ground;
static uint32_t       g_ground_ok;
static uint32_t       g_air_lost;

static void air_launch(uint16_t seq, uint32_t arrive_ms, const char *via) {
    for (int i = 0; i < AIR_SLOTS; i++) {
        if (!g_air[i].busy) {
            g_air[i].busy      = true;
            g_air[i].seq       = seq;
            g_air[i].arrive_ms = arrive_ms;
            g_air[i].via       = via;
            return;
        }
    }
    g_air_lost++;
}

static void ground_poll(uint32_t now_ms) {
    for (int i = 0; i < AIR_SLOTS; i++) {
        if (!g_air[i].busy || (int32_t)(now_ms - g_air[i].arrive_ms) < 0) {
            continue;
        }
        g_air[i].busy = false;
        if (dedup_accept(&g_ground, g_air[i].seq)) {
            g_ground_ok++;
        }
    }
}

/* --- Драйвери двох трансиверів --- */
typedef struct {
    const char *label;
    uint16_t    latency_ms;
    bool        faulty;
} radio_ctx_t;

static radio_ctx_t g_wifi = { "2.4G-OFDM", 3u,  false };
static radio_ctx_t g_lora = { "868M-LoRa", 90u, false };

static int radio_send(const packet_t *frame, void *ctx) {
    radio_ctx_t *r = (radio_ctx_t *)ctx;
    if (r->faulty) {
        return -1;   /* SPI не відповів: арбітр порахує помилку й спробує пізніше */
    }
    air_launch(frame->seq, g_now_ms + r->latency_ms, r->label);
    return (int)frame->len;
}

static void radio_set_mode(bearer_mode_t mode, void *ctx) {
    const radio_ctx_t *r = (const radio_ctx_t *)ctx;
    printf("        %-10s -> %s\n", r->label, bearer_mode_name(mode));
}

/* --- Модель радіообстановки --- */
static bool primary_frame_arrives(uint32_t now_ms, int16_t *rssi_dbm) {
    if (now_ms < JAM_START_MS || now_ms >= JAM_END_MS) {
        *rssi_dbm = -62;
        return true;                       /* 100 Гц телеметрії з землі */
    }
    if (now_ms < JAM_START_MS + 200u) {
        *rssi_dbm = -104;                  /* завада наростає: пролазить кожен третій */
        return (now_ms / TICK_MS) % 3u == 0u;
    }
    return false;                          /* повна тиша */
}

static bool fallback_frame_arrives(uint32_t now_ms) {
    if (now_ms % 200u != 0u) {
        return false;                      /* маяк резерву 5 Гц */
    }
    return (now_ms < FALL_JAM_START || now_ms >= FALL_JAM_END);
}

/* Контекст переривання: перекласти кадр у кільце й вийти. Жодної математики. */
static void rx_isr(rx_ring_t *ring, bearer_id_t id, uint16_t seq, int16_t rssi,
                   int8_t snr, uint32_t now_ms) {
    packet_t frame;
    frame.seq      = seq;
    frame.len      = 0;
    frame.stamp_ms = now_ms;
    frame.bearer   = (uint8_t)id;
    frame.prio     = (uint8_t)PRIO_TELEMETRY;
    frame.rssi_dbm = rssi;
    frame.snr_db   = snr;
    (void)rx_ring_push(ring, &frame);   /* переповнення вже пораховане всередині */
}

int main(void) {
    /* Статика: у польоті купи немає — тут теж */
    static link_arbiter_t arbiter;
    static rx_ring_t      rx_ring;
    static uint8_t        telemetry[48];
    static uint8_t        video[200];
    static uint8_t        command[12];

    const bearer_driver_t wifi_drv = { "2.4G-OFDM", radio_send, radio_set_mode, &g_wifi, 3u,  10u };
    const bearer_driver_t lora_drv = { "868M-LoRa", radio_send, radio_set_mode, &g_lora, 90u, 200u };

    memset(telemetry, 0xA5, sizeof(telemetry));
    memset(video, 0x5A, sizeof(video));
    memset(command, 0x3C, sizeof(command));

    rx_ring_init(&rx_ring);
    dedup_init(&g_ground);
    arbiter_init(&arbiter, 0u);
    arbiter_bind(&arbiter, BEARER_PRIMARY,  &wifi_drv, 0u);
    arbiter_bind(&arbiter, BEARER_FALLBACK, &lora_drv, 0u);

    uint16_t prim_seq = 0, fall_seq = 0;
    uint32_t tlm_ok = 0, vid_ok = 0, vid_refused = 0, crit_ok = 0, crit_lost = 0;
    arbiter_state_t last_state = arbiter_state(&arbiter);
    printf("  0.00 с  стан: %s\n", arbiter_state_name(last_state));

    for (g_now_ms = 0; g_now_ms <= SIM_END_MS; g_now_ms += TICK_MS) {
        const uint32_t now = g_now_ms;

        /* 1. Переривання приймачів. Лічильник кадру росте завжди: кадр міг
              вилетіти з землі й не долетіти — саме це й дає розрив у seq. */
        int16_t rssi = 0;
        const uint16_t pseq = prim_seq++;
        if (primary_frame_arrives(now, &rssi)) {
            rx_isr(&rx_ring, BEARER_PRIMARY, pseq, rssi, (rssi < -100) ? -4 : 12, now);
        }
        if (now % 200u == 0u) {
            const uint16_t fseq = fall_seq++;
            if (fallback_frame_arrives(now)) {
                rx_isr(&rx_ring, BEARER_FALLBACK, fseq, -95, 5, now);
            }
        }

        /* 2. Задача арбітра розбирає кільце й рахує метрики */
        packet_t rx;
        while (rx_ring_pop(&rx_ring, &rx)) {
            arbiter_on_rx(&arbiter, (bearer_id_t)rx.bearer, rx.seq, rx.rssi_dbm,
                          rx.snr_db, now);
        }

        /* 3. Автомат станів — кожні 10 мс */
        arbiter_step(&arbiter, now);

        /* 4. Політний контролер віддає свої пакети */
        if (now % 20u == 0u) {
            if (arbiter_send_packet(&arbiter, PRIO_TELEMETRY, telemetry, sizeof(telemetry), now) == ARB_OK) {
                tlm_ok++;
            }
        }
        if (now % 50u == 0u) {
            const arb_status_t rc = arbiter_send_packet(&arbiter, PRIO_VIDEO, video, sizeof(video), now);
            if (rc == ARB_OK) {
                vid_ok++;
            } else if (rc == ARB_ERR_NO_BANDWIDTH) {
                vid_refused++;
            }
        }
        if (now % 1000u == 0u) {
            const arb_status_t rc = arbiter_send_packet(&arbiter, PRIO_CRITICAL, command, sizeof(command), now);
            if (rc == ARB_OK) {
                crit_ok++;
            } else {
                crit_lost++;   /* верхній рівень тут вмикає автономне повернення */
            }
        }

        /* 5. Диспетчер віддає черги в ефір, 6. земля приймає, що долетіло */
        (void)arbiter_pump(&arbiter, now);
        ground_poll(now);

        const arbiter_state_t st = arbiter_state(&arbiter);
        if (st != last_state) {
            const bearer_t *prim = arbiter_bearer(&arbiter, BEARER_PRIMARY);
            printf("%6.2f с  стан: %-22s носій: %-10s PER основного %u%%\n",
                   now / 1000.0, arbiter_state_name(st),
                   arbiter_bearer(&arbiter, arbiter_active(&arbiter))->drv.name,
                   (unsigned)prim->stats.per_percent);
            last_state = st;
        }
    }

    const bearer_t *prim = arbiter_bearer(&arbiter, BEARER_PRIMARY);
    const bearer_t *fall = arbiter_bearer(&arbiter, BEARER_FALLBACK);
    printf("\n== Підсумок 20 с ==\n");
    printf("%-10s кадрів %5u, помилок драйвера %u, PER %u%%, RSSI %d dBm\n",
           prim->drv.name, (unsigned)prim->tx_frames, (unsigned)prim->tx_errors,
           (unsigned)prim->stats.per_percent, link_stats_rssi_dbm(&prim->stats));
    printf("%-10s кадрів %5u, помилок драйвера %u, PER %u%%, RSSI %d dBm\n",
           fall->drv.name, (unsigned)fall->tx_frames, (unsigned)fall->tx_errors,
           (unsigned)fall->stats.per_percent, link_stats_rssi_dbm(&fall->stats));
    printf("телеметрія: узято %u, витіснено старих %u\n",
           (unsigned)tlm_ok, (unsigned)arbiter_queue(&arbiter, PRIO_TELEMETRY)->dropped);
    printf("відео: узято %u, відмовлено на резерві %u, скинуто чергою %u\n",
           (unsigned)vid_ok, (unsigned)vid_refused,
           (unsigned)arbiter_queue(&arbiter, PRIO_VIDEO)->dropped);
    printf("критичні: узято %u, не взято через блекаут %u\n",
           (unsigned)crit_ok, (unsigned)crit_lost);
    printf("земля: прийнято %u, дублікатів %u, спізнілих поза вікном %u\n",
           (unsigned)g_ground_ok, (unsigned)g_ground.duplicates, (unsigned)g_ground.too_old);
    printf("перемикань стану %u, переповнень RX-кільця %u, втрачено в моделі ефіру %u\n",
           (unsigned)arbiter_switches(&arbiter), (unsigned)rx_ring.overruns,
           (unsigned)g_air_lost);
    return 0;
}
