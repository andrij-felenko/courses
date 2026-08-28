#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define JAM_MAX_SATELLITES      32
#define JAM_EMA_ALPHA           0.25f
#define JAM_THRESH_WARNING      0.35f
#define JAM_THRESH_CRITICAL     0.70f
#define JAM_THRESH_RECOVERY     0.20f
#define JAM_CRITICAL_PERSIST    3

typedef enum {
    JAM_STATE_CLEAN = 0,
    JAM_STATE_WARNING,
    JAM_STATE_CRITICAL,
    JAM_STATE_RECOVERY
} jam_state_t;

typedef struct {
    uint8_t  gnss_id;
    uint8_t  sv_id;
    uint8_t  cno;           /* dB-Hz */
    int8_t   elevation;     /* градуси (-90..+90) */
    bool     used_in_fix;
} gnss_sat_info_t;

typedef struct {
    uint8_t  block_id;
    uint8_t  flags;         /* jammingState у бітах 0..1 */
    uint8_t  ant_status;
    uint8_t  ant_power;
    uint32_t post_status;
    uint16_t noise_per_ms;
    uint16_t agc_cnt;       /* 0..8191 */
    uint8_t  jam_ind;       /* 0..255 */
    int8_t   ofs_i;
    uint8_t  mag_i;
    int8_t   ofs_q;
    uint8_t  mag_q;
} ubx_mon_rf_block_t;

typedef struct {
    /* Базові калібровані значення чистого етеру */
    uint16_t agc_baseline;
    float    cno_baseline;
    uint8_t  sv_count_baseline;
    bool     is_calibrated;
    uint16_t calib_samples;
    uint32_t agc_accum;
    float    cno_accum;

    /* Поточний стан детектора */
    jam_state_t state;
    float       filtered_score;
    uint8_t     critical_counter;
    uint16_t    recovery_timer_ticks;

    /* Поточні часткові оцінки загроз */
    float s_agc;
    float s_cno;
    float s_jam;
    float s_sv;
} jam_detector_t;

void jam_detector_init(jam_detector_t *det)
{
    if (!det) return;
    memset(det, 0, sizeof(jam_detector_t));
    det->agc_baseline = 7500;
    det->cno_baseline = 42.0f;
    det->sv_count_baseline = 12;
    det->state = JAM_STATE_CLEAN;
}

void jam_detector_calibrate_step(jam_detector_t *det, uint16_t agc_cnt, float mean_cno, uint8_t sv_count)
{
    if (det->is_calibrated) return;

    det->agc_accum += agc_cnt;
    det->cno_accum += mean_cno;
    det->calib_samples++;

    if (det->calib_samples >= 50) { /* 10 секунд за частоти 5 Гц */
        det->agc_baseline = (uint16_t)(det->agc_accum / det->calib_samples);
        det->cno_baseline = det->cno_accum / (float)det->calib_samples;
        det->sv_count_baseline = sv_count;
        det->is_calibrated = true;
    }
}

static float clampf(float val, float min_val, float max_val)
{
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

jam_state_t jam_detector_update(jam_detector_t *det,
                               const ubx_mon_rf_block_t *rf,
                               const gnss_sat_info_t *sats,
                               uint8_t sat_count)
{
    if (!det || !rf) return JAM_STATE_CLEAN;

    /* Розрахунок середнього C/N0 для високих супутників (elevation >= 15 град) */
    float cno_sum = 0.0f;
    uint8_t valid_sats = 0;

    if (sats && sat_count > 0) {
        for (uint8_t i = 0; i < sat_count && i < JAM_MAX_SATELLITES; ++i) {
            if (sats[i].elevation >= 15 && sats[i].cno > 0) {
                cno_sum += (float)sats[i].cno;
                valid_sats++;
            }
        }
    }

    float mean_cno = (valid_sats > 0) ? (cno_sum / (float)valid_sats) : 0.0f;

    /* Якщо базова лінія ще не зафіксована — виконуємо калібрування */
    if (!det->is_calibrated) {
        jam_detector_calibrate_step(det, rf->agc_cnt, mean_cno, valid_sats);
        return JAM_STATE_CLEAN;
    }

    /* 1. Обчислення загрози за падінням AGC */
    float delta_agc = 0.0f;
    if (det->agc_baseline > 0 && rf->agc_cnt < det->agc_baseline) {
        delta_agc = (float)(det->agc_baseline - rf->agc_cnt) / (float)det->agc_baseline;
    }
    det->s_agc = clampf((delta_agc - 0.15f) / (0.60f - 0.15f), 0.0f, 1.0f);

    /* 2. Обчислення загрози за просіданням середнього C/N0 */
    float delta_cno = det->cno_baseline - mean_cno;
    det->s_cno = clampf((delta_cno - 4.0f) / (18.0f - 4.0f), 0.0f, 1.0f);

    /* 3. Обчислення загрози за апаратним показником jamInd */
    det->s_jam = clampf(((float)rf->jam_ind - 40.0f) / (180.0f - 40.0f), 0.0f, 1.0f);

    /* 4. Обчислення загрози за кількістю втрачених супутників */
    float delta_sv = 0.0f;
    if (det->sv_count_baseline > 0 && valid_sats < det->sv_count_baseline) {
        delta_sv = (float)(det->sv_count_baseline - valid_sats) / (float)det->sv_count_baseline;
    }
    det->s_sv = clampf((delta_sv - 0.20f) / (0.70f - 0.20f), 0.0f, 1.0f);

    /* Зважений підсумок */
    float raw_score = 0.35f * det->s_agc +
                      0.30f * det->s_cno +
                      0.25f * det->s_jam +
                      0.10f * det->s_sv;

    /* Експоненційне згладжування */
    det->filtered_score = JAM_EMA_ALPHA * raw_score + (1.0f - JAM_EMA_ALPHA) * det->filtered_score;

    /* Скінченний автомат переходів станів */
    switch (det->state) {
    case JAM_STATE_CLEAN:
        if (det->filtered_score >= JAM_THRESH_WARNING) {
            det->state = JAM_STATE_WARNING;
        }
        break;

    case JAM_STATE_WARNING:
        if (det->filtered_score >= JAM_THRESH_CRITICAL) {
            det->critical_counter++;
            if (det->critical_counter >= JAM_CRITICAL_PERSIST) {
                det->state = JAM_STATE_CRITICAL;
                det->critical_counter = 0;
            }
        } else if (det->filtered_score < JAM_THRESH_RECOVERY) {
            det->state = JAM_STATE_CLEAN;
            det->critical_counter = 0;
        } else {
            det->critical_counter = 0;
        }
        break;

    case JAM_STATE_CRITICAL:
        if (det->filtered_score < 0.40f) {
            det->state = JAM_STATE_RECOVERY;
            det->recovery_timer_ticks = 25; /* 5 секунд затримки валідації при 5 Гц */
        }
        break;

    case JAM_STATE_RECOVERY:
        if (det->filtered_score >= JAM_THRESH_WARNING) {
            det->state = JAM_STATE_CRITICAL;
        } else if (det->recovery_timer_ticks > 0) {
            det->recovery_timer_ticks--;
        } else {
            det->state = JAM_STATE_CLEAN;
        }
        break;
    }

    return det->state;
}
