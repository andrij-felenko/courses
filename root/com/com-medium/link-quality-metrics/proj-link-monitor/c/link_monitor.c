/* link_monitor.c - Модуль аналізу якості радіоканалу на C */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PER_WINDOW_SIZE  32
#define ALPHA_FP_SHIFT   8   /* Фіксована крапка з масштабом 256 (α = 0.125 -> 32/256) */
#define ALPHA_WEIGHT     32

typedef enum {
    MCS_MODE_BPSK = 0,
    MCS_MODE_QPSK,
    MCS_MODE_QAM16
} mcs_mode_t;

typedef enum {
    LINK_STATUS_CRITICAL = 0,
    LINK_STATUS_FAIR,
    LINK_STATUS_EXCELLENT
} link_status_t;

typedef struct {
    int32_t ema_rssi_fp;     /* RSSI у фіксованій крапці (дБм * 256) */
    int32_t ema_snr_fp;      /* SNR у фіксованій крапці (дБ * 256) */
    uint32_t ema_lqi_fp;     /* LQI у фіксованій крапці (0..255 * 256) */
    
    uint8_t per_window[PER_WINDOW_SIZE];
    uint8_t window_head;
    uint32_t total_packets;
    uint32_t crc_errors;

    mcs_mode_t current_mcs;
    link_status_t status;
} link_monitor_t;

void link_monitor_init(link_monitor_t *mon) {
    if (!mon) return;
    memset(mon, 0, sizeof(link_monitor_t));
    mon->ema_rssi_fp = -100 * 256;  /* Початкове значення -100 дБм */
    mon->ema_snr_fp = 0;
    mon->ema_lqi_fp = 0;
    mon->current_mcs = MCS_MODE_BPSK;
    mon->status = LINK_STATUS_CRITICAL;
}

void link_monitor_update(link_monitor_t *mon, int8_t raw_rssi, int8_t raw_snr, uint8_t raw_lqi, bool crc_ok) {
    if (!mon) return;

    /* 1. Оновлення EMA фільтрів у фіксованій крапці */
    int32_t rssi_target = (int32_t)raw_rssi * 256;
    mon->ema_rssi_fp += ((rssi_target - mon->ema_rssi_fp) * ALPHA_WEIGHT) >> ALPHA_FP_SHIFT;

    int32_t snr_target = (int32_t)raw_snr * 256;
    mon->ema_snr_fp += ((snr_target - mon->ema_snr_fp) * ALPHA_WEIGHT) >> ALPHA_FP_SHIFT;

    uint32_t lqi_target = (uint32_t)raw_lqi * 256;
    mon->ema_lqi_fp += ((lqi_target - mon->ema_lqi_fp) * ALPHA_WEIGHT) >> ALPHA_FP_SHIFT;

    /* 2. Оновлення кільцевого буфера PER */
    uint8_t old_val = mon->per_window[mon->window_head];
    if (old_val == 1) {
        if (mon->crc_errors > 0) mon->crc_errors--;
    }

    uint8_t new_val = crc_ok ? 0 : 1;
    mon->per_window[mon->window_head] = new_val;
    if (new_val == 1) {
        mon->crc_errors++;
    }

    mon->window_head = (mon->window_head + 1) % PER_WINDOW_SIZE;
    if (mon->total_packets < PER_WINDOW_SIZE) {
        mon->total_packets++;
    }

    /* 3. Обчислення поточного PER у відсотках */
    float per_percent = 0.0f;
    if (mon->total_packets > 0) {
        per_percent = ((float)mon->crc_errors / (float)mon->total_packets) * 100.0f;
    }

    float snr_db = (float)mon->ema_snr_fp / 256.0f;
    float lqi_val = (float)mon->ema_lqi_fp / 256.0f;

    /* 4. Автомат станів адаптації MCS з гістерезисом */
    switch (mon->current_mcs) {
        case MCS_MODE_BPSK:
            if (snr_db >= 8.0f && lqi_val >= 120.0f && per_percent < 5.0f) {
                mon->current_mcs = MCS_MODE_QPSK;
            }
            break;

        case MCS_MODE_QPSK:
            if (per_percent > 15.0f || snr_db < 5.0f) {
                mon->current_mcs = MCS_MODE_BPSK;
            } else if (snr_db >= 16.0f && lqi_val >= 200.0f && per_percent < 2.0f) {
                mon->current_mcs = MCS_MODE_QAM16;
            }
            break;

        case MCS_MODE_QAM16:
            if (per_percent > 8.0f || snr_db < 12.0f || lqi_val < 150.0f) {
                mon->current_mcs = MCS_MODE_QPSK;
            }
            break;
    }

    /* 5. Класифікація загального стану каналу */
    if (per_percent > 20.0f || snr_db < 3.0f) {
        mon->status = LINK_STATUS_CRITICAL;
    } else if (per_percent < 3.0f && snr_db >= 12.0f && lqi_val >= 180.0f) {
        mon->status = LINK_STATUS_EXCELLENT;
    } else {
        mon->status = LINK_STATUS_FAIR;
    }
}

int main(void) {
    link_monitor_t monitor;
    link_monitor_init(&monitor);

    /* Імітація серії вимірювань під час прийому пакетів */
    int8_t test_rssi[] = {-85, -83, -80, -78, -75, -74, -75};
    int8_t test_snr[]  = {  4,   6,   9,  11,  14,  15,  16};
    uint8_t test_lqi[] = { 80, 100, 140, 170, 210, 220, 225};
    bool test_crc[]    = {true, true, true, true, true, true, true};

    size_t count = sizeof(test_rssi) / sizeof(test_rssi[0]);
    for (size_t i = 0; i < count; i++) {
        link_monitor_update(&monitor, test_rssi[i], test_snr[i], test_lqi[i], test_crc[i]);
        printf("Крок %zu: RSSI=%.1f dBm, SNR=%.1f dB, LQI=%.1f, MCS=%d, Status=%d\n",
               i + 1,
               (float)monitor.ema_rssi_fp / 256.0f,
               (float)monitor.ema_snr_fp / 256.0f,
               (float)monitor.ema_lqi_fp / 256.0f,
               monitor.current_mcs,
               monitor.status);
    }

    return 0;
}
