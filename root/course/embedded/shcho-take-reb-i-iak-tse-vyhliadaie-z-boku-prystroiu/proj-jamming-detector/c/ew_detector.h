#ifndef EW_DETECTOR_H
#define EW_DETECTOR_H

#include <stdbool.h>
#include <stdint.h>

/* Ковзне вікно: 16 вибірок ≈ 1.6 с за опитування 10 Гц. */
#define EW_WINDOW_SIZE      16u
/* Поки у вікні менше вибірок — воно ще не прогріте, вердикту не даємо. */
#define EW_WINDOW_MIN_FILL  4u
/* Скільки супутників сузір'я вміщає кадр GNSS. */
#define EW_MAX_GNSS_SATS    12u

typedef enum {
    EW_THREAT_NONE = 0,       /* ефір робочий */
    EW_THREAT_WEAK_SIGNAL,    /* далеко або затінення корпусом: RSSI і SNR просіли РАЗОМ */
    EW_THREAT_SPOT_JAMMING,   /* прицільна завада на нашому каналі */
    EW_THREAT_BARRAGE_BLOCKING, /* загороджувальна: вхідний тракт у насиченні */
    EW_THREAT_PULSE_JAMMING,  /* імпульсна завада */
    EW_THREAT_GNSS_SPOOFING   /* підміна супутникового сигналу */
} ew_threat_t;

/* Одна вибірка телеметрії радіотракту. Усе — цілі числа: модуль мусить
   рахуватися на Cortex-M0+ без FPU. */
typedef struct {
    uint32_t timestamp_ms;      /* час зняття вибірки, мс від старту */
    int16_t  rssi_dbm;          /* рівень ефіру, дБм (напр. -85) */
    int8_t   snr_db;            /* відношення сигнал/шум останнього кадру, дБ */
    uint8_t  agc_gain_code;     /* стан підсилення: 0 - мінімум/атенюатор, 255 - максимум LNA */
    uint8_t  throttle_pct;      /* сумарний газ двигунів 0..100 — для відсіву завад ESC */
    bool     preamble_detected; /* знайдено преамбулу або синхрослово */
    bool     crc_error;         /* кадр прийшов з побитою контрольною сумою */
} ew_rf_sample_t;

typedef struct {
    uint8_t  prn;               /* номер супутника */
    uint16_t cnr_x10;           /* CNR у десятих дБ-Гц (425 = 42.5 дБ-Гц) */
    int16_t  doppler_hz;        /* доплерівський зсув несучої, Гц */
    uint8_t  elevation_deg;     /* кут місця над горизонтом */
} ew_gnss_sat_t;

typedef struct {
    uint8_t       sat_count;
    ew_gnss_sat_t sats[EW_MAX_GNSS_SATS];
    bool          clock_jump_detected;  /* годинник приймача стрибнув */
    bool          pos_jump_without_imu; /* координата поїхала, а ІВП мовчить */
} ew_gnss_frame_t;

/* Зведення по вікну — те, на чому працює матриця правил. Модуль віддає його
   назовні, бо ці ж числа корисно бачити в телеметрії вниз. */
typedef struct {
    uint8_t  samples;
    int16_t  avg_rssi_dbm;
    int8_t   avg_snr_db;
    uint8_t  avg_agc;
    uint8_t  per_pct;        /* частка кадрів із помилкою CRC, % */
    uint8_t  sync_hits;      /* скільки разів знайдено преамбулу/синхрослово */
    uint32_t rssi_variance;  /* дисперсія RSSI, дБ² */
    uint8_t  max_step_db;    /* найбільший стрибок RSSI між СУСІДНІМИ вибірками */
} ew_rf_stats_t;

typedef struct {
    ew_rf_sample_t window[EW_WINDOW_SIZE];
    uint8_t        rf_head;   /* куди ляже наступна вибірка */
    uint8_t        rf_count;  /* скільки вибірок уже є */

    ew_threat_t threat;
    uint32_t    threat_since_ms;
} ew_detector_t;

void ew_detector_init(ew_detector_t *det);

/* Кладе вибірку у кільцевий буфер; найстаріша витісняється. */
void ew_detector_push_rf(ew_detector_t *det, const ew_rf_sample_t *sample);

/* Виносить вердикт. gnss може бути NULL, коли супутникового кадру цього циклу
   немає. now_ms потрібен, щоб рахувати, скільки вердикт уже тримається. */
ew_threat_t ew_detector_evaluate(ew_detector_t *det, const ew_gnss_frame_t *gnss,
                                 uint32_t now_ms);

/* Скільки мілісекунд поточний вердикт тримається без змін. */
uint32_t ew_detector_threat_held_ms(const ew_detector_t *det, uint32_t now_ms);

/* Повертає false, поки вікно не набрало EW_WINDOW_MIN_FILL вибірок. */
bool ew_detector_stats(const ew_detector_t *det, ew_rf_stats_t *out);

const char *ew_threat_name(ew_threat_t threat);

#endif /* EW_DETECTOR_H */
