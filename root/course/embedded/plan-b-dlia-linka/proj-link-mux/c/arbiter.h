#ifndef ARBITER_H
#define ARBITER_H

#include "link_stats.h"
#include "qos_queue.h"

/* Пороги. Асиметрія навмисна: падаємо на резерв за десятки мілісекунд,
   вертаємось на основний лише після п'яти секунд безперервної тиші в ефірі. */
#define FAILOVER_PER_PCT     25u
#define RECOVERY_PER_PCT     5u
#define PRIMARY_SILENCE_MS   200u
#define FALLBACK_SILENCE_MS  3000u
#define HYSTERESIS_DWELL_MS  5000u
#define SNIFF_PERIOD_MS      500u   /* черговий прийом заглушеного носія */
#define SNIFF_ON_MS          10u

typedef enum {
    BEARER_PRIMARY  = 0,
    BEARER_FALLBACK = 1,
    BEARER_COUNT    = 2
} bearer_id_t;

typedef enum {
    ARB_PRIMARY_OK = 0,
    ARB_FALLBACK_ACTIVE,
    ARB_RECOVERY_EVAL,
    ARB_BLACKOUT
} arbiter_state_t;

typedef enum {
    BEARER_MODE_ACTIVE = 0,   /* підсилювач гріється, приймач слухає */
    BEARER_MODE_LISTEN,       /* підсилювач вимкнено, приймач слухає */
    BEARER_MODE_SLEEP         /* усе вимкнено: пауза чергового прийому */
} bearer_mode_t;

typedef enum {
    ARB_OK               = 0,
    ARB_ERR_BLACKOUT     = -1,
    ARB_ERR_TOO_LARGE    = -2,
    ARB_ERR_NO_BANDWIDTH = -3,
    ARB_ERR_QUEUE_FULL   = -4
} arb_status_t;

/* Контракт драйвера трансивера — усе, чого арбітр потребує від заліза */
typedef struct {
    const char *name;
    int  (*raw_send)(const packet_t *frame, void *ctx);   /* <0 — апаратна помилка */
    void (*set_mode)(bearer_mode_t mode, void *ctx);
    void *ctx;
    uint16_t frame_air_ms;   /* час одного кадру в ефірі */
    uint16_t slot_ms;        /* очікуваний період вхідних кадрів */
} bearer_driver_t;

typedef struct {
    bearer_driver_t drv;
    link_stats_t    stats;
    bearer_mode_t   mode;
    uint32_t        next_free_ms;   /* коли передавач звільниться */
    uint32_t        tx_frames;
    uint32_t        tx_errors;
} bearer_t;

typedef struct {
    arbiter_state_t state;
    bearer_id_t     active;
    uint32_t        state_since_ms;
    uint32_t        sniff_next_ms;
    bool            sniff_open;
    uint16_t        tx_seq;
    uint32_t        switches;
    bearer_t        bearers[BEARER_COUNT];
    tx_queue_t      tx[PRIO_COUNT];
    packet_t        crit_slots[TX_SLOTS_CRITICAL];
    packet_t        tlm_slots[TX_SLOTS_TELEMETRY];
    packet_t        vid_slots[TX_SLOTS_VIDEO];
} link_arbiter_t;

void arbiter_init(link_arbiter_t *a, uint32_t now_ms);
void arbiter_bind(link_arbiter_t *a, bearer_id_t id, const bearer_driver_t *drv,
                  uint32_t now_ms);
void arbiter_on_rx(link_arbiter_t *a, bearer_id_t id, uint16_t seq, int16_t rssi_dbm,
                   int8_t snr_db, uint32_t now_ms);
void arbiter_step(link_arbiter_t *a, uint32_t now_ms);
arb_status_t arbiter_send_packet(link_arbiter_t *a, packet_prio_t prio, const uint8_t *data,
                            uint16_t len, uint32_t now_ms);
uint32_t arbiter_pump(link_arbiter_t *a, uint32_t now_ms);

arbiter_state_t   arbiter_state(const link_arbiter_t *a);
bearer_id_t       arbiter_active(const link_arbiter_t *a);
const bearer_t   *arbiter_bearer(const link_arbiter_t *a, bearer_id_t id);
const tx_queue_t *arbiter_queue(const link_arbiter_t *a, packet_prio_t prio);
uint32_t          arbiter_switches(const link_arbiter_t *a);
const char       *arbiter_state_name(arbiter_state_t st);
const char       *bearer_mode_name(bearer_mode_t mode);

#endif /* ARBITER_H */
