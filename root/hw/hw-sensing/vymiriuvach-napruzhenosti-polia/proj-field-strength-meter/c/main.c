#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define FIELD_METER_CAL_POINTS_MAX 32
#define FIELD_METER_RMS_WINDOW_SIZE 360  /* 360 вибірок по 1 с = 6 хвилин вікна ICNIRP */
#define WAVE_IMPEDANCE_FREE_SPACE 376.730313f

typedef struct {
    float freq_mhz;
    float af_db;        /* Антенний фактор у дБ(1/м) */
} CalPoint;

typedef struct {
    CalPoint cal_table[FIELD_METER_CAL_POINTS_MAX];
    uint16_t cal_count;
    float ortho_matrix[3][3];    /* Матриця компенсації неортогональності M^-1 */
    float temp_coeff_v_per_c;    /* Температурний дрейф детектора, В/°C */
    float t_cal_celsius;         /* Температура заводського калібрування */
    float v_offset[3];           /* Напруга зміщення нуля каналів, В */
} FieldProbeConfig;

typedef struct {
    float e_x;          /* Напруженість E_x, В/м */
    float e_y;          /* Напруженість E_y, В/м */
    float e_z;          /* Напруженість E_z, В/м */
    float e_total;      /* Повна напруженість E_tot, В/м */
    float s_power_wm2;  /* Густина потоку потужності Пойнтінга, Вт/м² */
    float e_rms_6min;   /* Середньоквадратичне значення за вікно 6 хв, В/м */
    float exposure_pct; /* Відсоток від ліміту безпеки ICNIRP, % */
    bool is_valid;
} FieldMeasurement;

typedef struct {
    FieldProbeConfig config;
    float ring_buffer[FIELD_METER_RMS_WINDOW_SIZE];
    uint16_t ring_head;
    uint16_t ring_count;
    float ring_sum_sq;
} FieldMeterDriver;

void field_meter_init(FieldMeterDriver *meter, const FieldProbeConfig *cfg) {
    if (!meter || !cfg) return;
    meter->config = *cfg;
    meter->ring_head = 0;
    meter->ring_count = 0;
    meter->ring_sum_sq = 0.0f;
    for (int i = 0; i < FIELD_METER_RMS_WINDOW_SIZE; i++) {
        meter->ring_buffer[i] = 0.0f;
    }
}

/* Інтерполяція антенного фактора AF (дБ/м) за робочою частотою */
static float interpolate_af_db(const FieldProbeConfig *cfg, float freq_mhz) {
    if (cfg->cal_count == 0) return 0.0f;
    if (freq_mhz <= cfg->cal_table[0].freq_mhz) return cfg->cal_table[0].af_db;
    if (freq_mhz >= cfg->cal_table[cfg->cal_count - 1].freq_mhz) {
        return cfg->cal_table[cfg->cal_count - 1].af_db;
    }

    for (uint16_t i = 0; i < cfg->cal_count - 1; i++) {
        if (freq_mhz >= cfg->cal_table[i].freq_mhz && freq_mhz <= cfg->cal_table[i + 1].freq_mhz) {
            float f0 = cfg->cal_table[i].freq_mhz;
            float f1 = cfg->cal_table[i + 1].freq_mhz;
            float af0 = cfg->cal_table[i].af_db;
            float af1 = cfg->cal_table[i + 1].af_db;
            float t = (freq_mhz - f0) / (f1 - f0);
            return af0 + t * (af1 - af0);
        }
    }
    return cfg->cal_table[0].af_db;
}

/* Розрахунок гранично допустимого рівня напруженості поля за ICNIRP 2020 (населення) */
static float get_icnirp_general_limit(float freq_mhz) {
    if (freq_mhz < 0.1f) return 614.0f;
    if (freq_mhz <= 1.0f) return 87.0f / (float)sqrt(freq_mhz);
    if (freq_mhz <= 30.0f) return 87.0f / (float)sqrt(freq_mhz);
    if (freq_mhz <= 400.0f) return 28.0f;  /* Зона резонансу людського тіла */
    if (freq_mhz <= 2000.0f) return 1.375f * (float)sqrt(freq_mhz);
    return 61.0f; /* 2 ГГц - 300 ГГц */
}

FieldMeasurement field_meter_process(FieldMeterDriver *meter, 
                                    const float v_raw[3], 
                                    float temp_celsius, 
                                    float target_freq_mhz) {
    FieldMeasurement res = {0};
    if (!meter || !v_raw) return res;

    /* 1. Температурна компенсація та усунення зміщення нуля */
    float temp_delta = temp_celsius - meter->config.t_cal_celsius;
    float v_comp[3];
    for (int i = 0; i < 3; i++) {
        float v_zero_corrected = v_raw[i] - meter->config.v_offset[i];
        v_comp[i] = v_zero_corrected - (temp_delta * meter->config.temp_coeff_v_per_c);
        if (v_comp[i] < 0.0f) v_comp[i] = 0.0f;
    }

    /* 2. Ортогональна корекція: V_ortho = M^-1 * V_comp */
    float v_ortho[3] = {0};
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            v_ortho[r] += meter->config.ortho_matrix[r][c] * v_comp[c];
        }
        if (v_ortho[r] < 0.0f) v_ortho[r] = 0.0f;
    }

    /* 3. Отримання антенного фактора та переведення в лінійний масштаб */
    float af_db = interpolate_af_db(&meter->config, target_freq_mhz);
    float af_linear = (float)pow(10.0, af_db / 20.0);

    /* 4. Розрахунок польових величин */
    res.e_x = v_ortho[0] * af_linear;
    res.e_y = v_ortho[1] * af_linear;
    res.e_z = v_ortho[2] * af_linear;

    float e_sq = res.e_x * res.e_x + res.e_y * res.e_y + res.e_z * res.e_z;
    res.e_total = (float)sqrt(e_sq);
    res.s_power_wm2 = e_sq / WAVE_IMPEDANCE_FREE_SPACE;

    /* 5. Оновлення ковзного кільцевого RMS-буфера */
    if (meter->ring_count == FIELD_METER_RMS_WINDOW_SIZE) {
        meter->ring_sum_sq -= meter->ring_buffer[meter->ring_head];
    } else {
        meter->ring_count++;
    }

    meter->ring_buffer[meter->ring_head] = e_sq;
    meter->ring_sum_sq += e_sq;
    if (meter->ring_sum_sq < 0.0f) meter->ring_sum_sq = 0.0f;

    meter->ring_head = (meter->ring_head + 1) % FIELD_METER_RMS_WINDOW_SIZE;
    res.e_rms_6min = (float)sqrt(meter->ring_sum_sq / (float)meter->ring_count);

    /* 6. Оцінка експозиції за нормами безпеки */
    float limit = get_icnirp_general_limit(target_freq_mhz);
    res.exposure_pct = (res.e_rms_6min / limit) * 100.0f;
    res.is_valid = true;

    return res;
}
