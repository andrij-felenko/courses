#include <stdint.h>
#include <stdbool.h>

#define LINK_ALPHA_SHIFT     3   /* Коефіцієнт згладжування EMA: 1/(2^3) = 0.125 */
#define LINK_WINDOW_PACKETS  100 /* Розмір вікна для розрахунку PER */

typedef struct {
    int16_t  rssi_ema_q8;       /* RSSI у форматі Q8 (дБм * 256) */
    int16_t  snr_ema_q8;        /* SNR у форматі Q8 (дБ * 256) */
    uint16_t last_seq;          /* Останній прийнятий номер пакета */
    uint32_t total_received;    /* Усього успішно прийнятих пакетів */
    uint32_t total_lost;        /* Усього виявлених втрачених пакетів */
    int16_t  sensitivity_limit; /* Поріг чутливості трансивера (дБм) */
    bool     initialized;
} link_monitor_t;

void link_monitor_init(link_monitor_t *mon, int16_t sensitivity_dbm) {
    mon->rssi_ema_q8 = 0;
    mon->snr_ema_q8 = 0;
    mon->last_seq = 0;
    mon->total_received = 0;
    mon->total_lost = 0;
    mon->sensitivity_limit = sensitivity_dbm;
    mon->initialized = false;
}

void link_monitor_update(link_monitor_t *mon, uint16_t seq, int16_t rssi_dbm, int8_t snr_db) {
    int16_t rssi_in_q8 = rssi_dbm << 8;
    int16_t snr_in_q8 = ((int16_t)snr_db) << 8;

    if (!mon->initialized) {
        mon->rssi_ema_q8 = rssi_in_q8;
        mon->snr_ema_q8 = snr_in_q8;
        mon->last_seq = seq;
        mon->total_received = 1;
        mon->initialized = true;
        return;
    }

    /* Оновлення експоненційного рухомого середнього (EMA) */
    mon->rssi_ema_q8 += (rssi_in_q8 - mon->rssi_ema_q8) >> LINK_ALPHA_SHIFT;
    mon->snr_ema_q8  += (snr_in_q8 - mon->snr_ema_q8) >> LINK_ALPHA_SHIFT;

    /* Розрахунок пропущених пакетів за послідовністю seq */
    uint16_t expected_seq = mon->last_seq + 1;
    if (seq != expected_seq) {
        uint16_t lost = (seq > mon->last_seq) 
                      ? (seq - expected_seq) 
                      : (uint16_t)((0xFFFF - mon->last_seq) + seq);
        mon->total_lost += lost;
    }

    mon->last_seq = seq;
    mon->total_received++;
}

int16_t link_monitor_get_smoothed_rssi(const link_monitor_t *mon) {
    return mon->rssi_ema_q8 >> 8;
}

int16_t link_monitor_get_fade_margin(const link_monitor_t *mon) {
    int16_t current_rssi = mon->rssi_ema_q8 >> 8;
    return current_rssi - mon->sensitivity_limit;
}

float link_monitor_get_per(const link_monitor_t *mon) {
    uint32_t total = mon->total_received + mon->total_lost;
    if (total == 0) return 0.0f;
    return ((float)mon->total_lost / (float)total) * 100.0f;
}
