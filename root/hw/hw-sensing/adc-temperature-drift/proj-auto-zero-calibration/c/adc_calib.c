#include "adc_calib.h"

void adc_calib_init(adc_calib_t *calib, uint32_t max_code, float vref_mv, float t0, float a0, float a1, float a2, float alpha) {
    if (!calib) return;
    
    calib->nominal_max_code = (max_code > 0) ? max_code : 4095;
    calib->nominal_vref_mv = (vref_mv > 0.0f) ? vref_mv : 3300.0f;
    
    calib->raw_zero_code = 0;
    calib->raw_vref_code = (int32_t)calib->nominal_max_code;
    
    calib->temp_t0 = t0;
    calib->poly_a0 = a0;
    calib->poly_a1 = a1;
    calib->poly_a2 = a2;
    
    calib->filtered_temp = t0;
    calib->temp_filter_alpha = (alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.05f;
    calib->temp_initialized = false;
}

void adc_calib_update_references(adc_calib_t *calib, int32_t zero_code, int32_t vref_code) {
    if (!calib) return;
    
    /* Захист від некоректних значень опорної шкали */
    if (vref_code > zero_code) {
        calib->raw_zero_code = zero_code;
        calib->raw_vref_code = vref_code;
    }
}

void adc_calib_update_temperature(adc_calib_t *calib, float raw_temp_degc) {
    if (!calib) return;
    
    if (!calib->temp_initialized) {
        calib->filtered_temp = raw_temp_degc;
        calib->temp_initialized = true;
    } else {
        /* Експоненційний низькочастотний фільтр першого порядку */
        calib->filtered_temp = calib->temp_filter_alpha * raw_temp_degc + (1.0f - calib->temp_filter_alpha) * calib->filtered_temp;
    }
}

float adc_calib_process_sample(const adc_calib_t *calib, int32_t raw_code) {
    if (!calib) return 0.0f;
    
    int32_t span = calib->raw_vref_code - calib->raw_zero_code;
    if (span <= 0) {
        span = (int32_t)calib->nominal_max_code;
    }
    
    /* Крок 1: Двохточкове усунення зміщення нуля та дрейфу масштабу */
    float normalized = (float)(raw_code - calib->raw_zero_code) / (float)span;
    float voltage_mv = normalized * calib->nominal_vref_mv;
    
    /* Крок 2: Поліноміальна термокомпенсація за поточною температурою */
    float dt = calib->filtered_temp - calib->temp_t0;
    float temp_offset_corr = calib->poly_a0 + (calib->poly_a1 * dt) + (calib->poly_a2 * dt * dt);
    
    /* Віднімаємо залишковий апроксимований дрейф */
    voltage_mv -= temp_offset_corr;
    
    return voltage_mv;
}

int32_t adc_calib_correct_code_fixed(const adc_calib_t *calib, int32_t raw_code) {
    if (!calib) return raw_code;
    
    int32_t span = calib->raw_vref_code - calib->raw_zero_code;
    if (span <= 0) return raw_code;
    
    /* Масштабування у форматі з фіксованою комою: (raw - zero) * nominal_max / span */
    int64_t num = ((int64_t)(raw_code - calib->raw_zero_code)) * (int64_t)calib->nominal_max_code;
    int32_t corrected = (int32_t)(num / span);
    
    if (corrected < 0) corrected = 0;
    if ((uint32_t)corrected > calib->nominal_max_code) corrected = (int32_t)calib->nominal_max_code;
    
    return corrected;
}
