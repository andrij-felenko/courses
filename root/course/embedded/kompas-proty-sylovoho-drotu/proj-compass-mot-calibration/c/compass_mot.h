/* compass_mot.h - C99 Implementation of Compass-Mot Calibration and In-Flight Engine */
#ifndef COMPASS_MOT_H
#define COMPASS_MOT_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define COMPASS_MOT_MAX_SAMPLES 1024

/* Конфігурація та робочий стан потокового фільтра */
typedef struct {
    float k_x;              /* Коефіцієнт компенсації осі X (мкТл/А) */
    float k_y;              /* Коефіцієнт компенсації осі Y (мкТл/А) */
    float k_z;              /* Коефіцієнт компенсації осі Z (мкТл/А) */
    float current_lpf_alpha;/* Коефіцієнт згладжування фільтра струму */
    float current_filtered; /* Поточний фільтрований струм (А) */
    float max_current_limit;/* Граничний струм для відсікання помилок давача */
    bool  is_enabled;       /* Прапорець активності компенсації */
} compass_mot_t;

/* Структура накопичувача статистики для процедури калібрування OLS */
typedef struct {
    float sum_i;            /* Сума струмів ∑ I */
    float sum_i2;           /* Сума квадратів струмів ∑ I² */
    float sum_bx;           /* Сума відхилень ∑ ΔBx */
    float sum_by;           /* Сума відхилень ∑ ΔBy */
    float sum_bz;           /* Сума відхилень ∑ ΔBz */
    float sum_i_bx;         /* Сума добутків ∑ (I · ΔBx) */
    float sum_i_by;         /* Сума добутків ∑ (I · ΔBy) */
    float sum_i_bz;         /* Сума добутків ∑ (I · ΔBz) */
    uint32_t sample_count;  /* Кількість зібраних вибірок */
    float b_baseline[3];    /* Опорне геомагнітне поле [Bx0, By0, Bz0] */
} compass_mot_calibrator_t;

/**
 * Ініціалізація структури компенсатора
 */
static inline void compass_mot_init(compass_mot_t *cm, float kx, float ky, float kz,
                                    float dt_sec, float cutoff_hz) {
    cm->k_x = kx;
    cm->k_y = ky;
    cm->k_z = kz;
    cm->current_filtered = 0.0f;
    cm->max_current_limit = 250.0f;
    cm->is_enabled = (fabsf(kx) > 1e-5f || fabsf(ky) > 1e-5f || fabsf(kz) > 1e-5f);

    /* Розрахунок коефіцієнта фільтра низьких частот першого порядку */
    float rc = 1.0f / (2.0f * 3.14159265f * cutoff_hz);
    cm->current_lpf_alpha = dt_sec / (rc + dt_sec);
}

/**
 * Старт калібрувального прогону
 */
static inline void compass_mot_calib_start(compass_mot_calibrator_t *cal, const float b_zero[3]) {
    cal->sum_i = 0.0f;
    cal->sum_i2 = 0.0f;
    cal->sum_bx = 0.0f;
    cal->sum_by = 0.0f;
    cal->sum_bz = 0.0f;
    cal->sum_i_bx = 0.0f;
    cal->sum_i_by = 0.0f;
    cal->sum_i_bz = 0.0f;
    cal->sample_count = 0;
    cal->b_baseline[0] = b_zero[0];
    cal->b_baseline[1] = b_zero[1];
    cal->b_baseline[2] = b_zero[2];
}

/**
 * Додавання вимірювання в накопичувач OLS
 */
static inline void compass_mot_calib_feed(compass_mot_calibrator_t *cal,
                                         float current_amps,
                                         const float b_raw[3]) {
    if (cal->sample_count >= COMPASS_MOT_MAX_SAMPLES || current_amps < 0.0f) {
        return;
    }

    float delta_bx = b_raw[0] - cal->b_baseline[0];
    float delta_by = b_raw[1] - cal->b_baseline[1];
    float delta_bz = b_raw[2] - cal->b_baseline[2];

    cal->sum_i    += current_amps;
    cal->sum_i2   += current_amps * current_amps;
    cal->sum_bx   += delta_bx;
    cal->sum_by   += delta_by;
    cal->sum_bz   += delta_bz;
    cal->sum_i_bx += current_amps * delta_bx;
    cal->sum_i_by += current_amps * delta_by;
    cal->sum_i_bz += current_amps * delta_bz;
    cal->sample_count++;
}

/**
 * Завершення калібрування: розрахунок коефіцієнтів OLS та відсотка завади
 */
static inline bool compass_mot_calib_finish(const compass_mot_calibrator_t *cal,
                                            compass_mot_t *cm,
                                            float *interference_pct) {
    if (cal->sample_count < 30) {
        return false;
    }

    float n = (float)cal->sample_count;
    float denom = n * cal->sum_i2 - cal->sum_i * cal->sum_i;
    if (fabsf(denom) < 1e-6f) {
        return false;
    }

    cm->k_x = (n * cal->sum_i_bx - cal->sum_i * cal->sum_bx) / denom;
    cm->k_y = (n * cal->sum_i_by - cal->sum_i * cal->sum_by) / denom;
    cm->k_z = (n * cal->sum_i_bz - cal->sum_i * cal->sum_bz) / denom;
    cm->is_enabled = true;

    /* Розрахунок відносного рівня завади при розрахунковому струмі 100 А */
    float base_norm = sqrtf(cal->b_baseline[0]*cal->b_baseline[0] +
                            cal->b_baseline[1]*cal->b_baseline[1] +
                            cal->b_baseline[2]*cal->b_baseline[2]);
    float comp_norm = sqrtf(cm->k_x*cm->k_x + cm->k_y*cm->k_y + cm->k_z*cm->k_z) * 100.0f;

    if (base_norm > 1.0f) {
        *interference_pct = (comp_norm / base_norm) * 100.0f;
    } else {
        *interference_pct = 0.0f;
    }
    return true;
}

/**
 * Потокова компенсація вимірювання компаса в кожному такті польотного циклу
 */
static inline void compass_mot_apply(compass_mot_t *cm,
                                     float raw_current_amps,
                                     const float b_in[3],
                                     float b_out[3]) {
    if (!cm->is_enabled || raw_current_amps < 0.0f || raw_current_amps > cm->max_current_limit) {
        b_out[0] = b_in[0];
        b_out[1] = b_in[1];
        b_out[2] = b_in[2];
        return;
    }

    /* Фільтрація струму для збігу фази з буфером магнітометра */
    cm->current_filtered += cm->current_lpf_alpha * (raw_current_amps - cm->current_filtered);

    /* Векторне віднімання динамічної завади */
    b_out[0] = b_in[0] - cm->k_x * cm->current_filtered;
    b_out[1] = b_in[1] - cm->k_y * cm->current_filtered;
    b_out[2] = b_in[2] - cm->k_z * cm->current_filtered;
}

#endif /* COMPASS_MOT_H */
