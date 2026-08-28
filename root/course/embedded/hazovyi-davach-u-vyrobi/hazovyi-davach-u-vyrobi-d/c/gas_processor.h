/* gas_processor.h — Інтерфейс аналітичного драйвера газового тракту (C99) */
#ifndef GAS_PROCESSOR_H
#define GAS_PROCESSOR_H

#include <stdint.h>
#include <stdbool.h>

#define GAS_WARMUP_TIME_SEC       30U      /* Час виходу на тепловий режим, с */
#define GAS_ABC_WINDOW_DAYS       7U       /* Вікно аналізу базової лінії ABC */
#define GAS_ABC_HOURS_PER_DAY     24U
#define GAS_ABC_BUCKETS_TOTAL     (GAS_ABC_WINDOW_DAYS * GAS_ABC_HOURS_PER_DAY)
#define GAS_TARGET_BASELINE_PPM   400.0f   /* Еталон чистого атмосферного повітря */
#define GAS_MAX_ABC_STEP_PPM      25.0f    /* Максимальний крок підгонки ABC */

typedef enum {
    GAS_STATE_UNINITIALIZED = 0,
    GAS_STATE_WARMUP        = 1,
    GAS_STATE_READY_VALID   = 2,
    GAS_STATE_CALIBRATION   = 3,
    GAS_STATE_FAULT         = 4
} gas_state_t;

typedef struct {
    float r_ref_clean_air;  /* Опір сенсора у чистому повітрі за нормальних умов, Ом */
    float alpha_temp;       /* Температурний коефіцієнт чутливості (1/K) */
    float beta_humidity;    /* Коефіцієнт абсолютної вологості (м3/г) */
    float abc_offset_ppm;   /* Поточне зміщення базової лінії за ABC, ppm */
    uint16_t crc16;         /* Контрольна сума налаштувань */
} gas_cal_config_t;

typedef struct {
    gas_state_t state;
    gas_cal_config_t config;
    bool abc_enabled;
    uint32_t uptime_sec;
    uint32_t current_hour_samples;
    float current_hour_min_ppm;
    float hourly_min_ppm[GAS_ABC_BUCKETS_TOTAL];
    uint16_t bucket_index;
    bool history_full;
} gas_engine_t;

/* Публічний API */
void gas_engine_init(gas_engine_t *dev, const gas_cal_config_t *cfg, bool enable_abc);
void gas_engine_tick_1hz(gas_engine_t *dev);
bool gas_engine_process(gas_engine_t *dev,
                        float raw_resistance,
                        float temp_c,
                        float rh_percent,
                        float *out_ppm,
                        float *out_comp_res);
void gas_engine_manual_calibrate(gas_engine_t *dev, float target_ppm, float current_raw_res);

#endif /* GAS_PROCESSOR_H */

/* gas_processor.c — Реалізація драйвера з математичним трактом Магнуса та ABC */
#include <math.h>
#include <string.h>

/* Обчислення абсолютної вологості AH (г/м3) за формулою Магнуса-Тетенса */
static float calculate_absolute_humidity(float t_c, float rh_pct)
{
    if (rh_pct < 0.0f) rh_pct = 0.0f;
    if (rh_pct > 100.0f) rh_pct = 100.0f;

    /* P_sat у гПа за Магнусом: 6.112 * exp((17.62 * T) / (243.12 + T)) */
    float p_sat = 6.112f * expf((17.62f * t_c) / (243.12f + t_c));
    float p_v = p_sat * (rh_pct / 100.0f);

    /* AH = 216.7 * P_v / (T + 273.15) */
    return (216.7f * p_v) / (t_c + 273.15f);
}

void gas_engine_init(gas_engine_t *dev, const gas_cal_config_t *cfg, bool enable_abc)
{
    if (!dev) return;
    memset(dev, 0, sizeof(gas_engine_t));

    if (cfg) {
        dev->config = *cfg;
    } else {
        dev->config.r_ref_clean_air = 50000.0f; /* 50 кОм за замовчуванням */
        dev->config.alpha_temp = -0.010f;
        dev->config.beta_humidity = 0.035f;
        dev->config.abc_offset_ppm = 0.0f;
    }

    dev->abc_enabled = enable_abc;
    dev->state = GAS_STATE_WARMUP;
    dev->uptime_sec = 0;
    dev->current_hour_min_ppm = 1e6f;
    dev->current_hour_samples = 0;
    dev->bucket_index = 0;
    dev->history_full = false;

    for (uint32_t i = 0; i < GAS_ABC_BUCKETS_TOTAL; ++i) {
        dev->hourly_min_ppm[i] = 1e6f;
    }
}

void gas_engine_tick_1hz(gas_engine_t *dev)
{
    if (!dev) return;
    dev->uptime_sec++;

    /* Оновлення автомата станів прогріву */
    if (dev->state == GAS_STATE_WARMUP) {
        if (dev->uptime_sec >= GAS_WARMUP_TIME_SEC) {
            dev->state = GAS_STATE_READY_VALID;
        }
    }

    /* Щогодинна ротація бакетів для алгоритму ABC */
    if (dev->uptime_sec % 3600U == 0U && dev->state == GAS_STATE_READY_VALID) {
        if (dev->current_hour_samples > 0) {
            dev->hourly_min_ppm[dev->bucket_index] = dev->current_hour_min_ppm;
            dev->bucket_index++;
            if (dev->bucket_index >= GAS_ABC_BUCKETS_TOTAL) {
                dev->bucket_index = 0;
                dev->history_full = true;
            }
        }
        dev->current_hour_min_ppm = 1e6f;
        dev->current_hour_samples = 0;

        /* Запуск щотижневої корекції ABC */
        if (dev->abc_enabled && dev->history_full && (dev->bucket_index == 0)) {
            float global_min = 1e6f;
            for (uint32_t i = 0; i < GAS_ABC_BUCKETS_TOTAL; ++i) {
                if (dev->hourly_min_ppm[i] < global_min) {
                    global_min = dev->hourly_min_ppm[i];
                }
            }

            /* Валідний діапазон для пошуку чистого атмосферного фону */
            if (global_min > 250.0f && global_min < 1200.0f) {
                float delta = global_min - GAS_TARGET_BASELINE_PPM;
                /* Обмеження кроку корекції для плавності */
                if (delta > GAS_MAX_ABC_STEP_PPM) delta = GAS_MAX_ABC_STEP_PPM;
                if (delta < -GAS_MAX_ABC_STEP_PPM) delta = -GAS_MAX_ABC_STEP_PPM;
                dev->config.abc_offset_ppm += delta;
            }
        }
    }
}

bool gas_engine_process(gas_engine_t *dev,
                        float raw_resistance,
                        float temp_c,
                        float rh_percent,
                        float *out_ppm,
                        float *out_comp_res)
{
    if (!dev || !out_ppm || !out_comp_res) return false;
    if (raw_resistance <= 10.0f) {
        dev->state = GAS_STATE_FAULT;
        return false;
    }

    /* 1. Розрахунок абсолютної вологості AH */
    float ah = calculate_absolute_humidity(temp_c, rh_percent);

    /* 2. Мультиплікативна компенсація T і AH до нормальних умов (25 °C, 10 г/м3) */
    float t_ref = 25.0f;
    float ah_ref = 10.0f;
    float k_env = 1.0f + dev->config.alpha_temp * (temp_c - t_ref)
                       + dev->config.beta_humidity * (ah - ah_ref);
    if (k_env < 0.2f) k_env = 0.2f;

    float r_compensated = raw_resistance * k_env;
    *out_comp_res = r_compensated;

    /* 3. Якщо ще триває прогрів — блокуємо видачу фізичної концентрації */
    if (dev->state != GAS_STATE_READY_VALID) {
        *out_ppm = 0.0f;
        return false;
    }

    /* 4. Степенева характеристика MOX: ppm = A * (Rs/R0)^B */
    float ratio = r_compensated / dev->config.r_ref_clean_air;
    if (ratio < 0.01f) ratio = 0.01f;

    /* Типова експонента для відновлювальних газів (VOC/CO): B ≈ -1.45 */
    float raw_ppm = 400.0f * powf(ratio, -1.45f);

    /* 5. Застосування поправки автокалібрування ABC */
    float final_ppm = raw_ppm - dev->config.abc_offset_ppm;
    if (final_ppm < 1.0f) final_ppm = 1.0f;

    *out_ppm = final_ppm;

    /* Накопичення мінімуму для поточної години */
    if (final_ppm < dev->current_hour_min_ppm) {
        dev->current_hour_min_ppm = final_ppm;
    }
    dev->current_hour_samples++;

    return true;
}

void gas_engine_manual_calibrate(gas_engine_t *dev, float target_ppm, float current_raw_res)
{
    if (!dev || current_raw_res <= 0.0f || target_ppm <= 0.0f) return;
    /* Перерахунок базового опору R0 за відомої еталонної концентрації */
    float ratio_target = powf(target_ppm / 400.0f, 1.0f / -1.45f);
    dev->config.r_ref_clean_air = current_raw_res / ratio_target;
    dev->config.abc_offset_ppm = 0.0f;
}
