#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_BEARERS             2
#define MAX_PAYLOAD_SIZE        256
#define STATS_WINDOW_SIZE       32
#define HYSTERESIS_DWELL_MS     5000
#define FAILOVER_PER_THRESHOLD  25
#define RECOVERY_PER_THRESHOLD  5

typedef enum {
    BEARER_PRIMARY = 0,
    BEARER_FALLBACK = 1
} bearer_type_t;

typedef enum {
    ARBITER_STATE_PRIMARY_OK = 0,
    ARBITER_STATE_FALLBACK_ACTIVE,
    ARBITER_STATE_EVALUATING_RECOVERY,
    ARBITER_STATE_TOTAL_BLACKOUT
} arbiter_fsm_state_t;

typedef enum {
    PRIO_CRITICAL = 0,
    PRIO_TELEMETRY,
    PRIO_VIDEO
} packet_prio_t;

typedef struct {
    int16_t  rssi_dbm;
    int8_t   snr_db;
    uint32_t last_rx_time_ms;
    uint32_t rx_packet_mask;     /* Бітова маска останніх 32 пакетів */
    uint8_t  smoothed_per;       /* Розрахований PER (0..100%) */
    uint8_t  composite_score;    /* Бал якості (0..100) */
    bool     is_physical_up;
} link_stats_t;

typedef struct {
    bearer_type_t       type;
    const char         *name;
    link_stats_t        stats;
    int (*raw_send)(const uint8_t *data, size_t len);
} bearer_channel_t;

typedef struct {
    arbiter_fsm_state_t state;
    bearer_type_t       active_bearer;
    uint32_t            state_enter_time_ms;
    uint32_t            consecutive_good_primary_pkts;
    bearer_channel_t    bearers[MAX_BEARERS];
} link_arbiter_t;

/* Обчислення кількості одиничних бітів у масці (кількість успішно прийнятих пакетів) */
static inline uint8_t count_received_packets(uint32_t mask) {
    uint8_t count = 0;
    while (mask) {
        count += (mask & 1);
        mask >>= 1;
    }
    return count;
}

/* Оновлення бітової маски втрат при надходженні нового пакета */
void link_stats_on_packet_rx(link_stats_t *stats, uint16_t seq, int16_t rssi, int8_t snr, uint32_t now_ms) {
    stats->last_rx_time_ms = now_ms;
    stats->rssi_dbm = (int16_t)((stats->rssi_dbm * 7 + rssi) >> 3); /* EWMA фільтр */
    stats->snr_db = (int8_t)((stats->snr_db * 7 + snr) >> 3);
    
    stats->rx_packet_mask = (stats->rx_packet_mask << 1) | 1;
    uint8_t received = count_received_packets(stats->rx_packet_mask);
    stats->smoothed_per = (uint8_t)(((STATS_WINDOW_SIZE - received) * 100) / STATS_WINDOW_SIZE);
    
    /* Розрахунок інтегрального балу: PER має найбільшу вагу */
    int score = 100 - stats->smoothed_per;
    if (stats->rssi_dbm < -100) {
        score -= 20;
    }
    stats->composite_score = (uint8_t)(score < 0 ? 0 : (score > 100 ? 100 : score));
}

void link_stats_on_packet_timeout(link_stats_t *stats) {
    stats->rx_packet_mask = (stats->rx_packet_mask << 1); /* Зсув нуля при втраті */
    uint8_t received = count_received_packets(stats->rx_packet_mask);
    stats->smoothed_per = (uint8_t)(((STATS_WINDOW_SIZE - received) * 100) / STATS_WINDOW_SIZE);
    stats->composite_score = (uint8_t)(100 - stats->smoothed_per);
}

void arbiter_init(link_arbiter_t *arbiter) {
    memset(arbiter, 0, sizeof(link_arbiter_t));
    arbiter->state = ARBITER_STATE_PRIMARY_OK;
    arbiter->active_bearer = BEARER_PRIMARY;
    arbiter->bearers[BEARER_PRIMARY].name = "2.4G-OFDM";
    arbiter->bearers[BEARER_PRIMARY].stats.rssi_dbm = -60;
    arbiter->bearers[BEARER_PRIMARY].stats.is_physical_up = true;
    
    arbiter->bearers[BEARER_FALLBACK].name = "868M-LoRa";
    arbiter->bearers[BEARER_FALLBACK].stats.rssi_dbm = -75;
    arbiter->bearers[BEARER_FALLBACK].stats.is_physical_up = true;
}

/* Періодичний автомат станів диспетчера */
void arbiter_step(link_arbiter_t *arbiter, uint32_t now_ms) {
    link_stats_t *prim_stats = &arbiter->bearers[BEARER_PRIMARY].stats;
    link_stats_t *fall_stats = &arbiter->bearers[BEARER_FALLBACK].stats;
    
    bool prim_dead = (now_ms - prim_stats->last_rx_time_ms > 1500) || (prim_stats->smoothed_per >= FAILOVER_PER_THRESHOLD);
    bool fall_dead = (now_ms - fall_stats->last_rx_time_ms > 3000);

    switch (arbiter->state) {
    case ARBITER_STATE_PRIMARY_OK:
        if (prim_dead) {
            arbiter->state = ARBITER_STATE_FALLBACK_ACTIVE;
            arbiter->active_bearer = BEARER_FALLBACK;
            arbiter->state_enter_time_ms = now_ms;
        }
        break;

    case ARBITER_STATE_FALLBACK_ACTIVE:
        if (prim_dead && fall_dead) {
            arbiter->state = ARBITER_STATE_TOTAL_BLACKOUT;
            arbiter->state_enter_time_ms = now_ms;
        } else if (!prim_dead && prim_stats->smoothed_per <= RECOVERY_PER_THRESHOLD) {
            arbiter->state = ARBITER_STATE_EVALUATING_RECOVERY;
            arbiter->state_enter_time_ms = now_ms;
            arbiter->consecutive_good_primary_pkts = 0;
        }
        break;

    case ARBITER_STATE_EVALUATING_RECOVERY:
        if (prim_dead) {
            arbiter->state = ARBITER_STATE_FALLBACK_ACTIVE;
            arbiter->active_bearer = BEARER_FALLBACK;
        } else if (now_ms - arbiter->state_enter_time_ms >= HYSTERESIS_DWELL_MS) {
            /* Успішне проходження гістерезису: повертаємося на основний канал */
            arbiter->state = ARBITER_STATE_PRIMARY_OK;
            arbiter->active_bearer = BEARER_PRIMARY;
        }
        break;

    case ARBITER_STATE_TOTAL_BLACKOUT:
        if (!fall_dead) {
            arbiter->state = ARBITER_STATE_FALLBACK_ACTIVE;
            arbiter->active_bearer = BEARER_FALLBACK;
        } else if (!prim_dead) {
            arbiter->state = ARBITER_STATE_PRIMARY_OK;
            arbiter->active_bearer = BEARER_PRIMARY;
        }
        break;
    }
}

/* Маршрутизація передачі пакета відповідно до QoS та стану */
int arbiter_send_packet(link_arbiter_t *arbiter, packet_prio_t prio, const uint8_t *payload, size_t len) {
    if (arbiter->state == ARBITER_STATE_TOTAL_BLACKOUT) {
        return -1; /* Повний радіоблекаут */
    }

    if (prio == PRIO_VIDEO && arbiter->active_bearer == BEARER_FALLBACK) {
        return 0; /* Скидаємо важкий відеопотік на вузькому резервному каналі */
    }

    bearer_channel_t *ch = &arbiter->bearers[arbiter->active_bearer];
    if (ch->raw_send) {
        return ch->raw_send(payload, len);
    }
    return 0;
}
