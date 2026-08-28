/* link_monitor.h — Оцінка якості радіолінка на мові C для вбудованих систем */
#ifndef LINK_MONITOR_H
#define LINK_MONITOR_H

#include <stdint.h>
#include <stdbool.h>

#define LINK_WINDOW_BITS    100
#define LINK_WORDS_COUNT    ((LINK_WINDOW_BITS + 31) / 32)

typedef enum {
    LINK_STATE_EXCELLENT,  /* LQ >= 90%, SNR стабільний, дані свіжі */
    LINK_STATE_DEGRADED,   /* LQ 70-89% або низький SNR */
    LINK_STATE_CRITICAL,   /* LQ < 70% або Age > 200 мс -> Stage 1 Failsafe */
    LINK_STATE_LOST        /* Age >= 1000 мс -> Stage 2 Повний Failsafe (RTL/Land) */
} link_state_t;

typedef struct {
    int16_t  rssi_dbm;         /* Останній виміряний RSSI (дБм) */
    int8_t   snr_db;           /* Останній виміряний SNR (дБ) */
    uint8_t  lq_percent;       /* Якість лінка 0..100% */
    uint32_t packet_age_ms;    /* Вік останнього валідного пакету в мс */
    link_state_t state;        /* Інтегральний стан каналу */
} link_metrics_t;

typedef struct {
    uint32_t window[LINK_WORDS_COUNT]; /* Бітова маска вікна 100 пакетів */
    uint8_t  head_idx;                 /* Поточна позиція в бітовій масці */
    uint8_t  received_count;           /* Кількість одиниць у масці */
    uint32_t last_packet_time_ms;      /* Час останнього валідного пакету */
    int16_t  last_rssi;
    int8_t   last_snr;
    uint32_t expected_interval_ms;     /* Очікуваний період пакетів (наприклад 10 мс для 100 Гц) */
    uint32_t last_slot_time_ms;        /* Час останньої обробки слота */
} link_monitor_t;

void link_monitor_init(link_monitor_t *mon, uint32_t packet_rate_hz, uint32_t now_ms);
void link_monitor_on_packet_received(link_monitor_t *mon, int16_t rssi, int8_t snr, uint32_t now_ms);
void link_monitor_on_slot_timeout(link_monitor_t *mon, uint32_t now_ms);
void link_monitor_update_time(link_monitor_t *mon, uint32_t now_ms);
link_metrics_t link_monitor_get_metrics(const link_monitor_t *mon, uint32_t now_ms);

#endif /* LINK_MONITOR_H */
