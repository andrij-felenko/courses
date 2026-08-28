/* link_monitor.c — Реалізація монітора лінка */
#include "link_monitor.h"

static inline uint8_t count_ones_u32(uint32_t val) {
    return (uint8_t)__builtin_popcount(val);
}

void link_monitor_init(link_monitor_t *mon, uint32_t packet_rate_hz, uint32_t now_ms) {
    for (int i = 0; i < LINK_WORDS_COUNT; ++i) {
        mon->window[i] = 0;
    }
    mon->head_idx = 0;
    mon->received_count = 0;
    mon->last_packet_time_ms = now_ms;
    mon->last_slot_time_ms = now_ms;
    mon->last_rssi = -120;
    mon->last_snr = -20;
    mon->expected_interval_ms = (packet_rate_hz > 0) ? (1000 / packet_rate_hz) : 10;
}

static void push_slot_result(link_monitor_t *mon, bool success) {
    uint8_t word_idx = mon->head_idx / 32;
    uint8_t bit_idx  = mon->head_idx % 32;
    uint32_t mask    = (1UL << bit_idx);

    if (success) {
        mon->window[word_idx] |= mask;
    } else {
        mon->window[word_idx] &= ~mask;
    }

    mon->head_idx++;
    if (mon->head_idx >= LINK_WINDOW_BITS) {
        mon->head_idx = 0;
    }
}

void link_monitor_on_packet_received(link_monitor_t *mon, int16_t rssi, int8_t snr, uint32_t now_ms) {
    mon->last_rssi = rssi;
    mon->last_snr = snr;
    mon->last_packet_time_ms = now_ms;
    mon->last_slot_time_ms = now_ms;
    push_slot_result(mon, true);
}

void link_monitor_on_slot_timeout(link_monitor_t *mon, uint32_t now_ms) {
    mon->last_slot_time_ms = now_ms;
    push_slot_result(mon, false);
}

void link_monitor_update_time(link_monitor_t *mon, uint32_t now_ms) {
    while ((now_ms - mon->last_slot_time_ms) >= mon->expected_interval_ms) {
        mon->last_slot_time_ms += mon->expected_interval_ms;
        push_slot_result(mon, false);
    }
}

link_metrics_t link_monitor_get_metrics(const link_monitor_t *mon, uint32_t now_ms) {
    link_metrics_t m;
    m.rssi_dbm = mon->last_rssi;
    m.snr_db = mon->last_snr;

    uint32_t total = count_ones_u32(mon->window[0]) +
                     count_ones_u32(mon->window[1]) +
                     count_ones_u32(mon->window[2]) +
                     count_ones_u32(mon->window[3] & 0x0000000FU);

    m.lq_percent = (uint8_t)total;
    m.packet_age_ms = (now_ms >= mon->last_packet_time_ms) ? (now_ms - mon->last_packet_time_ms) : 0;

    if (m.packet_age_ms >= 1000) {
        m.state = LINK_STATE_LOST;
    } else if (m.packet_age_ms >= 200 || m.lq_percent < 70) {
        m.state = LINK_STATE_CRITICAL;
    } else if (m.lq_percent < 90 || m.snr_db < 2) {
        m.state = LINK_STATE_DEGRADED;
    } else {
        m.state = LINK_STATE_EXCELLENT;
    }

    return m;
}
