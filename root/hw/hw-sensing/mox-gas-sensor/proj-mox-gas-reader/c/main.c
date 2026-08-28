#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CRC8_POLYNOMIAL 0x31
#define CRC8_INIT       0xFF

/* Перевірка та розрахунок CRC-8 (поліном 0x31, x^8 + x^5 + x^4 + 1) */
uint8_t mox_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = CRC8_INIT;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ CRC8_POLYNOMIAL;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

/* Розрахунок абсолютної вологості в г/м^3 */
float mox_calc_absolute_humidity(float temp_c, float rh_percent) {
    if (rh_percent < 0.0f) rh_percent = 0.0f;
    if (rh_percent > 100.0f) rh_percent = 100.0f;

    /* Формула Магнуса для тиску насиченої водяної пари в гПа */
    float p_sat = 6.112f * expf((17.62f * temp_c) / (243.12f + temp_c));
    float p_vapor = p_sat * (rh_percent / 100.0f);
    float abs_humidity = 216.7f * (p_vapor / (273.15f + temp_c));
    return abs_humidity;
}

typedef struct {
    float r_baseline;       /* Поточна оцінка базової лінії (кОм) */
    float alpha_up;         /* Коефіцієнт швидкої адаптації до чистого повітря */
    float alpha_down;       /* Коефіцієнт повільної деградації базової лінії */
    float k_humidity;       /* Чутливість до абсолютної вологості */
    float ref_humidity;     /* Опорна абсолютна вологість (10.0 г/м3) */
    float voc_gain;         /* Коефіцієнт масштабування логарифмічного відгуку */
    bool  is_warmed_up;     /* Прапорець завершення початкового прогріву */
    uint32_t sample_count;  /* Лічильник оброблених вимірів */
} MoxEngine;

void mox_engine_init(MoxEngine *eng, float initial_baseline_kohm) {
    eng->r_baseline = (initial_baseline_kohm > 1.0f) ? initial_baseline_kohm : 100.0f;
    /* При частоті виклику 1 Гц: */
    eng->alpha_up = 0.001f;      /* tau ~ 1000 секунд (16.6 хв) */
    eng->alpha_down = 0.00002f;  /* tau ~ 50000 секунд (13.8 год) */
    eng->k_humidity = 0.035f;    /* ~3.5% на 1 г/м3 вологи */
    eng->ref_humidity = 10.0f;   /* 25 °C, 50% RH */
    eng->voc_gain = 250.0f;
    eng->is_warmed_up = false;
    eng->sample_count = 0;
}

typedef struct {
    float r_compensated;   /* Опір сенсора з компенсацією вологості (кОм) */
    float r_baseline;      /* Поточний стан базової лінії (кОм) */
    int16_t voc_index;     /* Індекс VOC (0..500, норма = 100) */
    uint16_t eco2_ppm;     /* Розрахунковий eCO2 (400..60000 ppm) */
} MoxResult;

MoxResult mox_engine_process(MoxEngine *eng, float raw_r_kohm, float temp_c, float rh_percent) {
    MoxResult res;
    eng->sample_count++;

    /* Перші 60 секунд сенсор прогрівається */
    if (eng->sample_count > 60) {
        eng->is_warmed_up = true;
    }

    /* 1. Компенсація вологості */
    float ah = mox_calc_absolute_humidity(temp_c, rh_percent);
    float dh = ah - eng->ref_humidity;
    float comp_factor = expf(eng->k_humidity * dh);
    res.r_compensated = raw_r_kohm * comp_factor;

    /* 2. Асиметричний трекер базової лінії */
    if (eng->is_warmed_up) {
        if (res.r_compensated > eng->r_baseline) {
            /* Повітря чистіше за попередній фон: швидке підтягування базової лінії вгору */
            eng->r_baseline += eng->alpha_up * (res.r_compensated - eng->r_baseline);
        } else {
            /* Повітря брудніше (опір впав): надповільне сповзання вниз */
            eng->r_baseline += eng->alpha_down * (res.r_compensated - eng->r_baseline);
        }
    } else {
        /* Під час прогріву просто ініціалізуємо базову лінію */
        eng->r_baseline = res.r_compensated;
    }

    res.r_baseline = eng->r_baseline;

    /* 3. Обчислення логарифмічного VOC Index */
    float ratio = 0.0f;
    if (res.r_compensated > 0.001f && eng->r_baseline > 0.001f) {
        ratio = logf(eng->r_baseline / res.r_compensated);
    }

    float raw_index = 100.0f + eng->voc_gain * ratio;
    if (raw_index < 0.0f) raw_index = 0.0f;
    if (raw_index > 500.0f) raw_index = 500.0f;
    res.voc_index = (int16_t)(raw_index + 0.5f);

    /* 4. Емпіричний розрахунок еквівалентного CO2 (eCO2) */
    if (ratio <= 0.0f) {
        res.eco2_ppm = 400;
    } else {
        float eco2_calc = 400.0f + 1200.0f * powf(ratio, 1.45f);
        if (eco2_calc > 60000.0f) eco2_calc = 60000.0f;
        res.eco2_ppm = (uint16_t)eco2_calc;
    }

    return res;
}
