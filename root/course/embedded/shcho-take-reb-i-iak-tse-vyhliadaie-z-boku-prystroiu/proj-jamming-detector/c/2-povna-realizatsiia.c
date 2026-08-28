#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define EW_WINDOW_SIZE          16
#define EW_MAX_GNSS_SATS        12

#define EW_RSSI_JAM_THRESHOLD_DBM     (-65)
#define EW_RSSI_BARRAGE_THRESHOLD_DBM (-40)
#define EW_RSSI_PULSE_VARIANCE_MIN    (120)
#define EW_PER_JAM_THRESHOLD_PCT      (75)
#define EW_GNSS_SPOOF_CNR_THRESHOLD   (510) /* 51.0 дБ-Гц у сотих */
#define EW_GNSS_SPOOF_DEV_MAX         (25)  /* 2.5 дБ-Гц відхилення */

typedef enum {
    EW_THREAT_NONE = 0,
    EW_THREAT_WEAK_SIGNAL,
    EW_THREAT_SPOT_JAMMING,
    EW_THREAT_BARRAGE_BLOCKING,
    EW_THREAT_PULSE_JAMMING,
    EW_THREAT_GNSS_SPOOFING
} ew_threat_type_t;

typedef struct {
    int16_t  rssi_dbm;          /* Рівень вхідного сигналу, дБм */
    int8_t   snr_db;            /* Відношення сигнал/шум, дБ */
    uint8_t  agc_gain_code;     /* Стан підсилення AGC (0 - мін, 255 - макс) */
    bool     preamble_detected; /* Чи була знайдена преамбула/Sync Word */
    bool     crc_error;         /* Чи виявлено помилку контрольної суми */
} ew_rf_sample_t;

typedef struct {
    uint8_t prn;                /* Номер супутника */
    uint16_t cnr_x10;           /* CNR у дБ-Гц помножений на 10 (напр. 425 = 42.5) */
    int16_t  doppler_hz;        /* Доплерівський зсув частоти, Гц */
    uint8_t  elevation_deg;     /* Кут місця над горизонтом, градуси */
} ew_gnss_sat_t;

typedef struct {
    uint8_t sat_count;
    ew_gnss_sat_t sats[EW_MAX_GNSS_SATS];
    bool clock_jump_detected;
    bool pos_jump_without_imu;
} ew_gnss_frame_t;

typedef struct {
    ew_rf_sample_t rf_history[EW_WINDOW_SIZE];
    uint8_t        rf_head;
    uint8_t        rf_count;

    ew_threat_type_t current_threat;
    uint32_t         threat_duration_ms;
} ew_detector_t;

void ew_detector_init(ew_detector_t *det) {
    if (!det) return;
    memset(det, 0, sizeof(ew_detector_t));
    det->current_threat = EW_THREAT_NONE;
}

void ew_detector_push_rf(ew_detector_t *det, const ew_rf_sample_t *sample) {
    if (!det || !sample) return;
    det->rf_history[det->rf_head] = *sample;
    det->rf_head = (det->rf_head + 1) % EW_WINDOW_SIZE;
    if (det->rf_count < EW_WINDOW_SIZE) {
        det->rf_count++;
    }
}

static bool ew_check_gnss_spoofing(const ew_gnss_frame_t *gnss) {
    if (!gnss || gnss->sat_count < 4) return false;

    if (gnss->pos_jump_without_imu || gnss->clock_jump_detected) {
        return true;
    }

    uint32_t cnr_sum = 0;
    uint8_t high_cnr_count = 0;

    for (uint8_t i = 0; i < gnss->sat_count; i++) {
        cnr_sum += gnss->sats[i].cnr_x10;
        if (gnss->sats[i].cnr_x10 >= EW_GNSS_SPOOF_CNR_THRESHOLD) {
            high_cnr_count++;
        }
    }

    uint16_t cnr_avg = (uint16_t)(cnr_sum / gnss->sat_count);

    /* Обчислення середнього абсолютного відхилення рівнів сигналу */
    uint32_t dev_sum = 0;
    for (uint8_t i = 0; i < gnss->sat_count; i++) {
        int32_t diff = (int32_t)gnss->sats[i].cnr_x10 - (int32_t)cnr_avg;
        if (diff < 0) diff = -diff;
        dev_sum += (uint32_t)diff;
    }
    uint16_t cnr_mean_dev = (uint16_t)(dev_sum / gnss->sat_count);

    /* Ознака спуфінгу: понад 70% супутників мають неприродний CNR > 51 дБ-Гц
       і однаковий рівень сигналу від однієї передавальної антени */
    if ((high_cnr_count * 100 / gnss->sat_count) >= 70 && cnr_mean_dev <= EW_GNSS_SPOOF_DEV_MAX) {
        return true;
    }

    return false;
}

ew_threat_type_t ew_detector_evaluate(ew_detector_t *det, const ew_gnss_frame_t *gnss) {
    if (!det || det->rf_count == 0) return EW_THREAT_NONE;

    /* 1. Спершу перевіряємо спуфінг навігації */
    if (ew_check_gnss_spoofing(gnss)) {
        det->current_threat = EW_THREAT_GNSS_SPOOFING;
        return EW_THREAT_GNSS_SPOOFING;
    }

    /* 2. Обчислення статистик радіоканалу */
    int32_t rssi_sum = 0;
    uint32_t agc_sum = 0;
    uint8_t crc_errors = 0;
    uint8_t sync_hits = 0;

    for (uint8_t i = 0; i < det->rf_count; i++) {
        rssi_sum += det->rf_history[i].rssi_dbm;
        agc_sum += det->rf_history[i].agc_gain_code;
        if (det->rf_history[i].crc_error) crc_errors++;
        if (det->rf_history[i].preamble_detected) sync_hits++;
    }

    int16_t avg_rssi = (int16_t)(rssi_sum / det->rf_count);
    uint8_t avg_agc = (uint8_t)(agc_sum / det->rf_count);
    uint8_t per = (uint8_t)((crc_errors * 100) / det->rf_count);

    /* Обчислення дисперсії RSSI для імпульсних завад */
    uint32_t rssi_var_sum = 0;
    for (uint8_t i = 0; i < det->rf_count; i++) {
        int32_t diff = (int32_t)det->rf_history[i].rssi_dbm - (int32_t)avg_rssi;
        rssi_var_sum += (uint32_t)(diff * diff);
    }
    uint32_t rssi_variance = rssi_var_sum / det->rf_count;

    /* 3. Класифікація стану зв'язку */
    if (avg_rssi >= EW_RSSI_BARRAGE_THRESHOLD_DBM && avg_agc <= 30 && sync_hits == 0) {
        det->current_threat = EW_THREAT_BARRAGE_BLOCKING;
    } else if (avg_rssi >= EW_RSSI_JAM_THRESHOLD_DBM && per >= EW_PER_JAM_THRESHOLD_PCT && sync_hits <= 1) {
        det->current_threat = EW_THREAT_SPOT_JAMMING;
    } else if (rssi_variance >= EW_RSSI_PULSE_VARIANCE_MIN && per >= 40) {
        det->current_threat = EW_THREAT_PULSE_JAMMING;
    } else if (avg_rssi <= -105 && per >= EW_PER_JAM_THRESHOLD_PCT) {
        det->current_threat = EW_THREAT_WEAK_SIGNAL;
    } else {
        det->current_threat = EW_THREAT_NONE;
    }

    return det->current_threat;
}
