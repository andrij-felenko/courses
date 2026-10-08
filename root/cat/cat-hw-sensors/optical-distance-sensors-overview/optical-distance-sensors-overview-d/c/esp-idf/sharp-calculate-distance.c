#include <stdio.h>
#include <math.h>
#include "esp_adc/adc_oneshot.h"

// Фізичні константи калібрування сенсора Sharp GP2Y0A21YK0F
#define SHARP_COEFF_KA       16.5f   // Масштабний коефіцієнт (V * cm)
#define SHARP_V_ZERO         0.10f   // Напруга зсуву нуля (Вольт)
#define SHARP_MIN_DIST_CM    10.0f   // Початок робочої зони (см)
#define SHARP_MAX_DIST_CM    80.0f   // Кінець робочої зони (см)
#define SHARP_BLIND_VOLT_TH  2.70f   // Порогова напруга сліпої зони (Вольт)

typedef enum {
    MEASURE_OK = 0,
    MEASURE_ERR_BLIND_ZONE,
    MEASURE_ERR_OUT_OF_RANGE
} distance_status_t;

typedef struct {
    float distance_cm;
    float raw_voltage;
    distance_status_t status;
} distance_result_t;

/**
 * @brief Перерахунок аналогової напруги у фізичну відстань із детектуванням сліпої зони
 */
distance_result_t sharp_calculate_distance(uint32_t adc_raw_mv, float alpha_ema, float *filtered_mv) {
    distance_result_t result;
    
    // Експоненційне згладжування аналогового сигналу (EMA-фільтр)
    *filtered_mv = (alpha_ema * (float)adc_raw_mv) + ((1.0f - alpha_ema) * (*filtered_mv));
    
    float voltage = *filtered_mv / 1000.0f; // Переведення мілівольт у вольти
    result.raw_voltage = voltage;

    // Детектування перевищення максимальної напруги сліпої зони
    if (voltage >= SHARP_BLIND_VOLT_TH) {
        result.distance_cm = SHARP_MIN_DIST_CM;
        result.status = MEASURE_ERR_BLIND_ZONE;
        return result;
    }

    // Гіперболічний перерахунок відстані: x = k_a / (V - V_zero)
    float v_diff = voltage - SHARP_V_ZERO;
    if (v_diff <= 0.05f) {
        result.distance_cm = SHARP_MAX_DIST_CM;
        result.status = MEASURE_ERR_OUT_OF_RANGE;
        return result;
    }

    float dist = SHARP_COEFF_KA / v_diff;

    if (dist < SHARP_MIN_DIST_CM) {
        result.distance_cm = SHARP_MIN_DIST_CM;
        result.status = MEASURE_ERR_BLIND_ZONE;
    } else if (dist > SHARP_MAX_DIST_CM) {
        result.distance_cm = SHARP_MAX_DIST_CM;
        result.status = MEASURE_ERR_OUT_OF_RANGE;
    } else {
        result.distance_cm = dist;
        result.status = MEASURE_OK;
    }

    return result;
}
